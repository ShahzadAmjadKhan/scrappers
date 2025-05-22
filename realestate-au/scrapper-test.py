import asyncio
import re
import time
import subprocess
from gologin import GoLogin
from asyncio.log import logger
import undetected_chromedriver as uc
from lazy_object_proxy.utils import await_

# from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from playwright.async_api import async_playwright

# gl = GoLogin(
#     {
#         "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzBjZTQwNmE4NjI4OWViNjdhMWNmMzciLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NzBjZTVkNzZhMWIxZGZmYmM2YmI1YjUifQ._sm0IuaL2V9dds9vVJoPj01AiUPnIV9ZlN5heTi8Kj8",
#         "profile_id":"670ce406a86289eb67a1cfcd"
#     }
# )

# debugger_address = gl.start()

# Function to start the browser using subprocess
def start_browser_with_debugging():
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    # Start Chrome with remote debugging on port 9222
    subprocess.Popen([edge_path, "--remote-debugging-port=9222"])
    # Give the browser some time to start
    time.sleep(3)
    print("Edge started")

async def connect_to_browser() -> None:
    async with async_playwright() as p:
        browser = await  p.chromium.connect_over_cdp("http://localhost:9222")
        default_context  = browser.contexts[0]
        page = default_context.pages[0]
        await page.goto('https://www.realestate.com.au/find-agent', timeout=0)
        input_field = page.get_by_placeholder("Search by region, suburb or postcode")
        await input_field.fill('3000')
        # //await page.wait_for_load_state('load')
        await page.wait_for_load_state('networkidle')
        await page.keyboard.press('Enter')
        await page.wait_for_load_state()
        await page.wait_for_selector('#wrapper > div:nth-child(2) > section')
        names = await page.locator('.agent-profile__name').all()
        for name in names:
            full_name = await name.text_content()
            print(f'Name found: {full_name}')

        await page.close()
        await browser.close()

        # await page.screenshot(path="pl_kasada.png")

# Main function to start the browser and connect using Playwright
async def main():import asyncio
from patchright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.realestate.com.au/buy/in-sydney,+nsw/list-{}"

async def scrape_page(page, page_number):
    url = BASE_URL.format(page_number)
    print(f"Scraping: {url}")
    await page.goto(url, timeout=60000)
    await page.wait_for_selector("article")

    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    results = []

    for card in soup.select("article"):
        try:
            title = card.select_one("a.details-link") or card.select_one("a.residential-card__details-link")
            price = card.select_one("span.property-price")
            address = card.select_one("span.property-address")

            data = {
                "title": title.get_text(strip=True) if title else "",
                "url": f"https://www.realestate.com.au{title['href']}" if title else "",
                "price": price.get_text(strip=True) if price else "",
                "address": address.get_text(strip=True) if address else ""
            }

            results.append(data)
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        all_results = []
        for page_number in range(1, 6):  # Scrape first 5 pages
            results = await scrape_page(page, page_number)
            all_results.extend(results)

        await browser.close()

        # Save to CSV
        with open("realestate_listings.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "url", "price", "address"])
            writer.writeheader()
            writer.writerows(all_results)

        print(f"Scraped {len(all_results)} listings.")

if __name__ == "__main__":
    asyncio.run(main())

    # Step 1: Start the browser
    start_browser_with_debugging()

    # Step 2: Connect to the browser using CDP
    await connect_to_browser()

if __name__ == '__main__':
    asyncio.run(main())

