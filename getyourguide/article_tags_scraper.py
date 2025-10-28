import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.getyourguide.com/london-l57/"


def render_and_collect_articles(url: str, timeout_ms: int = 30000) -> List[str]:
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
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        # Wait for potential dynamic content; try selector then network idle fallback
        try:
            page.wait_for_selector("article", timeout=10000)
        except Exception:
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass

        article_elements = page.query_selector_all("article")
        outer_html_list: List[str] = []
        for el in article_elements:
            try:
                outer_html = el.evaluate("el => el.outerHTML")
                if isinstance(outer_html, str):
                    outer_html_list.append(outer_html)
            except Exception:
                continue

        context.close()
        browser.close()
        return outer_html_list


def extract_article_tags(url: str) -> List[str]:
    return render_and_collect_articles(url)


def extract_first_article_href_from_listing(url: str, timeout_ms: int = 30000) -> Optional[str]:
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
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_selector("article a[href]", timeout=15000)
        except Exception:
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
        # Try primary selector, fallbacks for possible structures
        link = page.locator("article a[href]").first
        href: Optional[str] = None
        if link.count() > 0:
            href = link.evaluate("el => el.href")
        if not href:
            candidates = page.query_selector_all("a[href][data-test-id*='activity-card'], a[href][aria-label*='details']")
            for el in candidates:
                href = el.evaluate("el => el.href")
                if href:
                    break
        context.close()
        browser.close()
        return href


def extract_all_article_hrefs_from_listing(url: str, timeout_ms: int = 30000) -> List[str]:
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
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_selector("article a[href]", timeout=15000)
        except Exception:
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass

        hrefs: List[str] = []
        articles = page.query_selector_all("article")
        for art in articles:
            try:
                link = art.query_selector("a[href]")
                if not link:
                    continue
                href = link.evaluate("el => el.getAttribute('href') || el.href")
                if not href:
                    continue
                absolute = href if href.startswith("http") else urljoin(url, href)
                hrefs.append(absolute)
            except Exception:
                continue

        # Deduplicate while preserving order
        seen = set()
        unique_hrefs: List[str] = []
        for h in hrefs:
            if h in seen:
                continue
            seen.add(h)
            unique_hrefs.append(h)

        context.close()
        browser.close()
        return unique_hrefs


def text_or_none(el: Optional[object]) -> Optional[str]:
    if not el:
        return None
    text = getattr(el, "get_text", None)
    if callable(text):
        return el.get_text(strip=True)
    return None


def select_text_by_heading(soup: BeautifulSoup, heading_regex: str) -> Optional[str]:
    pattern = re.compile(heading_regex, re.I)
    heading = soup.find(["h2", "h3", "h4"], string=pattern)
    if not heading:
        # Some headings are rendered as divs/spans with same text
        heading = soup.find(["div", "span", "p"], string=pattern)
    if not heading:
        return None
    # Collect text from siblings until the next heading-like element
    texts: List[str] = []
    for sib in heading.find_all_next():
        if sib is heading:
            continue
        if sib.name in {"h2", "h3", "h4"}:
            break
        # gather list items or paragraphs within a bounded container
        if sib.name in {"ul", "ol"}:
            for li in sib.find_all("li"):
                t = text_or_none(li)
                if t:
                    texts.append(t)
            break
        if sib.name == "p":
            t = text_or_none(sib)
            if t:
                texts.append(t)
            # If we got a decent paragraph, stop early
            if len(" ".join(texts)) > 50:
                break
    return "; ".join(texts) if texts else None


