import asyncio
import csv
import json
from urllib.parse import unquote, urlparse, parse_qs, urlencode, urlunparse
from playwright.async_api import async_playwright

async def run(max_pages=3):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        practitioners_data = []

        async def handle_response(response):
            if response.request.method == "POST" and "https://bams.vba.vic.gov.au/bams/s/sfsites/aura" in response.url:
                try:
                    post_data = response.request.post_data
                    form_data = {}
                    for pair in post_data.split("&"):
                        key, _, value = pair.partition("=")
                        form_data[key] = value

                    message_decoded = unquote(form_data.get("message", "{}"))
                    message_json = json.loads(message_decoded)
                    actions = message_json.get("actions", [])

                    # Check for 'getPractitioners' call
                    is_get_practitioners = False
                    for action in actions:
                        if action.get("params", {}).get("method") == "getPractitioners":
                            is_get_practitioners = True
                            break

                    if not is_get_practitioners:
                        print("Skipping response: Not a getPractitioners call.")
                        return

                    # Parse the JSON response
                    json_body = await response.json()
                    actions_response = json_body.get("actions", [])
                    if (
                            actions_response
                            and isinstance(actions_response, list)
                            and isinstance(actions_response[0], dict)
                    ):
                        return_value = actions_response[0].get("returnValue", {}).get("returnValue", {})
                        if isinstance(return_value, dict):
                            practitioner_list = return_value.get("PractitionerDetailList", [])
                            if practitioner_list:
                                for practitioner in practitioner_list:
                                    practitioners_data.append({
                                        "practitionerName": practitioner.get("practitionerName", ""),
                                        "registrationNumber": practitioner.get("registrationNumber", ""),
                                        "registrationType": practitioner.get("registrationType", ""),
                                        "registrationClass": practitioner.get("registrationClass", ""),
                                        "registrationCategoryWithClass": practitioner.get("registrationCategoryWithClass", ""),
                                        "phoneNumber": practitioner.get("phoneNumber", "")
                                    })
                            else:
                                print("No data found on this page.")
                        else:
                            print(f"Unexpected returnValue format: {type(return_value)}")
                    else:
                        print(f"Unexpected actions format: {type(actions_response)}")
                except Exception as e:
                    print(f"Error parsing response: {e}")



        page.on("response", handle_response)

        # Navigate to page and perform search
        await page.goto("https://bams.vba.vic.gov.au/bams/s/practitioner-search")
        await page.wait_for_selector('button[name="registrationCategory"]')
        await page.click('button[name="registrationCategory"]')
        await page.wait_for_selector('lightning-base-combobox-item')
        await page.locator('lightning-base-combobox-item:has(span[title="Domestic Builder Individual"])').click()
        await page.wait_for_timeout(1000)
        await page.click('button[title="Search"]')
        await page.wait_for_timeout(5000)

        # Find all pagination buttons
        for page_num in range(2, max_pages + 1):  # Start at page 2
            button = await page.query_selector(f'button[title="{page_num}"]')
            if not button:
                print(f"Pagination button for page {page_num} not found.")
                break

            await button.scroll_into_view_if_needed()
            print(f"Clicking page {page_num} button...")
            await button.click()
            await page.wait_for_timeout(5000) # You might want to add better wait logic here
        # Save data
        if practitioners_data:
            keys = [
                "practitionerName",
                "registrationNumber",
                "registrationType",
                "registrationClass",
                "registrationCategoryWithClass",
                "phoneNumber"
            ]
            with open("practitioners.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)
                writer.writeheader()
                writer.writerows(practitioners_data)
            print("Data saved to practitioners.csv.")
        else:
            print("No data found.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run(max_pages=3))
