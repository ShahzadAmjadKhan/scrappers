import asyncio
import pandas as pd
import random
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("lancaster_parcel_scraper.log"),
        logging.StreamHandler()
    ]
)

async def scrape_parcel(parcel_number, page):
    cleaned_parcel_number = parcel_number.replace("-", "")
    url = f"https://lancasterpa.devnetwedge.com/parcel/view/{cleaned_parcel_number}/2025"
    logging.info(f"Scraping: {url}")

    await page.goto(url, wait_until="networkidle", timeout=60000)
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Extract Parcel ID
    parcel_id_div = soup.find('div', class_='panel-body', id='overview-body')
    property_id = ''
    if parcel_id_div:
        row = parcel_id_div.find('div', class_='row')
        if row:
            property_id_div = row.find_all('div', class_='col-sm-7')
            if property_id_div and len(property_id_div) > 0:
                property_id = property_id_div[0].text.strip()

    # Extract Property Owner & Address
    owner_info_div = soup.find('div', style=lambda x: x and 'border' in x)
    owner_name = ''
    address_lines = []

    if owner_info_div:
        rows = owner_info_div.find_all('div', class_='row')
        for r in rows:
            label_div = r.find('div', class_='inner-label')
            value_divs = r.find_all('div', class_='col-sm-8')
            if label_div and 'Parcel Owner' in label_div.text and value_divs:
                owner_name = value_divs[0].text.strip()
            elif label_div and label_div.text.strip() == '' and value_divs:
                for value_div in value_divs:
                    address_lines.append(value_div.text.strip())

    property_address = ', '.join(address_lines)

    # Check for Delinquent Taxes
    delinquent_rows = []
    delinquent_panel = soup.find('div', class_='panel-heading', string=lambda text: text and text.strip() == 'Delinquent Taxes')
    if delinquent_panel:
        table = delinquent_panel.find_next_sibling('div', class_='panel-body').find_next_sibling('table')
        if table:
            rows = table.find_all('tr')[1:]  # skip header
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    year = cells[0].text.strip()
                    amount = cells[1].text.strip()
                    delinquent_rows.append({
                        "Parcel Number": property_id or parcel_number,
                        "Tax Year": year,
                        "Delinquent Tax Amount": amount,
                        "Owner Name": owner_name,
                        "Property Address": property_address
                    })
    else:
        # No Delinquent Taxes found
        delinquent_rows.append({
            "Parcel Number": property_id or parcel_number,
            "Tax Year": 'N/A',
            "Delinquent Tax Amount": '0.00',
            "Owner Name": owner_name,
            "Property Address": property_address
        })

    logging.info(f"Scraping completed for parcel {parcel_number}")
    return delinquent_rows

async def process_batch(batch, browser, concurrency=5):
    sem = asyncio.Semaphore(concurrency)
    results = []

    async def scrape_with_limit(parcel_number):
        async with sem:
            page = await browser.new_page()
            try:
                result = await scrape_parcel(parcel_number, page)
            except Exception as e:
                logging.error(f"Error scraping {parcel_number}: {e}")
                result = [{
                    "Parcel Number": parcel_number,
                    "Tax Year": 'N/A',
                    "Delinquent Tax Amount": 'N/A',
                    "Owner Name": 'N/A',
                    "Property Address": 'N/A'
                }]
            finally:
                await page.close()
                await asyncio.sleep(random.uniform(1, 3))
            return result

    tasks = [scrape_with_limit(pn) for pn in batch]
    all_results = await asyncio.gather(*tasks)
    for result in all_results:
        results.extend(result)
    return results

async def main(parcel_numbers, proxy_url=None):
    batch_size = 5000  # adjust as needed
    all_data = []

    async with async_playwright() as p:
        browser_args = {
            "headless": True
        }
        if proxy_url:
            browser_args["proxy"] = {"server": proxy_url}
            logging.info(f"Using proxy: {proxy_url}")
        else:
            logging.info("No proxy configured. Proceeding without proxy.")

        browser = await p.chromium.launch(**browser_args)

        for i in range(0, len(parcel_numbers), batch_size):
            batch = parcel_numbers[i:i+batch_size]
            batch_number = i // batch_size + 1
            total_batches = (len(parcel_numbers) - 1) // batch_size + 1
            logging.info(f"Processing batch {batch_number} of {total_batches} (parcels {i+1} to {i+len(batch)})")
            batch_results = await process_batch(batch, browser)
            all_data.extend(batch_results)
            # Save intermediate results
            df = pd.DataFrame(all_data)
            df.to_excel(f"lancaster_parcel_data_batch_{batch_number}.xlsx", index=False)
            logging.info(f"Batch {batch_number} saved with {len(batch_results)} rows.")
            await asyncio.sleep(random.uniform(10, 20))  # polite delay between batches

        await browser.close()
    logging.info("All batches processed and saved.")

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Lancaster Parcel Scraper")
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="Optional proxy URL, e.g., http://143.198.42.182:31280"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="parcel_numbers.txt",
        help="Path to the input file with parcel numbers"
    )
    args = parser.parse_args()

    try:
        with open(args.input_file) as f:
            parcel_numbers = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(parcel_numbers)} parcel numbers from file '{args.input_file}'.")
        asyncio.run(main(parcel_numbers, proxy_url=args.proxy))
    except Exception as e:
        logging.exception(f"Script terminated with an error: {e}")
