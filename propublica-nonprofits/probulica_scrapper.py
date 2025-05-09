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

async def scrape_propublica(search_query: str, max_pages: int = 5):
    """
    Scrapes business data from D&B for a given search query, with anti-bot measures.

    Args:
        search_query: The search query (e.g., "restaurants in New York").
        max_pages: Maximum number of pages to scrape.

    Returns:
        A list of dictionaries, where each dictionary contains business data.
        Returns an empty list if no data is found or an error occurs.
    """
    current_page = 1

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, timeout=60000) # Launch in headless mode
        context = await browser.new_context(
            user_agent=get_random_user_agent(),  # Set a random user agent
            ignore_https_errors=True,            # Ignore HTTPS errors, if necessary (use with caution)
        )
        page = await context.new_page()
        page.set_default_navigation_timeout(60000)
        try:
            # Go to ProPublica Nonprofits site
            await page.goto("https://projects.propublica.org/nonprofits")
            await page.fill('#big-search', search_query)
            await page.get_by_text('Advanced').click()
            await page.select_option('#state-filter', 'AK')
            await page.get_by_role("button", name="Search").click()
            await page.wait_for_selector('div.result-rows', timeout=10000)

            print("Search results loaded successfully.")
        except Exception as e:
            logging.error(f"General error during scraping: {e}")
            results = []  # Ensure an empty list is returned on error
        finally:
            await browser.close()  # Ensure the browser is closed

    return results

if __name__ == "__main__":
    search_query = "family foundations"
    max_pages = 3  # Limit the number of pages to avoid getting blocked.
    asyncio.run(scrape_propublica(search_query, max_pages))

