import asyncio
from patchright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv

SEARCH_URL = "https://www.realestate.com.au/buy/list-{}?locations=gold-coast%2C%2Cnorthern-nsw"

async def extract_listing_details(context, listing_url):
    page = await context.new_page()
    try:
        await page.goto(listing_url, timeout=60000)
        await page.wait_for_selector("body")

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1") or soup.select_one("h1.property-info__heading")
        address = soup.select_one("span.address") or soup.select_one("h2.property-info__address")
        agent_name = soup.select_one(".agent-card__name, .listing-agent__name")
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

async def scrape_results(page, context, page_number):
    url = SEARCH_URL.format(page_number)
    print(f"Scraping search page: {url}")
    await page.goto(url)
    await page.wait_for_selector("article")

    soup = BeautifulSoup(await page.content(), "html.parser")
    listings = []

    cards = soup.select("article a.details-link, article a.residential-card__details-link")
    listing_links = list({f"https://www.realestate.com.au{a['href']}" for a in cards if a.get('href')})

    for link in listing_links:
        details = await extract_listing_details(context, link)
        if details:
            listings.append(details)

    return listings

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        all_listings = []
        for page_number in range(1, 4):  # Scrape first 3 pages
            listings = await scrape_results(page, context, page_number)
            all_listings.extend(listings)

        await browser.close()

        # Save to CSV
        with open("goldcoast_nsw_listings.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "address", "agent_name", "agent_email"])
            writer.writeheader()
            writer.writerows(all_listings)

        print(f"Scraped {len(all_listings)} listings.")

if __name__ == "__main__":
    asyncio.run(main())
