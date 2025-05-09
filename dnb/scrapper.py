import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page
import random
import time
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
]
# Add more user agents as needed

# Function to get a random user agent
def get_random_user_agent() -> str:
    """
    Returns a random user agent from the list.
    """
    return random.choice(USER_AGENTS)

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
    await page.wait_for_timeout(sleep_time * 1000)  # Convert seconds to milliseconds

async def extract_business_data(page: Page) -> Optional[Dict]:
    """
    Extracts business data from the current page.  Handles potential errors
    and missing elements robustly.

    Args:
        page: The Playwright Page object.

    Returns:
        A dictionary containing the extracted data, or None on failure.
    """
    try:
        # Wait for the main content container to load.  This is crucial for reliability.
        await page.wait_for_selector('div.business-main', timeout=10000)

        # Extract data using CSS selectors.  Use more specific selectors.
        name_element = await page.query_selector('h1.business-name')  # More specific selector
        name = await name_element.inner_text() if name_element else "N/A"

        address_element = await page.query_selector('span.street-address')
        street = await address_element.inner_text() if address_element else "N/A"

        city_element = await page.query_selector('span.locality')
        city = await city_element.inner_text() if city_element else "N/A"

        state_element = await page.query_selector('span.region')
        state = await state_element.inner_text() if state_element else "N/A"

        zip_element = await page.query_selector('span.postal-code')
        zip_code = await zip_element.inner_text() if zip_element else "N/A"

        phone_element = await page.query_selector('span.phone')  # More specific selector
        phone = await phone_element.inner_text() if phone_element else "N/A"

        website_element = await page.query_selector('a.website-link')  # More specific
        website = await website_element.get_attribute('href') if website_element else "N/A"

        # Create full address
        full_address = f"{street}, {city}, {state} {zip_code}"

        # Log success
        logging.info(f"Extracted data for: {name}")

        return {
            "name": name,
            "full_address": full_address,
            "phone": phone,
            "website": website,
        }
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        return None  # Important: Return None on error

async def navigate_to_next_page(page: Page) -> bool:
    """
    Navigates to the next page, handling potential errors and anti-bot measures.

    Args:
        page: The Playwright Page object.

    Returns:
        True if navigation was successful, False otherwise.
    """
    try:
        # Wait for the next page button to be clickable.
        next_page_button = await page.query_selector('a.pagination-next') # More specific selector.
        if next_page_button:
            await next_page_button.click(timeout=5000)
            await delay(page)  # Introduce delay after clicking
            return True
        else:
            logging.info("No more pages to navigate.")
            return False
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False

async def scrape_dnb(search_query: str, max_pages: int = 5) -> List[Dict]:
    """
    Scrapes business data from D&B for a given search query, with anti-bot measures.

    Args:
        search_query: The search query (e.g., "restaurants in New York").
        max_pages: Maximum number of pages to scrape.

    Returns:
        A list of dictionaries, where each dictionary contains business data.
        Returns an empty list if no data is found or an error occurs.
    """
    results: List[Dict] = []
    current_page = 1

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Launch in headless mode
        context = await browser.new_context(
            user_agent=get_random_user_agent(),  # Set a random user agent
            ignore_https_errors=True,  # Ignore HTTPS errors, if necessary (use with caution)
        )
        page = await context.new_page()

        try:
            # 1. Initial navigation and search
            await page.goto("https://www.dnb.com/business-directory.html", timeout=10000)
            await delay(page)

            # Locate the search input and submit the query
            search_input = await page.query_selector('input#search')  # Corrected selector
            if search_input:
                await search_input.type(search_query, delay=100)
                await search_input.press("Enter")
                await delay(page, 5, 8) # Increased delay after search
            else:
                raise Exception("Search input not found.")

            # 2. Main scraping loop
            while current_page <= max_pages:
                logging.info(f"Scraping page: {current_page}")

                # Wait for the search results to load.  Important for reliability.
                await page.wait_for_selector('div.search-results', timeout=10000)

                # Extract data from the current page
                # Use a more robust way to select all business listings
                business_links = await page.query_selector_all('a.business-name-link')  # Changed selector

                if not business_links:
                    logging.warning(f"No business links found on page {current_page}.  Stopping.")
                    break  # Exit the loop if no links are found

                for link in business_links:
                    try:
                        # Introduce a small delay before navigating to each business page
                        await delay(page, 0.5, 1.5)

                        # Get the URL *before* navigating.
                        business_url = await link.get_attribute('href')
                        if business_url:
                            # Create a new page for each business.  This is crucial for avoiding
                            # interference between different pages and for better error handling.
                            business_page = await context.new_page()
                            await business_page.goto(business_url, timeout=10000)
                            await delay(business_page, 1, 3) # Add delay for individual business page load
                            business_data = await extract_business_data(business_page)
                            await business_page.close() # Close the tab after scraping
                            if business_data:  # Only add if data was extracted successfully
                                results.append(business_data)
                    except Exception as e:
                        logging.error(f"Error processing a business link: {e}")
                        # Consider using a retry mechanism here if needed

                # 3. Navigate to the next page
                if not await navigate_to_next_page(page):
                    break  # Exit loop if no more pages

                current_page += 1
                await delay(page, 2, 4) # Delay before going to next page

        except Exception as e:
            logging.error(f"General error during scraping: {e}")
            results = []  # Ensure an empty list is returned on error
        finally:
            await browser.close()  # Ensure the browser is closed

    return results

if __name__ == "__main__":
    search_query = "restaurants in New York"
    max_pages = 3  # Limit the number of pages to avoid getting blocked.
    data = asyncio.run(scrape_dnb(search_query, max_pages))

    if data:
        print(f"Found {len(data)} businesses:")
        for business in data:
            print(business)
    else:
        print("No data found or an error occurred.")
