#!/usr/bin/env python3
"""
Mark Cuban Companies Scraper (socials + website refined version)

Extracts:
  - brand_name
  - company_page
  - website (from div.col.websites)
  - facebook / instagram / twitter / linkedin (from div.col.socials)

Keeps empty values if not found.
Filters out known global social links.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter, Retry

# ---- Constants ----
BASE = "https://markcubancompanies.com"
COMPANY_PREFIX = BASE.rstrip("/") + "/companies/"
UNWANTED_FACEBOOK = "https://www.facebook.com/markcuban?fref=ts"
UNWANTED_INSTAGRAM = "https://www.instagram.com/markcubancompanies/"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MCCBot/1.0; +https://example.com/bot)"}
DELAY = 0.8  # seconds between requests

# ---- HTTP session with retry ----
SESSION = requests.Session()
retries = Retry(total=5, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
SESSION.mount("https://", HTTPAdapter(max_retries=retries))
SESSION.headers.update(HEADERS)


def get_soup(url):
    """Fetch a page and return BeautifulSoup object."""
    try:
        resp = SESSION.get(url, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def find_company_links(start_urls):
    """Find all company page URLs from site."""
    found = set()
    for url in start_urls:
        print(f"[crawl] {url}")
        soup = get_soup(url)
        if not soup:
            continue
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"].strip())
            parsed = urlparse(href)
            href = parsed.scheme + "://" + parsed.netloc + parsed.path
            if href.startswith(COMPANY_PREFIX):
                found.add(href)
        time.sleep(DELAY)
    return sorted(found)


def extract_company_data(url):
    """Extract company data from its page."""
    data = {
        "brand_name": "",
        "company_page": url,
        "website": "",
        "facebook": "",
        "instagram": "",
        "twitter": "",
        "linkedin": "",
    }

    print(f"[extract] {url}")
    soup = get_soup(url)
    if not soup:
        return data

    # ---- Brand name ----
    h1 = soup.select_one("div.entry-content h1")
    if h1:
        data["brand_name"] = h1.get_text(strip=True)

    # ---- Website ----
    website_div = soup.select_one("div.col.websites a[href]")
    if website_div:
        href = website_div.get("href", "").strip()
        if href.startswith("http"):
            data["website"] = href

    # ---- Social links ----
    socials_div = soup.select("div.col.socials a[href]")
    for a in socials_div:
        href = a.get("href", "").strip().lower()
        if not href:
            continue
        if "facebook.com" in href and not data["facebook"]:
            data["facebook"] = href
        elif "instagram.com" in href and not data["instagram"]:
            data["instagram"] = href
        elif "linkedin.com" in href and not data["linkedin"]:
            data["linkedin"] = href
        elif ("twitter.com" in href or "x.com" in href) and not data["twitter"]:
            data["twitter"] = href

    # ---- Filter unwanted generic links ----
    if data["instagram"].startswith(UNWANTED_INSTAGRAM.lower()):
        data["instagram"] = ""
    if data["facebook"].startswith(UNWANTED_FACEBOOK.lower()):
        data["facebook"] = ""

    return data


def save_csv(rows, filename="companies.csv"):
    """Write results to CSV."""
    fields = [
        "brand_name",
        "company_page",
        "website",
        "facebook",
        "instagram",
        "twitter",
        "linkedin",
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"[done] Saved {len(rows)} records to {filename}")


def main():
    start_urls = [
        "https://markcubancompanies.com/",
    ]

    company_links = find_company_links(start_urls)
    print(f"[found] {len(company_links)} company links")

    results = []
    for i, link in enumerate(company_links, start=1):
        print(f"[{i}/{len(company_links)}] {link}")
        data = extract_company_data(link)
        results.append(data)
        time.sleep(DELAY)

    save_csv(results)


if __name__ == "__main__":
    main()
