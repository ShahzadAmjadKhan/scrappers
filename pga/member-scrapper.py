from patchright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import asyncio
import random
import csv
import time
import json
import re

BLOCKED_EXT = (".png", ".jpg", ".jpeg", ".gif", ".css", ".woff", ".woff2", ".ttf",".webp")
BLOCKED_DOMAINS = [
    "googletagmanager", "google-analytics", "doubleclick",
    "facebook", "twitter", "linkedin",
    "scorecardresearch", "quantserve", "adsystem",
    "pubmatic", "criteo", "taboola", "outbrain",
    "adsrvr","doubleclick"
]

def should_block(url: str) -> bool:
    if url.lower().endswith(BLOCKED_EXT):
        return True
    return any(d in url.lower() for d in BLOCKED_DOMAINS)

def scrape_member_detail(context, link, retries=3):
    member_id_match = re.search(r'/member/detail/(\d+)', link)
    if not member_id_match:
        print(f"Could not extract member ID from link: {link}")
        return {}

    member_id = member_id_match.group(1)
    endpoint = f"/indexes/MemberFacilityDirectory/{member_id}"

    member_detail = {
        'Full Name': '',
        'Member Type/Role': '',
        'Facility Name/Organization': '',
        'City & State': '',
        'Email': '',
        'Phone': '',
        'Certification': ''
    }

    for attempt in range(1, retries + 1):
        try:
            def handle_response(response):
                if endpoint in response.url and response.status == 200:
                    try:
                        data = json.loads(response.body())
                        member_detail['Full Name'] = data.get('profile_name', '')
                        member_detail['Member Type/Role'] = data.get('job_title', '')
                        member_detail['Facility Name/Organization'] = data.get('facility_name', '')
                        member_detail['City & State'] = f"{data.get('city', '')}, {data.get('state', '')}"
                        member_detail['Email'] = data.get('email', '')
                        member_detail['Mobile'] = data.get('mobile', '')
                        member_detail['Phone'] = data.get('phone', '')
                        awards = data.get('awards', [])
                        member_detail['Certification'] = ', '.join([award.get('description', '') for award in awards])
                    except Exception as e:
                        print(f"Error parsing response: {e}")

            context.on("response", handle_response)

            detail_page = context.new_page()
            detail_page.route("**/*",
                              lambda route: route.abort()
                              if should_block(route.request.url)
                              else route.continue_())
            detail_page.goto(link, timeout=60000, wait_until="load")
            detail_page.close()

            return member_detail

        except Exception as e:
            print(f"Attempt {attempt} failed for {link}: {e}")
            time.sleep(3)

    print(f"Failed to scrape after {retries} attempts: {link}")
    return member_detail

def get_member_links(page):
    soup = BeautifulSoup(page.content(), 'html.parser')
    member_links = []
    for a in soup.find_all('a', href=True):
        if "/member/detail/" in a['href']:
            full_link = f"https://directory.pga.org{a['href']}"
            member_links.append(full_link)
    return member_links

def write_data_to_csv(data_list, filename='member_data.csv'):
    fieldnames = ['url', 'Full Name', 'Member Type/Role', 'Facility Name/Organization', 'City & State', 'Email', 'Phone', 'Mobile', 'Certification']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

def start_scraping(context, max_pages=5):
    all_member_data = []

    for page_number in range(1, max_pages + 1):
        url = f"https://directory.pga.org/?refinementList%5BprogramHistory.programCode%5D=&refinementList%5Bmember_type_label%5D%5B0%5D=MB&refinementList%5Bfacility_type_label%5D=&page={page_number}&configure%5BhitsPerPage%5D=6&configure%5Bfacets%5D%5B0%5D=_geoloc&configure%5Bfacets%5D%5B1%5D=zip&query="
        page = context.new_page()
        print(f"Navigating to page {page_number}...")
        page.route(
            "**/*",
            lambda route: route.abort()
            if should_block(route.request.url)
            else route.continue_())

        page.goto(url, wait_until="load", timeout=60000)

        member_links = get_member_links(page)
        print(f"Found {len(member_links)} member detail links on page {page_number}.")

        for link in member_links:
            print(f"Processing: {link}")
            member_detail = scrape_member_detail(context, link)
            time.sleep(random.uniform(0.5, 1.5))
            member_detail['url'] = link
            all_member_data.append(member_detail)

        page.close()

    write_data_to_csv(all_member_data)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})

        start_scraping(context, max_pages=2)

        browser.close()

if __name__ == "__main__":
    main()
