import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import random
import time

OUTPUT_FILE = "queenstown_listings.xlsx"
BASE_URL = "https://www.realestate.co.nz"
START_URL = "https://www.realestate.co.nz/residential/sale/central-otago-lakes-district/queenstown"

# Utility to pause scrolling to allow listings to load
async def auto_scroll(page, max_retries=3, scroll_step=1000, pause_time=3):

    retries = 0
    prev_listing_count = -1
    start_time = time.time()

    while retries < max_retries:
        # Scroll a bit down (not to bottom)
        await page.mouse.wheel(0, scroll_step)
        await page.wait_for_timeout(pause_time * 1000)

        # Count current listings
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        listings = soup.select('div[data-test="tile"]')
        curr_listing_count = len(listings)

        print(f"Listings loaded: {curr_listing_count}")

        if curr_listing_count == prev_listing_count:
            retries += 1
        else:
            retries = 0
            prev_listing_count = curr_listing_count

    print("Scrolling completed.")
    return soup


# Scrape all listing URLs
def extract_listing_urls(soup):
    urls = []
    for tile in soup.select('div[data-test="tile"]'):
        anchor = tile.select_one("a:has(> div.listed-date:first-child)")
        if anchor:
            href = anchor["href"]
            full_url = BASE_URL + href if href.startswith("/") else href
            urls.append(full_url)

    return list(set(urls))  # remove duplicates


async def scrape_fetures(soup):
    # Find the container with the features using the data-test attribute
    container = soup.find("div", attrs={"data-test": "features-icons"})

    # Initialize an empty dictionary to store the features
    features = {}

    # If the container exists
    if container:
        # Find all divs inside the container with class 'flex items-center'
        feature_blocks = container.find_all("div", class_="flex items-center")
        for i, feature_block in enumerate(feature_blocks):
            # Extract the <title> from <svg> to identify the feature
            title_tag = feature_block.find("title")
            if title_tag:
                feature_name = title_tag.get_text(strip=True).lower().replace(" ", "_")
            else:
                feature_name = "unknown"

            # Extract the text from the <span> tag next to the icon
            feature_text = feature_block.find("span").get_text(strip=True)

            # For the first feature, use the key 'property_type'
            if i == 0:
                features['property_type'] = feature_text
            else:
                features[feature_name] = feature_text

    return features

# Scrape details from each listing page
async def scrape_details(page, url):
    await page.goto(url)
    await page.wait_for_load_state("load")
    extract_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")
    agent_names = [h3.get_text(strip=True) for h3 in soup.select('div.property-agents h3')]
    if len(agent_names) > 1:
        merged_names = ', '.join(agent_names[:-1]) + ' & ' + agent_names[-1]
    else:
        merged_names = agent_names[0] if agent_names else ''

    agency_name = soup.select_one('div[data-test="agent-info__listing-agent-office"]')
    property_address = soup.select_one('h1[data-test="listing-title"]')
    primary_image_url = ""
    photo_block = soup.find("div", {"data-test": "photo-block"})
    if photo_block:
        img_tag = photo_block.find("img")
        if img_tag and img_tag.get("src"):
            primary_image_url = img_tag["src"]
    sales_method = soup.select_one('h3[data-test="pricing-method__price"]')
    features = await scrape_fetures(soup)
    listed_date = soup.select_one('span[data-test="description__listed-date"]')
    capital_value = soup.select_one('div[data-test="capital-valuation"] h4')
    # Placeholder object
    return {
        "Extract Date": extract_date,
        "Listing URL": url,
        "Agent Names": merged_names,
        "Agency Name": agency_name.get_text(strip=True) if agency_name else "",
        "Primary Image URL": primary_image_url if primary_image_url else "",
        "Property Address": property_address.get_text(strip=True) if property_address else "",
        "Sales Method": sales_method.get_text(strip=True) if sales_method else "",
        "Property Type": features.get("property_type",""),
        "Bedrooms": features.get("bedroom",""),
        "Bathrooms": features.get("bathroom",""),
        "Parking Space": features.get("garage",""),
        "Floor Area": features.get("floor_area",""),
        "Land Area": features.get("land_area",""),
        "Listing Date": listed_date.get_text(strip=True) if listed_date else "",
        "Capital Value":  capital_value.get_text(strip=True) if capital_value else "",
    }

async def get_total_pages_from_soup(soup):
    page_links = soup.select('div[data-test="paginated-items"] > div > a.paginated-items__page-number')
    page_numbers = [int(a.text.strip()) for a in page_links if a.text.strip().isdigit()]
    return max(page_numbers) if page_numbers else 1

# Main async function
async def main(max_pages=3):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        results = []

        current_page = 1
        START_URL_BASE = "https://www.realestate.co.nz/residential/sale/central-otago-lakes-district/queenstown"

        while True:
            current_url = START_URL_BASE if current_page == 1 else f"{START_URL_BASE}?page={current_page}"
            print(f"\n--- Visiting page {current_page}: {current_url} ---")
            await page.goto(current_url)
            soup = await auto_scroll(page)

            if current_page == 1:
                total_pages = await get_total_pages_from_soup(soup)
                total_pages = min(total_pages, max_pages)
                print(f"Scraping up to {total_pages} page(s).")

            urls = extract_listing_urls(soup)
            print(f"Found {len(urls)} listing URLs on page {current_page}.")

            page_results = []

            for i, url in enumerate(urls, 1):
                print(f"[Page {current_page} - {i}/{len(urls)}] Scraping: {url}")
                try:
                    data = await scrape_details(page, url)
                    page_results.append(data)

                    delay = random.uniform(1.5, 4.0)
                    print(f"Sleeping for {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue

            if page_results:
                df = pd.DataFrame(page_results)
                file_name = f"queenstown_page_{current_page}.xlsx"
                df.to_excel(file_name, index=False)
                print(f"✅ Saved page {current_page} data to '{file_name}'")

            results.extend(page_results)

            if current_page >= total_pages:
                break

            current_page += 1

        await browser.close()

        # Save results to Excel
        df = pd.DataFrame(results)
        df.to_excel("queenstown_listings.xlsx", index=False)
        print(f"\n✅ Saved {len(results)} listings to 'queenstown_listings.xlsx'.")

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
