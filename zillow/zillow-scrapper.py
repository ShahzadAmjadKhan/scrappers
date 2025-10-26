import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import random
import logging
from urllib.parse import urljoin

ZILLOW_SEARCH_URL = "https://www.zillow.com/homes/for_sale/Los-Angeles_rb/"  # Use local city if needed

BLOCKED_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".css", ".woff", ".woff2", ".ttf",".webp")
BLOCKED_DOMAINS = [
    "googletagmanager", "google-analytics", "doubleclick",
    "facebook", "twitter", "linkedin",
    "scorecardresearch", "quantserve", "adsystem",
    "pubmatic", "criteo", "taboola", "outbrain",
    "adsrvr","doubleclick"
]

STEALTH_JS = """
// navigator.webdriver = false
Object.defineProperty(navigator, 'webdriver', {
    get: () => false,
});

// plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3],
});

// languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// user-agent override
Object.defineProperty(navigator, 'userAgent', {
    get: () => navigator.userAgent.replace("Headless", ""),
});

// hairline fix
const elementDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "offsetHeight");
Object.defineProperty(HTMLDivElement.prototype, "offsetHeight", {
  ...elementDescriptor,
  get: function () {
    if (this.id === "modernizr") {
      return 1;
    }
    return elementDescriptor.get.apply(this);
  },
});
"""

def should_block(url: str) -> bool:
    if url.lower().endswith(BLOCKED_EXT):
        return True
    return any(d in url.lower() for d in BLOCKED_DOMAINS)

async def delay(min_delay: float = 0.5, max_delay: float = 1.5) -> None:
    """
    Introduces a random delay to mimic human behavior.
    """
    sleep_time = random.uniform(min_delay, max_delay)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds.")
    await asyncio.sleep(sleep_time)


async def get_context(p, proxy=None):
    """Launches Chrome with stealth patches applied, headless but human-like"""
    args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--start-maximized",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]

    # Pick a random viewport for realism
    viewport = {
        "width": random.randint(1200, 1600),
        "height": random.randint(700, 1000)
    }

    context = await p.chromium.launch_persistent_context(
        user_data_dir="./data-patchright",
        channel="chrome",
        headless=False,      # 👈 safe headless
        no_viewport=True,   # allow window args to control size
        proxy=proxy
        # args=args
    )

    # Inject stealth script
    await context.add_init_script(STEALTH_JS)

    # Create a page and apply viewport
    page = await context.new_page()
    await page.set_viewport_size(viewport)

    await page.route(
        "**/*",
        lambda route: asyncio.create_task(route.abort())
        if should_block(route.request.url)
        else asyncio.create_task(route.continue_())
    )

    # Optional: set a realistic user-agent string
    # await page.set_extra_http_headers({
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #                   "AppleWebKit/537.36 (KHTML, like Gecko) "
    #                   "Chrome/120.0.0.0 Safari/537.36"
    # })

    return context, page

