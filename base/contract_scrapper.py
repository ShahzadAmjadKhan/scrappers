import asyncio
import csv
import json
import math
import argparse
from playwright.async_api import async_playwright
from urllib.parse import parse_qs, urlencode

async def run(max_page):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Event to signal when all processing is done
        processing_done = asyncio.Event()

        async def handle_response(response):
            if "/Base4/en/resultados/" in response.url:
                try:
                    request = response.request
                    text_data = await response.text()
                    json_data = json.loads(text_data)

                    # Page 1
                    items = json_data.get("items", [])
                    total_records = json_data.get("total", 0)
                    page_size = 25
                    total_pages = math.ceil(total_records / page_size)
                    total_pages = min(total_pages, max_page)
                    print(f"Total records: {total_records} | Pages to fetch: {total_pages}")
                    print(f"Page 1: {len(items)} records.")
                    await save_items_to_csv(items, "results_page1.csv")

                    # Prepare headers
                    request_headers = dict(request.headers)
                    request_headers.pop("content-length", None)

                    # Parse initial form data
                    post_data = request.post_data
                    form_data = {}
                    if post_data:
                        form_data = {k: v[0] for k, v in parse_qs(post_data).items()}

                    # Loop through remaining pages
                    for page_number in range(2, total_pages + 1):
                        form_data["page"] = str(page_number)
                        new_response = await page.request.post(
                            url=request.url,
                            data=urlencode(form_data),
                            headers=request_headers
                        )
                        new_text_data = await new_response.text()
                        new_json_data = json.loads(new_text_data)
                        new_items = new_json_data.get("items", [])
                        print(f"Page {page_number}: {len(new_items)} records.")
                        await save_items_to_csv(new_items, f"results_page{page_number}.csv")

                    # Signal completion
                    processing_done.set()

                except Exception as e:
                    print(f"Error processing response: {e}")
                    processing_done.set()

        async def save_items_to_csv(items, filename):
            if isinstance(items, list) and len(items) > 0:
                keys = items[0].keys()
                with open(filename, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(items)
                print(f"Data saved to {filename}")
            else:
                print(f"No data found to save in {filename}.")

        page.on("response", handle_response)

        await page.goto("https://www.base.gov.pt/Base4/en/")
        await page.click("#advanced_contratos")
        await page.fill("input[name='texto']", " ")
        await page.click("#search_contratos")
        await page.wait_for_selector("text='Search results'")

        # Wait until all processing is done
        await processing_done.wait()

        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape contracts from base.gov.pt")
    parser.add_argument(
        "--max_page",
        type=int,
        default=5,
        help="Maximum number of pages to fetch (default: 5)"
    )
    args = parser.parse_args()
    asyncio.run(run(args.max_page))
