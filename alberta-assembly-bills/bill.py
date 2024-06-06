from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
from pandas import json_normalize


def start():
    with sync_playwright() as p:
        bills = []

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.assembly.ab.ca/assembly-business/assembly-dashboard")
        bill_count = page.locator('//*[@id="accordionBill"]/div[contains(@class, "bill bill")]').count()
        if bill_count > 0:
            bill_locators = page.locator('//*[@id="accordionBill"]/div[contains(@class, "bill bill")]').all()
            for bill_loc in bill_locators:
                readings = []
                bi = BeautifulSoup(bill_loc.inner_html(),'html.parser')
                title = bi.find('a').find_parent().find_next_sibling().text
                details = bi.find('div', {"class": "details"}).find_all_next('div', {"class": "detail"})

                bill = {}
                bill['Title'] = title
                bill['Legislature'] = details[0].find_all_next('div')[1].text
                bill['Sponsor'] = details[1].find_all_next('div')[1].text
                bill['Type'] = details[2].find_all_next('div')[1].text
                bill['Amendments'] = details[3].find_all_next('div')[1].text
                bill['Document'] = details[4].find_all_next('div')[1].find_next('a').attrs.get('href')

                readings_loc = bi.find_all('div', {"class": "b_entry"})
                for index, reading_loc in enumerate(readings_loc):
                    if index != 0:
                        trans_link = reading_loc.find_next('div', {"class": "b_hansard"}).findChild()
                        link = ''
                        if trans_link is not None:
                            link = trans_link.attrs.get('href')

                        reading = {}
                        reading['Reading'] = reading_loc.find_next('span').text
                        reading['Date'] = reading_loc.find_next('div', {"class": "b_date"}).text
                        reading['Status'] = reading_loc.find_next('div', {"class": "b_status"}).text
                        reading['Transcript'] = link
                        readings.append(reading)

                bill['Readings'] = readings
                bills.append(bill)
                print("{} add to CSV".format(bill))

    flattened_data = json_normalize(bills, 'Readings', [
        'Title', 'Legislature', 'Sponsor', 'Type', 'Amendments', 'Document'
    ])

    column_order = ['Title', 'Legislature', 'Sponsor', 'Type', 'Amendments',
                    'Document', 'Reading', 'Date', 'Status', 'Transcript']
    flattened_data = flattened_data[column_order]
    df = pd.DataFrame(flattened_data)
    df.to_csv('bills_readings.csv', index=False)


if __name__ == "__main__":
    # search_text = input("Enter map search text:")
    start()