async def extract_listing_details(page, url):
    try:
        await page.goto(url, timeout=1200000, wait_until="domcontentloaded")

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        price_tag = soup.find(attrs={"data-testid": "price"})
        if price_tag:
            price = price_tag.get_text(strip=True)
        else:
            # fallback: find <span> with class containing "price-text"
            span_tag = soup.find("span", class_=lambda c: c and "price-text" in c)
            if span_tag:
                price = span_tag.get_text(strip=True)
            else:
                price = ""

        address = soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else ""

        # all the fact containers
        containers = soup.find_all("div", {"data-testid": "bed-bath-sqft-fact-container"})

        labels = ["beds", "baths", "sqft"]  # expected order
        result = {}

        if containers:
            for i, container in enumerate(containers):
                first_span = container.find("span")
                if first_span and i < len(labels):
                    result[labels[i]] = first_span.get_text(strip=True)
        else:
            # Fallback: look inside desktop-bed-bath-sqft
            desktop_div = soup.find("div", {"data-testid": "desktop-bed-bath-sqft"})
            if desktop_div:
                spans = desktop_div.find_all("span", {"data-testid": "bed-bath-sqft-text__value"})
                for i, span in enumerate(spans):
                    if i < len(labels):
                        result[labels[i]] = span.get_text(strip=True)

        glance_div = soup.find("div", {"aria-label": "At a glance facts"})

        if not glance_div:
            glance_div = soup.find("div", {"data-testid": "at-a-glance"})

        facts = []
        if glance_div:
            for inner_div in glance_div.find_all("div", recursive=False):
                spans = [s.get_text(strip=True) for s in inner_div.find_all("span")]
                if spans:
                    facts.append(" ".join(spans))

        specials = []

        # Find the <h2> with exact text "What's special"
        h2_tag = soup.find("h2", string=lambda t: t and "What's special" in t)

        if h2_tag:
            # Get its first sibling <div>
            sibling_div = h2_tag.find_next_sibling("div")
            if sibling_div:
                # Find <div role="list"> inside
                list_div = sibling_div.find("div", {"role": "list"})
                if list_div:
                    # Find all <span role="listitem">
                    spans = list_div.find_all("span", {"role": "listitem"})
                    specials = [s.get_text(strip=True) for s in spans if s.get_text(strip=True)]

        agent = ""

        agent_div = soup.find("div", {"data-testid": "enhanced-agent-card"})
        if agent_div:
            p_tags = agent_div.find_all("p")
            parts = []
            if len(p_tags) > 0:
                parts.append(p_tags[0].get_text(strip=True))  # agent name
            if len(p_tags) > 1:
                parts.append(p_tags[1].get_text(strip=True))  # agent company
            agent = " | ".join(parts)  # join with separator

        return {
            "url": url,
            "price": price,
            "address": address,
            "beds": result.get("beds", ""),
            "baths": result.get("baths", ""),
            "sqft": result.get("sqft", ""),
            "facts": facts,
            "specials": specials,
            "agent": agent
        }
    except Exception as e:
        print(f"[!] Error extracting {url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_zillow():
    async with async_playwright() as p:
        # persistent context with Chrome
        context, page = await get_context(p, proxy=None)
        # go to Zillow search page
        await page.goto(ZILLOW_SEARCH_URL, timeout=120000, wait_until="domcontentloaded")
        await page.wait_for_selector("ul.photo-cards li article", timeout=120000)

        # --- Infinite Scroll Logic (small steps + auto-stop) ---
        seen_urls = set()
        max_scrolls = 50       # absolute safety cap
        scroll_step = 800      # px per scroll
        pause = 1.5            # seconds to wait between steps
        no_new_limit = 3       # stop if no new cards for N steps
        no_new_count = 0

        last_height = await page.evaluate("() => document.body.scrollHeight")

        for i in range(max_scrolls):
            # extract current property links
            cards = await page.query_selector_all("ul.photo-cards li article a[data-test='property-card-link']")
            current_count = len(seen_urls)

            for a in cards:
                href = await a.get_attribute("href")
                if href:
                    clean_url = urljoin("https://www.zillow.com", href.split("?")[0])
                    seen_urls.add(clean_url)

            # check if we found new URLs
            if len(seen_urls) == current_count:
                no_new_count += 1
            else:
                no_new_count = 0  # reset if new URLs found

            print(f"Step {i+1}: collected {len(seen_urls)} unique listings")

            if no_new_count >= no_new_limit:
                print("🔚 No new listings after several steps, stopping scroll")
                break

            # scroll in small increments
            await page.evaluate(f"window.scrollBy(0, {scroll_step})")
            await asyncio.sleep(pause)

            # check if page height stops growing
            new_height = await page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                print("🔚 Reached bottom of page")
                break
            last_height = new_height

        urls = list(seen_urls)
        print(f"✅ Total URLs collected: {len(urls)}")

        # --- Extract listing details ---
        listings = []
        for link in urls[:50]:  # Limit to 50 for demo/testing
            print(f"Scraping {link}")
            details = await extract_listing_details(page, link)
            if details:
                listings.append(details)

            await delay()  # simulate delay after page load


        await context.close()

        df = pd.DataFrame(
            listings,
            columns=["url", "price", "address", "beds", "baths", "sqft", "facts", "specials", "agent"]
        )
        df.to_excel("zillow_listings.xlsx", index=False, engine="openpyxl")

        print(f"✅ Scraped {len(listings)} listings.")


if __name__ == "__main__":
    asyncio.run(scrape_zillow())
