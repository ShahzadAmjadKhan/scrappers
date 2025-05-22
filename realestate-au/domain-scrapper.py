import asyncio
from patchright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv

SEARCH_URL = "https://www.domain.com.au/sale/gold-coast-qld/?page={}"

async def extract_listing_details(browser, listing_url):
    page = await browser.new_page()
    try:
        await page.goto(listing_url, timeout=60000)
        await page.wait_for_selector("body")

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1") or soup.select_one("h1[data-testid='listing-details__summary-title']")
        address = soup.select_one("h2[data-testid='listing-details__address']")

        agent_name = soup.select_one("[data-testid='listing-details__agent-name']")
        agent_email = soup.find("a", href=lambda href: href and "mailto:" in href)

        return {
            "title": title.get_text(strip=True) if title else "",
            "address": address.get_text(strip=True) if address else "",
            "agent_name": agent_name.get_text(strip=True) if agent_name else "",
            "agent_email": agent_email['href'].replace("mailto:", "") if agent_email else ""
        }
    except Exception as e:
        print(f"Error extracting {listing_url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_results(page, browser, page_number):
    url = SEARCH_URL.format(page_number)
    print(f"Scraping search page: {url}")
    await page.goto(url)
    await page.wait_for_selector("article", timeout=20000)

    soup = BeautifulSoup(await page.content(), "html.parser")
    listings = []

    cards = soup.select("article a[href*='/property-']")
    listing_links = list({f"https://www.domain.com.au{a['href']}" for a in cards if a.get('href')})

    for link in listing_links:
        details = await extract_listing_details(browser, link)
        if details:
            listings.append(details)

    return listings

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="...",
            channel="chrome",
            headless=False,
            no_viewport=True )
        # browser = await p.chromium.launch(headless=True)
        # context = await browser.new_context()
        page = await browser.new_page()

        all_listings = []
        for page_number in range(1, 4):  # Scrape first 3 pages
            listings = await scrape_results(page, browser, page_number)
            all_listings.extend(listings)

        await browser.close()

        # Save to CSV
        with open("domain_listings.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "address", "agent_name", "agent_email"])
            writer.writeheader()
            writer.writerows(all_listings)

        print(f"Scraped {len(all_listings)} listings.")

if __name__ == "__main__":
    asyncio.run(main())
