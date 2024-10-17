import asyncio
import re
from datetime import datetime, timedelta

from playwright.async_api import async_playwright
import json
from bs4 import BeautifulSoup

BASE_URL = 'https://tradingeconomics.com'

def generate_date_ranges(current_date: datetime):
    # Calculate the start date (2 years ago)
    start_date = current_date - timedelta(days=365 * 1)

    # Initialize a list to hold the date ranges
    date_ranges = []

    # Loop through each month in the past two years
    while start_date < current_date:
        end_date = start_date + timedelta(days=30)
        date_ranges.append((start_date.date(), end_date.date()))
        start_date = end_date + timedelta(days=1)  # Move to the next range starting the day after the current end_date

    return date_ranges

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://tradingeconomics.com/united-states/calendar")
        await page.locator('#calendar').is_visible()

        current_date = datetime.now()
        date_ranges = generate_date_ranges(current_date)

        for from_date, to_date in date_ranges:
            print(f"processing for {from_date} and {to_date}")
            await page.locator('button.btn-calendar').first.click()
            await page.get_by_role('menuitem', name='Custom').click()
            await page.locator('#startDate').fill(str(from_date))
            await page.locator('#endDate').fill(str(to_date))
            await page.get_by_role('button', name='Submit').click()
            await page.wait_for_load_state()

            table_html = await page.locator('#calendar').inner_html()
            soup = BeautifulSoup(table_html, 'html.parser')

            t_heads = soup.select('thead.hidden-head')
            data = []
            event = {}

            for t_head in t_heads:
                first_tr = t_head.find('tr')
                first_th = first_tr.find('th') if first_tr else None

                tbody = t_head.find_next_sibling()
                rows_with_data_url = [tr for tr in tbody.find_all('tr') if tr.get('data-url')]

                for row in rows_with_data_url:
                   event['date'] = first_th.text.strip()
                   tds = row.find_all('td')
                   event['time'] = tds[0].text.strip()
                   event['event'] = tds[4].text.strip()
                   event['actual'] = tds[5].text.strip()
                   event['previous'] = tds[6].text.strip().replace('\n\n               ®', '')
                   event['consensus']= tds[7].text.strip()
                   event['forecast'] = tds[8].text.strip()
                   link = tds[4].find('a')
                   if link:
                       href = link.get('href')
                       event['source_url'] = BASE_URL + href
                       await page.goto(BASE_URL + href)
                       summary_loc = page.locator('#description')
                       if summary_loc:
                        event['summary'] = await summary_loc.inner_text()

                   data.append(event)
                   event = {}

            save_to_json(data)
            await page.goto("https://tradingeconomics.com/united-states/calendar")
            await page.locator('#calendar').is_visible()

        await page.close()
        await browser.close()

def save_to_json(data):
    # Write the data to a JSON file
    with open('all_events.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    asyncio.run(scrape())