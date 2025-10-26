import asyncio
import random
import csv
import json
import re
import logging
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Blocked URLs ---
BLOCKED_EXT = (".png", ".jpg", ".jpeg", ".gif", ".css", ".woff", ".woff2", ".ttf", ".webp")
BLOCKED_DOMAINS = [
    "googletagmanager", "google-analytics", "doubleclick",
    "facebook", "twitter", "linkedin",
    "scorecardresearch", "quantserve", "adsystem",
    "pubmatic", "criteo", "taboola", "outbrain",
    "adsrvr", "doubleclick"
]


def should_block(url: str) -> bool:
    if url.lower().endswith(BLOCKED_EXT):
        return True
    return any(d in url.lower() for d in BLOCKED_DOMAINS)


async def scrape_member_detail(context, link, retries=3):
    """Scrapes member details from both MemberFacilityDirectory and GraphQL endpoints."""
    member_id_match = re.search(r'/member/detail/(\d+)', link)
    if not member_id_match:
        logger.warning(f"Could not extract member ID from link: {link}")
        return {}

    member_id = member_id_match.group(1)
    endpoint = f"/indexes/MemberFacilityDirectory/{member_id}"

    member_detail = {
        'url': link,
        'Full Name': '',
        'Member Type/Role': '',
        'Facility Name/Organization': '',
        'City & State': '',
        'Email': '',
        'Phone': '',
        'Mobile': '',
        'Certification': '',
    }

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🔍 Scraping member {member_id} (Attempt {attempt}/{retries})")
            detail_page = await context.new_page()

            await detail_page.route("**/*", lambda route: asyncio.create_task(
                route.abort() if should_block(route.request.url) else route.continue_()
            ))

            async def handle_response(response):
                try:
                    url = response.url
                    if endpoint in url and response.status == 200:
                        data = await response.json()
                        member_detail['Full Name'] = data.get('profile_name', '')
                        member_detail['Member Type/Role'] = data.get('job_title', '')
                        member_detail['Facility Name/Organization'] = data.get('facility_name', '')
                        member_detail['City & State'] = f"{data.get('city', '')}, {data.get('state', '')}"
                        member_detail['Email'] = data.get('email', '') or ''
                        member_detail['Mobile'] = data.get('mobile', '') or ''
                        member_detail['Phone'] = data.get('phone', '') or ''
                        awards = data.get('awards', [])
                        member_detail['Certification'] = ', '.join(
                            [award.get('description', '') for award in awards]
                        )

                    # ✅ GraphQL "GetMember"
                    elif "https://developers.pga.org/graphql" in url and response.status == 200:
                        req = response.request
                        post_data = req.post_data
                        if post_data and '"operationName":"GetMember"' in post_data:
                            graphql_data = await response.json()
                            member_data = graphql_data.get("data", {}).get("memberByUid", {})
                            if member_data:
                                facility = member_data.get("primaryFacility", {}) or {}
                                phone_number = facility.get("phoneNumber", "")
                                public_email = member_data.get("publicEmail", "")

                                existing_phone = str(member_detail.get("Phone") or "").strip()
                                existing_email = str(member_detail.get("Email") or "").strip()

                                if phone_number:
                                    if existing_phone and phone_number not in existing_phone:
                                        member_detail["Phone"] = f"{existing_phone}, {phone_number}"
                                    else:
                                        member_detail["Phone"] = phone_number or existing_phone

                                if public_email:
                                    if existing_email and public_email not in existing_email:
                                        member_detail["Email"] = f"{existing_email}, {public_email}"
                                    else:
                                        member_detail["Email"] = public_email or existing_email

                except Exception as e:
                    logger.error(f"Error handling response for {url}: {e}")

            detail_page.on("response", handle_response)

            await detail_page.goto(link, timeout=60000, wait_until="load")
            await asyncio.sleep(random.uniform(1.0, 2.0))
            await detail_page.close()
            logger.info(f"✅ Finished scraping member {member_id}")
            return member_detail

        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt} failed for {link}: {e}")
            await asyncio.sleep(2)

    logger.error(f"❌ Failed to scrape member {member_id} after {retries} attempts")
    return member_detail


async def get_member_links(page):
    """Extracts all member profile links from a directory page."""
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        if "/member/detail/" in a['href']:
            links.append(f"https://directory.pga.org{a['href']}")
    unique_links = list(set(links))
    logger.info(f"🔗 Found {len(unique_links)} unique member links on page")
    return unique_links


async def write_data_to_csv(data, filename='member_data.csv'):
    """Saves scraped data to CSV."""
    fieldnames = ['url', 'Full Name', 'Member Type/Role', 'Facility Name/Organization', 'City & State',
                  'Email', 'Phone', 'Mobile', 'Certification']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    logger.info(f"💾 Data saved to {filename} ({len(data)} records)")


async def start_scraping(max_pages=3):
    """Main scraping controller."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 800})

        all_data = []

        for page_num in range(1, max_pages + 1):
            url = f"https://directory.pga.org/?refinementList%5BprogramHistory.programCode%5D=&refinementList%5Bmember_type_label%5D%5B0%5D=MB&refinementList%5Bfacility_type_label%5D=&page={page_num}&configure%5BhitsPerPage%5D=6&configure%5Bfacets%5D%5B0%5D=_geoloc&configure%5Bfacets%5D%5B1%5D=zip&query="
            logger.info(f"📄 Scraping directory page {page_num} -> {url}")
            page = await context.new_page()

            await page.route("**/*", lambda route: asyncio.create_task(
                route.abort() if should_block(route.request.url) else route.continue_()
            ))
            await page.goto(url, timeout=60000, wait_until="load")

            links = await get_member_links(page)
            await page.close()

            if not links:
                logger.warning(f"⚠️ No member links found on page {page_num}")
                continue

            # Limit concurrent tasks
            semaphore = asyncio.Semaphore(5)

            async def bounded_scrape(link):
                async with semaphore:
                    return await scrape_member_detail(context, link)

            results = await asyncio.gather(*[bounded_scrape(link) for link in links])
            all_data.extend(results)

        await write_data_to_csv(all_data)
        await browser.close()
        logger.info("🏁 Scraping complete!")


if __name__ == "__main__":
    asyncio.run(start_scraping(max_pages=15))
