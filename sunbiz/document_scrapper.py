import asyncio
import json
import logging
import random
from asyncio import Semaphore

from patchright.async_api import async_playwright
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
BATCH_SIZE = 50
CONCURRENT_REQUESTS = 5
DELAY_BETWEEN_REQUESTS = (1, 3)  # seconds random delay between each request
DELAY_BETWEEN_BATCHES = (5, 10)  # seconds random delay between batches

# Set proxy here, or None for no proxy
# Format: "http://username:password@proxyserver:port" or "http://proxyserver:port"
PROXY = None  # Example: "http://user:pass@123.45.67.89:8080"


def scrape_detail(page_content):
    soup = BeautifulSoup(page_content, "html.parser")
    detail = {}

    # Corporation Name
    corp_name_div = soup.select_one("div.detailSection.corporationName")
    if corp_name_div:
        p_tags = corp_name_div.find_all("p")
        if len(p_tags) >= 2:
            corp_type = p_tags[0].get_text(strip=True)
            corp_name = p_tags[1].get_text(strip=True)
            detail["Corporation Name"] = f"{corp_type} {corp_name}"

    # Filing Information
    filing_info_div = soup.select_one("div.detailSection.filingInformation div")
    fields = {
        "Document Number": None,
        "FEI/EIN Number": None,
        "Date Filed": None,
        "State": None,
        "Status": None
    }
    if filing_info_div:
        labels = filing_info_div.find_all("label")
        for label in labels:
            key = label.get_text(strip=True).replace(":", "")
            if key in fields:
                value_span = label.find_next_sibling("span")
                if value_span:
                    fields[key] = value_span.get_text(strip=True)
    detail.update(fields)

    # Principal Address
    principal_div = None
    for div in soup.find_all("div", class_="detailSection"):
        span = div.find("span")
        if span and "Principal Address" in span.text:
            principal_div = div
            break
    if principal_div:
        addr_div = principal_div.find("div")
        if addr_div:
            detail["Principal Address"] = ", ".join(line.strip() for line in addr_div.stripped_strings)

    # Registered Agent Name
    reg_agent_div = None
    for div in soup.find_all("div", class_="detailSection"):
        span = div.find("span")
        if span and "Registered Agent Name" in span.text:
            reg_agent_div = div
            break
    if reg_agent_div:
        spans = reg_agent_div.find_all("span")
        if len(spans) >= 2:
            detail["Registered Agent Name"] = spans[1].get_text(strip=True)

    # Officer/Director Detail - first two officers
    officers = []
    officer_div = None
    for div in soup.find_all("div", class_="detailSection"):
        span = div.find("span")
        if span and "Officer/Director Detail" in span.text:
            officer_div = div
            break

    if officer_div:
        children = list(officer_div.children)
        i = 0
        while i < len(children) and len(officers) < 2:
            child = children[i]
            if getattr(child, "name", None) == "span":
                text = child.get_text(strip=True)
                if text.startswith("Title"):
                    title = text.replace("Title", "").strip()
                    i += 1
                    while i < len(children) and (getattr(children[i], "name", None) == "br" or (hasattr(children[i], "get_text") and not children[i].get_text(strip=True))):
                        i += 1
                    if i >= len(children):
                        break
                    officer_name = None
                    if getattr(children[i], "name", None) == "span":
                        officer_name = children[i].get_text(strip=True)
                    else:
                        officer_name = str(children[i]).strip()
                    officers.append({"Title": title, "Name": officer_name})
            i += 1

    if len(officers) > 0:
        detail["1st Officer Title"] = f"Title {officers[0]['Title']}"
        detail["1st Officer Name"] = officers[0]["Name"]
    if len(officers) > 1:
        detail["2nd Officer Title"] = f"Title {officers[1]['Title']}"
        detail["2nd Officer Name"] = officers[1]["Name"]

    return detail


async def scrape_document(context, doc_num, semaphore):
    async with semaphore:
        page = await context.new_page()
        logger.info(f"Processing document number: {doc_num}")
        try:
            await page.goto("https://search.sunbiz.org/Inquiry/CorporationSearch/ByDocumentNumber", timeout=30000)
            await page.fill('input#SearchTerm', doc_num)
            await page.press('input#SearchTerm', 'Enter')

            try:
                await page.wait_for_selector('h2:text("Detail by Document Number")', timeout=10000)
            except Exception:
                logger.warning(f"No detail found for document number {doc_num}")
                await page.close()
                return {"Searched Document Number": doc_num, "Error": "No detail found"}

            content = await page.content()
            detail = scrape_detail(content)
            detail["Searched Document Number"] = doc_num

            delay = random.uniform(*DELAY_BETWEEN_REQUESTS)
            logger.debug(f"Sleeping {delay:.2f}s after doc {doc_num}")
            await asyncio.sleep(delay)

            await page.close()
            return detail

        except Exception as e:
            logger.error(f"Error processing {doc_num}: {e}")
            await page.close()
            return {"Searched Document Number": doc_num, "Error": str(e)}


async def run_scraper(document_numbers):
    results = []
    semaphore = Semaphore(CONCURRENT_REQUESTS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_args = {}
        if PROXY:
            logger.info(f"Using proxy: {PROXY}")
            context_args["proxy"] = {"server": PROXY}
        context = await browser.new_context(**context_args)

        for i in range(0, len(document_numbers), BATCH_SIZE):
            batch = document_numbers[i : i + BATCH_SIZE]
            logger.info(f"Starting batch {i // BATCH_SIZE + 1} with {len(batch)} documents")

            tasks = [scrape_document(context, doc_num, semaphore) for doc_num in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Save every 100 records
            if len(results) % 100 == 0 or i + BATCH_SIZE >= len(document_numbers):
                with open("scraped_results.json", "w", encoding="utf-8") as outfile:
                    json.dump(results, outfile, indent=2, ensure_ascii=False)
                logger.info(f"Saved {len(results)} records so far.")

            delay = random.uniform(*DELAY_BETWEEN_BATCHES)
            logger.info(f"Batch {i // BATCH_SIZE + 1} done. Sleeping {delay:.2f}s before next batch...")
            await asyncio.sleep(delay)

        await browser.close()

    # Final save at the end
    with open("scraped_results.json", "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=2, ensure_ascii=False)

    logger.info(f"Scraping completed. Total records: {len(results)}")
    logger.info("Results saved to scraped_results.json")


def main():
    with open("documents.txt", "r") as f:
        document_numbers = [line.strip() for line in f if line.strip()]

    asyncio.run(run_scraper(document_numbers))


if __name__ == "__main__":
    main()
