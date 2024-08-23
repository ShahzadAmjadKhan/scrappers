import json
from playwright.sync_api import sync_playwright

def scrape_dentists():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Initialize a list to hold all dentists data
        all_dentists = []

        # Function to scrape data from the current page
        def scrape_current_page(specialty_name):
            # Wait for the sections to load
            page.wait_for_selector('#dentistSearchResults section.row')

            # Use Playwright to get all section elements
            sections = page.query_selector_all('#dentistSearchResults section.row')

            for section in sections:
                # Extract data using Playwright
                name = section.query_selector('h2').inner_text().strip()

                # Registration number (optional)
                reg_number_element = section.query_selector('dt:text("Registration Number:") + dd')
                registration_number = reg_number_element.inner_text().strip() if reg_number_element else ''

                # Status (optional)
                status_element = section.query_selector('dt:text("Status:") + dd')
                status = status_element.inner_text().strip() if status_element else ''

                # Primary practice address (optional)
                address_elements = section.query_selector_all('address span')
                primary_practice_address = ', '.join([element.inner_text().strip() for element in address_elements]) if address_elements else ''

                # Phone number (optional)
                phone_element = section.query_selector('dt:text("Phone:") + dd')
                phone = phone_element.inner_text().strip() if phone_element else ''

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

        # Go to the initial page
        page.goto("https://www.rcdso.org/find-a-dentist")

        # Get all options in the dropdown
        options = page.query_selector_all('select[name="MbrSpecialty"] option')

        # Loop through each option
        for index in range(len(options)):
            # Re-fetch the options after each navigation to avoid stale element reference
            options = page.query_selector_all('select[name="MbrSpecialty"] option')
            option = options[index]

            value = option.get_attribute('value')
            specialty_name = option.inner_text().strip()

            if not value:
                continue  # Skip the empty/default option

            # Select the option
            page.select_option('select[name="MbrSpecialty"]', value)

            # Click the search button
            page.click('text="Search"')

            # Wait for the search results to load
            page.wait_for_selector('text=" Search Result(s)"')

            # Scrape data from the current page, passing the specialty name
            scrape_current_page(specialty_name)

            # Go back to the initial search page
            page.goto("https://www.rcdso.org/find-a-dentist")

        # Write the data to a JSON file
        with open('all_dentists.json', 'w') as f:
            json.dump(all_dentists, f, indent=4)

        # Close the browser
        browser.close()

if __name__ == "__main__":
    scrape_dentists()
