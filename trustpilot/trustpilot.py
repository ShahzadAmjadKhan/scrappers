import asyncio
from playwright.async_api import async_playwright
import requests
import pandas as pd
import os

async def scrape_category_data(page, category_url):
    # Convert the category URL to JSON URL

    base_json_url = "https://au.trustpilot.com/_next/data/categoriespages-consumersite-2.285.0"
    category_id = category_url.split("/")[-1]
    page_number = 1
    total_pages = 1

    json_url = f"{base_json_url}{category_url}.json?claimed=true&categoryId={category_id}"

    while page_number <= total_pages:
        # Fetch the JSON URL and process business information
        if page_number == 1:
            print(f"Processing businesses from URL: {json_url}")
            response = requests.get(json_url, timeout=10)
        else:
            page_json_url = json_url + "&page=" + str(page_number)
            print(f"Processing businesses from URL: {page_json_url}")
            response = requests.get(page_json_url)

        if response.status_code == 200:
            json_data = response.json()
            # Extract the list of businesses
            businesses = json_data.get('pageProps', {}).get('businessUnits', {}).get('businesses', [])
            total_pages = json_data.get('pageProps', {}).get('businessUnits', {}).get('totalPages', 1)

            # Initialize a list to store the modified business data
            updated_business_data = []

            for business in businesses:
                # Extract business identifying name
                identifying_name = business.get('identifyingName', 'N/A')
                print(f"Processing business: {identifying_name}")
                # Construct the detailed review URL
                detail_url = f"https://au.trustpilot.com/review/{identifying_name}"

                # Create a new page to get the HTML of the detail URL
                detail_page = await page.context.new_page()
                await detail_page.goto(detail_url)
                # Wait for the page to load completely
                await detail_page.wait_for_selector('body')

                # Check if the business pays for extra features
                page_content = await detail_page.content()
                pay_for_feature = "<span>Pays for extra features</span>" in page_content

                # Extract categories and convert to a comma-separated string
                categories = business.get('categories', [])
                category_names = [cat['displayName'] for cat in categories]
                categories_str = ', '.join(category_names)

                # Add the "Pays for Extra Features" and "Claimed" fields to the business data
                business["paysForExtraFeatures"] = pay_for_feature
                business["categories"] = categories_str
                business["claimed"] = True

                # Append the updated business information to the list
                updated_business_data.append(business)

                # Close the detail page
                await detail_page.close()

            # Flatten the JSON data using json_normalize
            if updated_business_data:
                df = pd.json_normalize(updated_business_data)

                # Define the columns to be included in the CSV
                columns = [
                    'businessUnitId',
                    'displayName',                  # Business Name
                    'paysForExtraFeatures',      # Pays for Extra Features Flag
                    'claimed',                      # Claimed Flag
                    'numberOfReviews',              # Number of Reviews
                    'stars',                       # Rating
                    'contact.website',              # Business Website
                    'contact.phone',                # Business Phone
                    'contact.email',                # Business Email
                    'location.address',              # Business Address
                    'location.city',              # Business Address
                    'location.zipCode',              # Business Address
                    'trustScore',                   # TrustScore
                    'categories'
                ]

                # Reorder the DataFrame to match the desired columns
                df = df[columns]

                # Write data to CSV file
                csv_filename = 'output/business_data.csv'
                df.to_csv(csv_filename, mode='a' if os.path.exists(csv_filename) else 'w', header=not os.path.exists(csv_filename), index=False)

                print(f"Business data for category written to '{csv_filename}'")

            page_number += 1
        else:
            print(f"Failed to retrieve data from {json_url}")

async def scrape_all_categories():
    async with async_playwright() as p:
        # Launch a browser instance
        browser = await p.chromium.launch()
        # Create a new browser context
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Trustpilot categories page
        await page.goto("https://au.trustpilot.com/categories")

        # Extract anchor links where parent is a <li> and href starts with /categories/
        li_elements = await page.locator('li a[href^="/categories/"]').all()

        # Extract href attributes from the filtered anchor links
        category_urls = [await li.get_attribute('href') for li in li_elements]

        # Process each category
        for category_url in category_urls[:6]:
            await scrape_category_data(page, category_url)

        # Close the browser
        await page.close()
        await browser.close()

# Run the async function
asyncio.run(scrape_all_categories())
