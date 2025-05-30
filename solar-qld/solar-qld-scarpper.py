import requests
from bs4 import BeautifulSoup
import re
import csv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# URL of the main page
BASE_URL = "https://www.solaranswered.com.au/solar-panel-pricing/qld/"

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def get_suburb_links():
    """Scrape the main page and extract all suburb links."""
    logging.info(f"Fetching main page: {BASE_URL}")
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"Failed to fetch main page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    suburb_links = []
    for a_tag in soup.select('a[href*="https://www.solaranswered.com.au/solar-panel-pricing/qld/"]'):
        href = a_tag['href']
        suburb_name = a_tag.get_text(strip=True)
        if href.rstrip('/') != BASE_URL.rstrip('/'):
            suburb_links.append({'suburb_name': suburb_name, 'url': href})

    logging.info(f"Found {len(suburb_links)} suburb links.")
    return suburb_links

def extract_suburb_data(url):
    """Extract statistics from a suburb page."""
    logging.info(f"Fetching suburb page: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        logging.warning(f"Failed to fetch suburb page {url}, status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    h2_tag = soup.find('h2', class_='wp-block-heading', string=re.compile(r'^Solar Panel Statistics in'))
    if not h2_tag:
        logging.warning(f"No H2 tag found on {url}")
        return None

    h2_text = h2_tag.get_text(strip=True)
    logging.debug(f"Extracted H2 text: {h2_text}")

    postcode_match = re.search(r'(\d{4})$', h2_text)
    postcode = postcode_match.group(1) if postcode_match else None

    number_of_homes = None
    homes_with_solar = None

    p_tag = h2_tag.find_next_sibling('p')
    while p_tag:
        p_text = p_tag.get_text(strip=True)

        if p_text.startswith('Number of homes in'):
            strong_tag = p_tag.find('strong')
            if strong_tag:
                number_of_homes = strong_tag.get_text(strip=True).replace(',', '')
        elif p_text.startswith('Number of homes with solar in'):
            strong_tag = p_tag.find('strong')
            if strong_tag:
                homes_with_solar = strong_tag.get_text(strip=True).replace(',', '')

        p_tag = p_tag.find_next_sibling('p')

    logging.info(f"Extracted data for postcode {postcode}: Homes={number_of_homes}, Homes with solar={homes_with_solar}")
    return {
        'postcode': postcode,
        'number_of_homes': number_of_homes,
        'homes_with_solar': homes_with_solar
    }

def main(limit=10):
    logging.info("Starting scraping process.")
    suburb_links = get_suburb_links()
    if not suburb_links:
        logging.error("No suburb links found. Exiting.")
        return

    results = []
    count = 0
    for suburb in suburb_links:
        if count >= limit:
            logging.info(f"Reached limit of {limit} suburbs. Stopping.")
            break
        data = extract_suburb_data(suburb['url'])
        if data:
            results.append({
                'Suburb Name': suburb['suburb_name'],
                'Postcode': data['postcode'],
                'Number of homes': data['number_of_homes'],
                'Number of homes with solar': data['homes_with_solar']
            })
            count += 1

    if results:
        csv_filename = 'qld_solar_panel_statistics.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Suburb Name', 'Postcode', 'Number of homes', 'Number of homes with solar']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"Data saved to {csv_filename} (scraped {count} suburbs).")
    else:
        logging.warning("No data to save. Exiting.")

if __name__ == '__main__':
    main()
