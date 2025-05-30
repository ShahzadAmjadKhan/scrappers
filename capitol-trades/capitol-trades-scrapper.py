import argparse
import logging
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

def extract_total_pages(html: str) -> int:
    """Extract total number of pages from the HTML pagination info."""
    soup = BeautifulSoup(html, "html.parser")
    p_tags = soup.find_all("p")
    for p in p_tags:
        # Look for "Page X of <b>Y</b>" or similar patterns
        text = str(p)
        match = re.search(r'of\s*<b>(\d+)</b>', text)
        if match:
            return int(match.group(1))
    return 1  # default to 1 if not found

def extract_trades_from_html(html: str):
    """Extract trade rows from page HTML and return list of dicts."""
    soup = BeautifulSoup(html, "html.parser")
    tbody = soup.find("tbody")
    trades_data = []

    if not tbody:
        logging.error("No table body found on this page!")
        return trades_data

    rows = tbody.find_all("tr")
    logging.info(f"Found {len(rows)} rows on current page.")

    for idx, row in enumerate(rows, start=1):
        cols = row.find_all("td")
        try:
            # Politician Name and Party (column index 0)
            name_col = cols[0]
            name_tag = name_col.find("h2", class_="politician-name")
            name = name_tag.text.strip() if name_tag else "N/A"

            party_tag = name_col.find("span", class_=lambda x: x and "party" in x)
            party = party_tag.text.strip() if party_tag else "N/A"

            # Ticker Symbol (column index 1)
            ticker_col = cols[1]
            ticker_tag = ticker_col.find("span", class_=lambda x: x and "issuer-ticker" in x)
            ticker = ticker_tag.text.strip() if ticker_tag else "N/A"

            # Transaction Date (column index 3)
            date_col = cols[3]
            day_div = date_col.find("div", class_="text-size-3 font-medium")
            year_div = date_col.find("div", class_="text-size-2 text-txt-dimmer")
            if day_div and year_div:
                day_str = day_div.text.strip()
                year_str = year_div.text.strip()
                date_str = f"{day_str} {year_str}"
                transaction_date = datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")
            else:
                transaction_date = "N/A"

            # Transaction Type (column index 6)
            tx_col = cols[6]
            tx_type_tag = tx_col.find("span", class_=lambda x: x and "tx-type" in x)
            transaction_type = tx_type_tag.text.strip() if tx_type_tag else "N/A"

            # Reported Amount Range (column index 7)
            amt_col = cols[7]
            range_tag = amt_col.find("span", class_="q-field trade-size")
            amount_range = range_tag.text.strip() if range_tag else "N/A"

            trades_data.append({
                "Politician Name": name,
                "Party": party,
                "Ticker Symbol": ticker,
                "Transaction Date": transaction_date,
                "Transaction Type": transaction_type,
                "Reported Amount Range": amount_range
            })

            logging.debug(f"Row {idx} processed: {name}, {ticker}, {transaction_date}")

        except Exception as e:
            logging.warning(f"Error processing row {idx}: {e}")
            continue

    return trades_data

def scrape_politician_trades(days: int = 365, total_page: int = 5):
    """
    Scrapes politician trades from CapitolTrades for the given number of days,
    starting from start_page up to last page.
    """
    start_page = 1
    base_url = f"https://www.capitoltrades.com/trades?txDate={days}d"
    logging.info(f"Starting scraping process for {days} days, starting from page {start_page}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # First request to get total pages
        first_page_url = f"{base_url}&page=1"
        logging.info(f"Loading first page to detect total pages: {first_page_url}")
        page.goto(first_page_url)
        page.wait_for_selector("tbody", timeout=10000)
        first_page_html = page.content()

        total_pages = extract_total_pages(first_page_html)
        logging.info(f"Total pages detected: {total_pages}")
        if total_page < total_pages:
            total_pages = total_page

        all_trades = []

        # Loop through pages from start_page to total_pages
        for current_page in range(start_page, total_pages + 1):
            url = f"{base_url}&page={current_page}"
            logging.info(f"Scraping page {current_page} / {total_pages}: {url}")
            if current_page != start_page:
                page.goto(url)
                try:
                    page.wait_for_selector("tbody", timeout=10000)
                except Exception as e:
                    logging.error(f"Timeout waiting for table on page {current_page}: {e}")
                    continue

            html_content = page.content()
            trades = extract_trades_from_html(html_content)
            logging.info(f"Extracted {len(trades)} trades from page {current_page}.")
            all_trades.extend(trades)

        browser.close()
        logging.info("Browser closed.")

    if all_trades:
        df = pd.DataFrame(all_trades)
        output_file = f"politician_trades_{days}d_page{start_page}_to_{total_pages}.xlsx"
        df.to_excel(output_file, index=False)
        logging.info(f"Saved {len(all_trades)} trades to {output_file}")
    else:
        logging.warning("No trades extracted; no file created.")

def main():
    parser = argparse.ArgumentParser(description="Fetch politician trade transaction data with pagination.")
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=365,
        help="Number of days for txDate (default: 365)"
    )
    parser.add_argument(
        "-p", "--page",
        type=int,
        default=5,
        help="Total Pages to be extracted (default: 5)"
    )
    args = parser.parse_args()

    scrape_politician_trades(days=args.days, total_page=args.page)

if __name__ == "__main__":
    main()