def parse_detail_html(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = None
    candidates = [
        soup.select_one("#adp-title-text"),
        soup.select_one("h1[data-test-id='activity-title']"),
        soup.select_one("h1.text-atom--title-1"),
        soup.find("h1"),
    ]
    for c in candidates:
        title = text_or_none(c)
        if title:
            break

    # Rating and Reviews
    rating = None
    reviews = None
    # Common patterns: aria-label like "4.7 out of 5" and sibling text like "7,800 reviews"
    rating_text_candidates = soup.select("[aria-label*='out of 5'], [data-test-id*='rating'], [itemprop='ratingValue']")
    for el in rating_text_candidates:
        t = el.get("aria-label") or text_or_none(el)
        if not t:
            continue
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:/|out of)\s*5", t)
        if m:
            rating = m.group(1)
            break
        m = re.search(r"\b(\d(?:\.\d+)?)\b", t)
        if m and float(m.group(1)) <= 5:
            rating = m.group(1)
            break
    if not rating:
        # Fallback: look for text near the first star icon container
        star = soup.find(attrs={"class": re.compile("rating|stars", re.I)})
        if star:
            t = star.get_text(" ", strip=True)
            m = re.search(r"(\d+(?:\.\d+)?)", t)
            if m:
                rating = m.group(1)

    m_reviews = re.search(r"([\d,.]+)\s+reviews", soup.get_text(" ", strip=True), re.I)
    if m_reviews:
        reviews = f"{m_reviews.group(1)} reviews"

    # Provider
    provider = None
    provider_el = soup.find(string=re.compile(r"(Provider|Provided by|Organized by)", re.I))
    if provider_el and provider_el.parent:
        # next significant text on the same line or following sibling
        next_text = provider_el.parent.get_text(" ", strip=True)
        m = re.search(r"(?:Provider|Provided by|Organized by)\s*:?\s*(.+)$", next_text, re.I)
        if m:
            provider = m.group(1)
    if not provider:
        prov_candidate = soup.select_one("[data-test-id='supplier-name'], [data-test-id*='supplier']")
        provider = text_or_none(prov_candidate)

    # Price: prioritize the explicit price container if present
    price = None
    price_candidates = [
        soup.select_one(".price-info__actual-price-explanation"),
        soup.select_one("[data-test-id='price'], [data-test-id='activity-price']"),
        soup.find(attrs={"class": re.compile(r"price|amount|from", re.I)}),
    ]
    for pc in price_candidates:
        if not pc:
            continue
        t = pc.get_text(" ", strip=True)
        m = re.search(r"([€$£]\s*\d+[\d,\.]*|\d+[\d,\.]*\s*[€$£])", t)
        if m:
            price = m.group(1).replace(" ", "")
            break
    if not price:
        m = re.search(r"([€$£]\s*\d+[\d,\.]*|\d+[\d,\.]*\s*[€$£])", soup.get_text(" ", strip=True))
        if m:
            price = m.group(1).replace(" ", "")

    # Short Description (top blurb)
    description = None
    desc_candidate = soup.select_one("[data-test-id='product-short-description']")
    description = text_or_none(desc_candidate)
    if not description:
        # Fallback: meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            description = meta.get("content").strip()

    # Itinerary section
    itinerary = select_text_by_heading(soup, r"^Itinerary$")

    # About: Prefer the section list under 'About' or 'About this activity'
    about = None
    about_heading = soup.find(["h2", "h3"], string=re.compile(r"^About( this activity)?$", re.I))
    if about_heading:
        # Find the nearest following list
        section_container = about_heading.find_next(lambda tag: tag.name in {"ul", "div", "section"})
        items: List[str] = []
        if section_container:
            for li in section_container.select("li"):
                txt = li.get_text(" ", strip=True)
                if txt:
                    items.append(txt)
        if items:
            about = ", ".join(items)
    if not about:
        # Fallback to previous heuristic but keep bracketed parts intact
        about_items: List[str] = []
        for key in ["Free cancellation", "Duration", "Host or greeter", "Skip the line", "Small group"]:
            m = re.search(rf"{re.escape(key)}(?:\s*\(([^)]*)\))?", soup.get_text(" ", strip=True), re.I)
            if m:
                if m.group(1):
                    about_items.append(f"{key} ({m.group(1)})")
                else:
                    about_items.append(key)
        about = ", ".join(about_items) if about_items else None

    # Highlights
    highlights_text = select_text_by_heading(soup, r"^Highlights$")

    # Full description and other sections using more robust section scoping
    def collect_section_after_heading(heading_text_regex: str) -> Optional[str]:
        h = soup.find(["h2", "h3"], string=re.compile(heading_text_regex, re.I))
        if not h:
            return None
        # Try to find a wrapping section/div tied to this heading via aria-labelledby
        section = None
        heading_id = h.get("id")
        if heading_id:
            section = soup.find(attrs={"aria-labelledby": heading_id})
        if not section:
            # Fallback: next siblings until next heading
            texts: List[str] = []
            for sib in h.find_all_next():
                if sib is h:
                    continue
                if sib.name in {"h2", "h3"}:
                    break
                if sib.name in {"p", "li"}:
                    t = sib.get_text(" ", strip=True)
                    if t:
                        texts.append(t)
            return "\n".join(texts) if texts else None
        # If we have a section, collect paragraphs and list items within
        texts: List[str] = []
        for el in section.select("p, li"):
            t = el.get_text(" ", strip=True)
            if t:
                texts.append(t)
        return "\n".join(texts) if texts else None

    full_description = collect_section_after_heading(r"^Full description$") or select_text_by_heading(soup, r"^Full description$")
    includes = collect_section_after_heading(r"^Includes$") or select_text_by_heading(soup, r"^Includes$")
    not_suitable = collect_section_after_heading(r"^Not suitable for$") or select_text_by_heading(soup, r"^Not suitable for$")
    meeting_point = collect_section_after_heading(r"^Meeting point$") or select_text_by_heading(soup, r"^Meeting point$")
    important_info = collect_section_after_heading(r"^Important information$") or select_text_by_heading(soup, r"^Important information$")

    return {
        "Title": title,
        "Rating": rating,
        "Reviews": reviews,
        "Provider": provider,
        "Price": price,
        "Description": description,
        "Itinerary": itinerary,
        "About": about,
        "Highlights": highlights_text,
        "Full description": full_description,
        "Includes": includes,
        "Not suitable for": not_suitable,
        "Meeting point": meeting_point,
        "Important information": important_info,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch and list all <article> tags from a GetYourGuide page."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Page URL to fetch (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=30000,
        help="Navigation timeout in milliseconds (default: 30000)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max number of detail URLs to visit from the listing (default: 5)",
    )
    args = parser.parse_args()

    # Navigate listing: gather all article links, visit each, extract
    try:
        detail_urls = extract_all_article_hrefs_from_listing(args.url, timeout_ms=args.timeout_ms)
        if not detail_urls:
            print("Error: No article links found on the listing page.", file=sys.stderr)
            sys.exit(1)
        if args.limit and args.limit > 0:
            detail_urls = detail_urls[:args.limit]

        results: List[Dict[str, Optional[str]]] = []
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
            for href in detail_urls:
                try:
                    page.goto(href, wait_until="domcontentloaded", timeout=args.timeout_ms)
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass
                    html = page.content()
                    data = parse_detail_html(html)
                    data["url"] = href
                    results.append(data)
                except Exception:
                    continue
            context.close()
            browser.close()

        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


