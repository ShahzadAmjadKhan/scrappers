import asyncio
from playwright.async_api import async_playwright
import requests
import csv


async def scrape_category_urls():
    async with async_playwright() as p:
        # Launch a browser instance
        browser = await p.chromium.launch()
        # Create a new browser context and page
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Trustpilot categories page
        await page.goto("https://au.trustpilot.com/categories")

        # Define the XPath to extract the category anchor URLs
        xpath = '//*[@id="__next"]/div/div/main/div/section/div[3]/div/div[*]/div/a'

        # Wait for the category elements to load (if necessary)
        await page.wait_for_selector(xpath)

        # Extract all anchor elements matching the XPath
        category_elements = await page.query_selector_all(xpath)
        # Extract the href attribute (URL) from each anchor element

        category_urls = [await element.get_attribute('href') for element in category_elements]

        # Convert category URLs to JSON URLs
        json_urls = []
        base_json_url = "https://au.trustpilot.com/_next/data/categoriespages-consumersite-2.285.0"

        for url in category_urls:
            # Extract category identifier from the URL
            category_id = url.split("/")[-1]
            # Construct the JSON URL (remove leading slash from `url` if present)
            json_url = f"{base_json_url}{url}.json?claimed=true&categoryId={category_id}"
            json_urls.append(json_url)

        # Fetch each JSON URL and process business information
        for json_url in json_urls:
            response = requests.get(json_url)
            if response.status_code == 200:
                json_data = response.json()
                # Extract the list of businesses
                businesses = json_data.get('pageProps', {}).get('businessUnits', {}).get('businesses', [])
                # Limit to the first 50 businesses
                businesses = businesses[:50]
                # Initialize a list to store business data
                business_data = []

                print(f"Processing businesses from URL: {json_url}\n")

                for business in businesses:
                    # Extract business identifying name
                    identifying_name = business.get('identifyingName', 'N/A')

                    # Check if the business pays for extra features
                    detail_url = f"https://au.trustpilot.com/review/{identifying_name}"

                # Use Playwright to get the final HTML of the detail URL
                    detail_page = await context.new_page()
                    await detail_page.goto(detail_url)
                    # Wait for the page to load completely (adjust the selector as needed)
                    await detail_page.wait_for_selector('body')

                    # Check if the business pays for extra features
                    page_content = await detail_page.content()
                    pay_for_feature = "<span>Pays for extra features</span>" in page_content

                    # Extract the display name, website, and claimed status
                    display_name = business.get('displayName', 'N/A')
                    website = business.get('contact', {}).get('website', 'N/A')
                    claimed = True

                    # Print the extracted information
                    print(f"Business Name: {display_name}")
                    print(f"Website: {website}")
                    print(f"Pays for Extra Features: {pay_for_feature}")
                    print(f"Claimed: {claimed}\n")

                    # Append the extracted information to the list
                    business_data.append({
                        "Business Name": display_name,
                        "Website": website,
                        "Pays for Extra Features": pay_for_feature,
                        "Claimed": claimed
                    })

                    with open('output/business_data.csv', mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=["Business Name", "Website", "Pays for Extra Features", "Claimed"])
                        writer.writeheader()
                        writer.writerows(business_data)

                print("Business data has been written to 'business_data.csv'")

            else:
                print(f"Failed to retrieve data from {json_url}")

        # Close the browser
        await browser.close()

# Run the async function
asyncio.run(scrape_category_urls())
