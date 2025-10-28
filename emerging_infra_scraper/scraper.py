
import os
import re
import csv
import time
import json
import yaml
import random
import logging
import datetime as dt
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

# Optional: RSS support (pip install feedparser)
try:
    import feedparser  # type: ignore
    HAS_FEEDPARSER = True
except Exception:
    HAS_FEEDPARSER = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def polite_get(url: str, sleep: float = 1.5) -> Optional[requests.Response]:
    """Simple polite GET with a small delay. Add retries / proxy rotation as needed."""
    time.sleep(sleep + random.random())
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp
        logging.warning(f"Non-200 ({resp.status_code}) at {url}")
        return None
    except Exception as e:
        logging.error(f"GET error at {url}: {e}")
        return None

def textnorm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def extract_links_from_html(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            links.append(href)
        elif href.startswith("/"):
            parsed = urlparse(base_url)
            links.append(f"{parsed.scheme}://{parsed.netloc}{href}")
    # dedupe preserving order
    seen = set()
    deduped = []
    for l in links:
        if l not in seen:
            seen.add(l)
            deduped.append(l)
    return deduped

def parse_generic_article(url: str, html: str) -> Dict[str, Any]:
    """Generic parser that tries to extract title, date-ish text, and a summary."""
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("h1") or soup.find("title")
    title_text = textnorm(title_el.get_text()) if title_el else ""

    date_text = ""
    for selector in ["time", ".date", ".posted-on", ".entry-date", ".post-date"]:
        el = soup.select_one(selector)
        if el and el.get_text(strip=True):
            date_text = textnorm(el.get_text())
            break

    p = soup.find("p")
    summary = textnorm(p.get_text()) if p else ""

    return {"title": title_text, "date_text": date_text, "summary": summary}

def crawl_portal(name: str, url: str) -> List[Dict[str, Any]]:
    """Fetch a portal page and extract a list of likely project/news links + parse each."""
    out = []
    resp = polite_get(url)
    if not resp:
        return out
    links = extract_links_from_html(resp.text, url)

    base = urlparse(url).netloc
    same_domain = [l for l in links if urlparse(l).netloc == base]

    candidates = [l for l in same_domain if any(x in l.lower() for x in ["project", "road", "bridge", "rail", "port", "expressway", "highway"])]
    candidates = candidates[:20]

    for link in candidates:
        sub = polite_get(link, sleep=0.7)
        if not sub:
            continue
        parsed = parse_generic_article(link, sub.text)
        if parsed.get("title"):
            out.append({
                "source_portal": name,
                "url": link,
                **parsed
            })
    return out

def crawl_feed(name: str, url: str) -> List[Dict[str, Any]]:
    """Attempt to parse a feed via feedparser; fallback to HTML search results if not RSS."""
    items = []
    if HAS_FEEDPARSER:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:20]:
                items.append({
                    "source_feed": name,
                    "url": e.get("link", ""),
                    "title": textnorm(e.get("title", "")),
                    "date_text": textnorm(e.get("published", "") or e.get("updated", "")),
                    "summary": textnorm(e.get("summary", "")),
                })
            if items:
                return items
        except Exception as e:
            logging.warning(f"Feedparser failed for {url}: {e}")

    resp = polite_get(url)
    if not resp:
        return items
    links = extract_links_from_html(resp.text, url)
    candidates = [l for l in links if any(token in l.lower() for token in ["news", "story", "article", "infrastructure", "project"])]
    candidates = candidates[:20]
    for link in candidates:
        sub = polite_get(link, sleep=0.5)
        if not sub:
            continue
        parsed = parse_generic_article(link, sub.text)
        if parsed.get("title"):
            items.append({
                "source_feed": name,
                "url": link,
                **parsed
            })
    return items

def load_seeds(path: str) -> Dict[str, Any]:
    import yaml
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_csv(rows: List[Dict[str, Any]], path: str) -> None:
    if not rows:
        logging.info("No rows to save.")
        return
    keys = sorted({k for r in rows for k in r.keys()})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def suggest_titles(rows: List[Dict[str, Any]], country: str) -> List[str]:
    titles = []
    for r in rows[:30]:
        title = r.get("title", "")
        if not title:
            continue
        base = textnorm(title)
        patterns = [
            f"How {country} Is Building: {base}",
            f"{country}'s Next Big Project: {base} Explained",
            f"Why This Project Matters: {base} ({country})",
            f"The Future of {country}: {base}",
            f"{base} — What It Means for {country}'s Economy",
        ]
        titles.extend(patterns[:2])
    deduped = list(dict.fromkeys(titles))
    return deduped[:20]

def run(config_path: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    seeds = load_seeds(config_path)
    master_rows = []
    title_bank = []

    for country, bundle in seeds["countries"].items():
        logging.info(f"=== {country} ===")
        portals = bundle.get("portals", [])
        feeds = bundle.get("feeds", [])

        for p in portals:
            name, url = p["name"], p["url"]
            logging.info(f"Portal: {name} -> {url}")
            rows = crawl_portal(name, url)
            for r in rows:
                r["country"] = country
                master_rows.append(r)

        for fdef in feeds:
            name, url = fdef["name"], fdef["url"]
            logging.info(f"Feed/Search: {name} -> {url}")
            rows = crawl_feed(name, url)
            for r in rows:
                r["country"] = country
                master_rows.append(r)

        country_rows = [r for r in master_rows if r.get("country") == country]
        title_bank.extend(suggest_titles(country_rows, country))

    ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(out_dir, f"scraped_{ts}.csv")
    save_csv(master_rows, csv_path)

    with open(os.path.join(out_dir, f"titles_{ts}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(title_bank))

    print(f"Saved {len(master_rows)} rows to: {csv_path}")
    print(f"Saved {len(title_bank)} title ideas to: {os.path.join(out_dir, f'titles_{ts}.txt')}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="seeds.yaml", help="Path to seeds.yaml")
    ap.add_argument("--out", default="out", help="Output directory")
    args = ap.parse_args()
    run(args.config, args.out)
