#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import os
import csv

# Create output directory if it doesn't exist
os.makedirs('ofcom/output', exist_ok=True)

# Function to get all postcode detail page links
def get_postcode_links():
    url = 'https://www.townscountiespostcodes.co.uk/postcodes-in-wales/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links matching the pattern
    links = soup.select('a[href*="-postcode-info"]')
    
    # Extract the href attributes
    href_list = [link.get('href') for link in links]
    
    # Remove duplicates while preserving order
    unique_links = []
    for href in href_list:
        if href not in unique_links:
            unique_links.append(href)
    
    # Convert relative URLs to absolute URLs
    base_url = 'https://www.townscountiespostcodes.co.uk'
    absolute_links = [base_url + href if href.startswith('/') else href for href in unique_links]
    
    # Limit to first 10 links
    return absolute_links[:10]

# Function to extract postcodes from a detail page
def extract_postcodes(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table - using the fact that it's the 7th table in the content div
        tables = soup.select('#content div table')
        if len(tables) < 7:
            print(f"Table not found at {url}")
            return []
        
        target_table = tables[6]  # 7th table (0-indexed)
        
        # Extract postcodes from rows
        postcodes = []
        rows = target_table.select('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.select('td')
            if len(cells) > 1:  # Make sure we have at least 2 cells
                postcode = cells[1].text.strip()  # Changed index from 0 to 1 for second cell
                postcodes.append(postcode)
        
        return postcodes
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Main function
def main():
    # Get all postcode detail page links
    links = get_postcode_links()
    print(f"Found {len(links)} unique postcode area links (limited to first 10)")
    
    # Create a CSV file to save all postcodes
    with open('ofcom/output/wales_postcodes.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Area', 'Postcode'])
        
        # Process each link
        for link in links:
            # Extract the postcode area from the URL
            area = link.split('/')[-2].split('-')[0].upper()
            
            # Get the postcodes for this area
            postcodes = extract_postcodes(link)
            
            # Save to CSV
            for postcode in postcodes:
                csv_writer.writerow([area, postcode])
            
            # Be nice to the server
            time.sleep(1)
    
    print("Scraping completed. Results saved to ofcom/output/wales_postcodes.csv")

if __name__ == "__main__":
    main() 