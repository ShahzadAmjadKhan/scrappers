from playwright.sync_api import sync_playwright
from typing import Dict
import time
import re
import argparse
from bs4 import BeautifulSoup
import pandas as pd

def extract_company_details(page) -> Dict:
    """
    Extract detailed information from a company's page using Playwright + BeautifulSoup.
    """

    details = {
        "website": "",
        "type_of_production": "",
        "co_packer": "",
        "business_availability": "",
        "products_sold": "",
        "methods_of_sale": "",
        "sell_at_farmers_market": "",
        "farmers_market_names": ""
    }

    # Get the HTML content of the entire page
    html = page.evaluate("() => document.documentElement.outerHTML")
    soup = BeautifulSoup(html, "html.parser")

    # --------------------
    # Website
    # --------------------
    contact_info = soup.find('div', class_='contact-info')
    if contact_info:
        website_link = contact_info.find('a', href=lambda x: x and x.startswith('http'))
        if website_link:
            details["website"] = website_link['href']

    # --------------------
    # Extract section by heading title (Products / Growers)
    # --------------------
    def extract_section_fields(section_title: str, field_patterns: Dict[str, str]):
        heading = soup.find('h3', string=re.compile(section_title, re.IGNORECASE))
        if heading:
            section_html = ''
            current = heading.next_sibling
            while current and not (hasattr(current, 'name') and current.name == 'h3'):
                section_html += str(current)
                current = current.next_sibling

            section_soup = BeautifulSoup(section_html, 'html.parser')
            section_text = section_soup.get_text(separator='\n', strip=True)

            for key, pattern in field_patterns.items():
                match = re.search(pattern, section_text, re.IGNORECASE)
                if match:
                    details[key] = match.group(1).strip()

    # --------------------
    # Products section
    # --------------------
    extract_section_fields("products", {
        "type_of_production": r"Type of Production Facilty\?:?\s*(.*)",
        "co_packer": r"Co-?Packer\:[\s]*([^\n]*)",
        "business_availability": r"Business availability\:?[\s]*([^\n]*)",
        "products_sold": r"Products Sold\:\s*(.*)"
    })

    # --------------------
    # Growers section
    # --------------------
    extract_section_fields("growers", {
        "methods_of_sale": r"Methods of Sale for Produce\?:?\s*(.*)",
        "sell_at_farmers_market": r"Sell at Farmers Market\?:?\s*(.*)",
        "farmers_market_names": r"Farmers Market Name\(s\)\:?\s*(.*)"
    })

    return details

def main(limit: int = 5):
    """
    Scrape company information from Got to Be NC website.
    
    Args:
        limit (int): Maximum number of companies to process. Defaults to 5.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the main page
        url = "https://gottobenc.com/find-local/product/?filter=manufactured-food-items"
        page.goto(url)
        
        # Wait for the content to load
        page.wait_for_selector('a[href*="gottobenc.com/member-list/"]')
        
        # Get page content and create BeautifulSoup object
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get all company links
        companies = []
        links = soup.find_all('a', href=lambda x: x and 'gottobenc.com/member-list/' in x)
        
        # Limit the number of links to process
        links = links[:limit]
        print(f"Processing {len(links)} companies (limit: {limit})")
        
        for i, link in enumerate(links, 1):
            company_data = {
                "company_name": link.find('h4').get_text(strip=True),
                "location": link.find('address').get_text(strip=True),
                "href": link['href']
            }
            
            print(f"Processing company {i}/{len(links)}: {company_data['company_name']}")
            
            # Split location into city, state, and zip
            location_parts = company_data["location"].split(", ")
            if len(location_parts) == 2:
                state_zip = location_parts[1].split(" ")
                if len(state_zip) == 2:
                    company_data["location_city"] = location_parts[0]
                    company_data["location_state"] = state_zip[0]
                    company_data["location_zip"] = state_zip[1]
            
            # Visit company page and get additional details
            page.goto(company_data["href"])
            page.wait_for_load_state('networkidle')
            
            # Extract additional details
            details = extract_company_details(page)
            company_data.update(details)
            
            companies.append(company_data)
            time.sleep(1)  # Be nice to the server
        
        browser.close()
        
        # Convert to pandas DataFrame and save to CSV
        if companies:
            df = pd.DataFrame(companies)
            
            # Save to CSV with proper encoding and index=False to avoid row numbers
            file_name = 'companies.csv'
            df.to_csv(file_name, index=False, encoding='utf-8')
            print(f"\nData saved to {file_name}")
            
            # Display summary
            print(f"\nSummary:")
            print(f"Total companies processed: {len(df)}")
            print(f"Companies with websites: {df['website'].notna().sum()}")
            print(f"Unique production types: {df['type_of_production'].nunique()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Got to Be NC manufacturer information')
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of companies to process (default: 5)')
    
    args = parser.parse_args()
    main(limit=args.limit) 