import asyncio
from patchright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import csv
import random
import logging
from urllib.parse import urljoin

ZILLOW_SEARCH_URL = "https://www.zillow.com/homes/for_sale/Los-Angeles_rb/"  # Use local city if needed

async def delay(page: Page, min_delay: float = 1.0, max_delay: float = 3.0) -> None:
    """
    Introduces a random delay to mimic human behavior.

    Args:
        page: The Playwright Page object.
        min_delay: Minimum delay in seconds.
        max_delay: Maximum delay in seconds.
    """
    sleep_time = random.uniform(min_delay, max_delay)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds.")
    await page.wait_for_timeout(sleep_time * 1000)

async def extract_listing_details(context, url):
    page = await context.new_page()
    try:
        await delay(page)  # simulate delay before navigation
        await page.goto(url, timeout=60000)
        await delay(page)  # simulate delay after page load

        await page.wait_for_selector("h1", timeout=10000)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else ""
        address = soup.select_one("h1 ~ h2").get_text(strip=True) if soup.select_one("h1 ~ h2") else ""

        agent_block = soup.find("section", {"data-testid": "listing-agent-section"})
        agent_name = ""
        if agent_block:
            agent_name_tag = agent_block.find("div", string=lambda s: s and "Agent" in s)
            if agent_name_tag:
                agent_name = agent_name_tag.get_text(strip=True)

        return {
            "title": title,
            "address": address,
            "agent_name": agent_name,
            "agent_email": "",  # Not provided
        }
    except Exception as e:
        print(f"[!] Error extracting {url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_zillow():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./data",
            channel="chrome",
            headless=False,
            no_viewport=True )
        # context = await browser.new_context(user_agent=(
        #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        #     "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        # ))

        page = await browser.new_page()
        await page.goto(ZILLOW_SEARCH_URL, timeout=60000)
        await page.wait_for_selector("ul.photo-cards li article", timeout=20000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        cards = soup.select("ul.photo-cards li article a[data-test='property-card-link']")

        base_url = "https://www.zillow.com"
        urls = list({urljoin(base_url, a['href'].split('?')[0]) for a in cards if a.get('href')})

        for link in urls[:10]:  # Limit to 10 for demo
            print(f"Scraping {link}")
            await delay(page)
            details = await extract_listing_details(browser, link)
            if details:
                listings.append(details)

        await browser.close()

        # Save to CSV
        with open("zillow_listings.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "address", "agent_name", "agent_email"])
            writer.writeheader()
            writer.writerows(listings)

        print(f"✅ Scraped {len(listings)} listings.")

if __name__ == "__main__":
    asyncio.run(scrape_zillow())