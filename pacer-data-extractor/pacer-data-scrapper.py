import asyncio
from playwright.async_api import async_playwright
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


async def scrape():
    async with async_playwright() as p:
        # Launch a browser instance
        browser = await p.chromium.launch(headless=False)
        # Create a new browser context
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Trustpilot categories page
        await page.goto("https://ecf.cand.uscourts.gov/cgi-bin/iqquerymenu.pl?427413")

        await page.locator('#loginForm\:loginName').fill('puttaiahkartik')
        await page.locator('#loginForm\:password').fill('*7Test123')

        await page.get_by_role('button', name='Login').click()

        await page.wait_for_load_state()
        link =  page.get_by_role('link',name='Attorney')
        await link.click()
        await page.wait_for_load_state()

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        # Close the browser
        print(soup.text)
        await page.close()
        await browser.close()

# Run the async function

if __name__ == '__main__':
    asyncio.run(scrape())
