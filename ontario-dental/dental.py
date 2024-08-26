import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_dentists():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Initialize a list to hold all dentists data
        all_dentists = []

        # Go to the initial page and parse options with BeautifulSoup
        page.goto("https://www.rcdso.org/find-a-dentist")
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Get all options in the dropdown using BeautifulSoup
        options = soup.select('select[name="MbrSpecialty"] option')

        # Loop through each option
        for option in options:
            value = option.get('value')
            specialty_name = option.get_text(strip=True)

            if not value:
                continue  # Skip the empty/default option

            # Use Playwright to select the option and perform actions
            page.select_option('select[name="MbrSpecialty"]', value)

            # Click the search button
            page.click('text="Search"')

            # Wait for the search results to load
            page.wait_for_selector('text="Search Result(s)"')

            # Scrape data from the current page using Playwright and BeautifulSoup
            scrape_current_page(page, specialty_name, all_dentists)

            # Go back to the initial search page
            page.goto("https://www.rcdso.org/find-a-dentist")

        # Write the data to a JSON file
        with open('all_dentists.json', 'w') as f:
            json.dump(all_dentists, f, indent=4)

        # Close the browser
        browser.close()

def scrape_current_page(page, specialty_name, all_dentists):
    # Wait for the sections to load
    page.wait_for_selector('#dentistSearchResults section.row')

    # Use Playwright to get the outer HTML of the entire search results
    results_html = page.inner_html('#dentistSearchResults')

    # Use BeautifulSoup to parse the HTML content retrieved by Playwright
    soup = BeautifulSoup(results_html, 'html.parser')

    # Find all the dentist sections
    dentist_sections = soup.select('section.row')

    for section in dentist_sections:
        # Extract the data
        name = section.find('h2').get_text(strip=True)

        # Registration number (optional)
        reg_number_tag = section.find('dt', text='Registration Number:')
        registration_number = reg_number_tag.find_next('dd').get_text(strip=True) if reg_number_tag else ''

        # Status (optional)
        status_tag = section.find('dt', text='Status:')
        status = status_tag.find_next('dd').get_text(strip=True) if status_tag else ''

        # Primary practice address (optional)
        address_tag = section.find('address')
        primary_practice_address = ', '.join([span.get_text(strip=True) for span in address_tag.find_all('span')]) if address_tag else ''

        # Phone number (optional)
        phone_tag = section.find('dt', text='Phone:')
        phone = phone_tag.find_next('dd').get_text(strip=True) if phone_tag else ''

        # Create a dictionary for each dentist
        dentist = {
            "Name": name,
            "Registration number": registration_number,
            "Status": status,
            "Primary practice address": primary_practice_address,
            "Phone": phone,
            "Specialty": specialty_name
        }

        # Add the dictionary to the list
        all_dentists.append(dentist)

if __name__ == "__main__":
    scrape_dentists()
