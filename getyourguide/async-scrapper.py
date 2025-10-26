import argparse
import json
import csv
import sys
import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- Config ---
DEFAULT_URL = "https://www.getyourguide.com/london-l57/"
MAX_WORKERS = 5  # adjust based on your system/network
BLOCKED_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".css", ".woff", ".woff2", ".ttf", ".webp")
BLOCKED_DOMAINS = [
    "googletagmanager", "google-analytics", "doubleclick",
    "facebook", "twitter", "linkedin", "scorecardresearch",
    "quantserve", "adsystem", "pubmatic", "criteo", "taboola",
    "outbrain", "adsrvr"
]

def should_block(url: str) -> bool:
    if url.lower().endswith(BLOCKED_EXT):
        return True
    return any(d in url.lower() for d in BLOCKED_DOMAINS)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def safe_text(element):
    return element.get_text(strip=True) if element else None

def parse_detail_html(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")
    data = {
        "title": safe_text(soup.select_one("#adp-title-text span")),
        "rating": safe_text(soup.select_one(".c-activity-rating__rating")),
        "reviews": safe_text(soup.select_one(".simple-activity-rating--reviews-count span")),
        "provider": safe_text(soup.select_one("#activity-provider-description-title span")),
        "price": safe_text(soup.select_one("div.price-info__actual-price-explanation")),
        "description": safe_text(soup.select_one("#short-description-adp-text span")),
        "itinerary": [item.get_text(" ", strip=True) for item in soup.select(".activity-itinerary-timeline li")],
    }

    about = []
    for block in soup.select(".key-detail-item-block"):
        title_el = block.select_one("dt span.text-atom--body-strong")
        desc_el = block.select_one("dd span.text-atom--caption")
        if title_el and desc_el:
            about.append({"title": safe_text(title_el), "details": safe_text(desc_el)})
    data["about"] = about

    hl_div = soup.select_one("div#row-highlights-point-header-content")
    highlights = []
    if hl_div:
        highlight_items = hl_div.select("div#highlights-point ul li span.text-atom--body")
        highlights = [safe_text(item) for item in highlight_items if safe_text(item)]
    data["highlights"] = highlights

    inc_div = soup.select_one("div#row-inclusions-header-content")
    includes, not_included = [], []
    if inc_div:
        include_blocks = inc_div.select('span[id^="inclusion-"][id$="-title"]')
        includes = [safe_text(div) for div in include_blocks if safe_text(div)]
        exclusion_blocks = inc_div.select('span[id^="exclusion-"][id$="-title"]')
        not_included = [safe_text(div) for div in exclusion_blocks if safe_text(div)]
    data["includes"] = includes
    data["not_included"] = not_included

    ns_div = soup.select_one("div#row-not-suitable-for-header-content")
    not_suitable_for = []
    if ns_div:
        li_items = ns_div.select("#not-suitable-for-point ul li")
        not_suitable_for = [li.get_text(strip=True) for li in li_items]
    data["not_suitable_for"] = not_suitable_for

    mp_div = soup.select_one("div#row-meeting-points-header-content")
    meeting_point, meeting_point_link = None, None
    if mp_div:
        span = mp_div.select_one("#meeting-point-links span.text-atom--body")
        meeting_point = safe_text(span)
        link_tag = mp_div.select_one("#meeting-point-links a[href]")
        if link_tag:
            meeting_point_link = link_tag["href"]
    data["meeting_point"] = meeting_point
    data["meeting_point_link"] = meeting_point_link

    return data

def flatten_list_fields(record):
    for k, v in record.items():
        if isinstance(v, list):
            if v and isinstance(v[0], dict):
                record[k] = "; ".join(f"{d.get('title', '')}: {d.get('details', '')}" for d in v)
            else:
                record[k] = "; ".join(str(i) for i in v)
        elif isinstance(v, dict):
            record[k] = json.dumps(v, ensure_ascii=False)
    return record

def extract_all_article_hrefs_from_listing(url: str, timeout_ms: int = 30000) -> List[str]:
    logging.info(f"Extracting article links from listing: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.route("**/*", lambda route, request: route.abort() if should_block(request.url) else route.continue_())
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_selector("article a[href]", timeout=15000)
        except Exception:
            page.wait_for_load_state("networkidle", timeout=10000)

        hrefs = []
        for art in page.query_selector_all("article"):
            link = art.query_selector("a[href]")
            if link:
                href = link.get_attribute("href") or link.evaluate("el => el.href")
                if href:
                    absolute = href if href.startswith("http") else urljoin(url, href)
                    hrefs.append(absolute)
        unique = list(dict.fromkeys(hrefs))
        browser.close()
        logging.info(f"Found {len(unique)} unique activity links.")
        return unique

def scrape_one(url: str, timeout_ms: int) -> Optional[Dict]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/127.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            page.route("**/*", lambda route, request: route.abort() if should_block(request.url) else route.continue_())
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            html = page.content()
            data = parse_detail_html(html)
            data["url"] = url
            browser.close()
            return data
    except Exception as e:
        logging.warning(f"Failed to scrape {url}: {e}")
        return None

def scrape_details(detail_urls: List[str], timeout_ms: int = 30000) -> List[Dict]:
    results = []
    total = len(detail_urls)
    logging.info(f"Scraping {total} detail pages with {MAX_WORKERS} workers...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scrape_one, url, timeout_ms): url for url in detail_urls}
        for i, future in enumerate(as_completed(futures), start=1):
            url = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    logging.info(f"[{i}/{total}] Done: {url}")
            except Exception as e:
                logging.warning(f"[{i}/{total}] Error scraping {url}: {e}")
    return results

def main() -> None:
    global MAX_WORKERS
    parser = argparse.ArgumentParser(description="Scrape GetYourGuide activities into CSV and JSON (fast mode).")
    parser.add_argument("--url", default=DEFAULT_URL, help="Listing page URL")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Timeout per page")
    parser.add_argument("--limit", type=int, default=10, help="Max number of detail pages to scrape")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Concurrent worker count")
    args = parser.parse_args()

    MAX_WORKERS = args.workers

    csv_file = Path("activities.csv")
    json_file = Path("activities.json")

    try:
        detail_urls = extract_all_article_hrefs_from_listing(args.url, timeout_ms=args.timeout_ms)
        if not detail_urls:
            logging.error("No activity links found.")
            sys.exit(1)

        if args.limit > 0:
            detail_urls = detail_urls[:args.limit]

        results = scrape_details(detail_urls, timeout_ms=args.timeout_ms)
        if results:
            with open(json_file, "w", encoding="utf-8") as jf:
                json.dump(results, jf, ensure_ascii=False, indent=2)
            logging.info(f"💾 Saved raw data to {json_file}")

            flat_results = [flatten_list_fields(r) for r in results]
            keys = flat_results[0].keys()

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(flat_results)
            logging.info(f"✅ Saved {len(flat_results)} records to {csv_file}")
        else:
            logging.warning("⚠️ No data scraped.")
    except Exception as exc:
        logging.error(f"Fatal error: {exc}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
