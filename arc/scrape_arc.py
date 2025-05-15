import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import argparse

async def setup_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    return playwright, browser, context

async def get_state_chapters(context):
    # Navigate to the main page
    page = await context.new_page()
    await page.goto("https://thearc.org/find-a-chapter/#")
    await page.wait_for_load_state("networkidle")
    
    # Find the select element
    select_element = await page.query_selector(".chosen-select")
    options = await select_element.query_selector_all("option")
    
    # Extract state URLs and names
    state_data = []
    for option in options:
        value = await option.get_attribute("value")
        if value:  # Skip empty values
            text = await option.text_content()
            state_data.append({
                "state": text.strip(),
                "url": value  # Use the complete URL from the option value
            })
    
    await page.close()
    return state_data

async def extract_contact_info(context, url):
    page = await context.new_page()
    try:
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        
        # Get the complete page HTML first
        full_html = await page.content()
        full_soup = BeautifulSoup(full_html, 'html.parser')
        
        # Wait for the contact information section to load
        contact_div = await page.wait_for_selector('//*[@id="main"]/div[2]/div[2]/main/div/div[2]')
        
        # Get the HTML content for contact info
        content = await contact_div.inner_html()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the textblock section that contains contact info
        textblock = soup.find("section", class_="av_textblock_section")
        if not textblock:
            return None
            
        # Get all paragraphs
        paragraphs = textblock.find_all("p")
        if len(paragraphs) < 4:  # We expect at least 4 paragraphs
            return None
            
        # Extract data from paragraphs
        chapter_name = paragraphs[0].text.strip()
        
        # Extract address from second paragraph
        address = paragraphs[1].text.strip()
        address_parts = address.split(',')
        if len(address_parts) >= 3:
            street_address = address_parts[0].strip()
            city = address_parts[1].strip()
            state_zip = address_parts[2].strip().split()
            state = state_zip[0]
            zip_code = ' '.join(state_zip[1:])
        else:
            street_address = address
            city = ""
            state = ""
            zip_code = ""
        
        # Extract phone from third paragraph
        phone = paragraphs[2].text.strip()
        phone = phone.replace('Phone:', '').strip()
        
        # Extract email from fourth paragraph
        email = paragraphs[3].text.strip()
        email = email.replace('Email:', '').strip()
        
        # Extract website URL
        website = ""
        website_link = soup.find("a", class_="avia-button")
        if website_link:
            website = website_link.get('href', '')
        
        # Get local chapters from full page HTML
        chapters_div = full_soup.find("div", class_="local_chapters_list")
        if chapters_div:
            chapter_links = chapters_div.find_all("a", href=re.compile(r"https://thearc.org/chapter/"))
            local_chapters = [{"name": link.text.strip(), "url": link["href"]} for link in chapter_links]
        else:
            local_chapters = []
        
        return {
            "chapter_name": chapter_name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "phone": phone,
            "email": email,
            "website": website,
            "local_chapters": local_chapters  # Keep this for processing but won't be in CSV
        }
    except Exception as e:
        print(f"Error extracting data from {url}: {str(e)}")
        return None
    finally:
        await page.close()

async def main(num_states=1, num_local_chapters=1):
    playwright, browser, context = await setup_browser()
    try:
        # Get state chapters
        state_chapters = await get_state_chapters(context)
        
        # Limit the number of states to process
        state_chapters = state_chapters[:num_states]
        print(f"Processing {len(state_chapters)} states...")
        
        # List to store all chapter data
        all_chapter_data = []
        
        # Process each state chapter
        for state_info in state_chapters:
            print(f"Processing {state_info['state']}...")
            chapter_data = await extract_contact_info(context, state_info['url'])
            
            if chapter_data:
                # Add state chapter data
                state_chapter = chapter_data.copy()
                state_chapter['state_name'] = state_info['state']
                state_chapter['chapter_type'] = 'State'
                # Remove local_chapters from the data to be saved
                state_chapter.pop('local_chapters', None)
                all_chapter_data.append(state_chapter)
                
                # Process limited number of local chapters
                local_chapters = chapter_data.get('local_chapters', [])[:num_local_chapters]
                print(f"Found {len(chapter_data.get('local_chapters', []))} local chapters, processing up to {num_local_chapters}")
                
                for local_chapter in local_chapters:
                    print(f"Processing local chapter: {local_chapter['name']}...")
                    local_data = await extract_contact_info(context, local_chapter['url'])
                    if local_data:
                        local_data['state_name'] = state_info['state']
                        local_data['chapter_type'] = 'Local'
                        # Remove local_chapters from the data to be saved
                        local_data.pop('local_chapters', None)
                        all_chapter_data.append(local_data)
        
        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(all_chapter_data)
        # Ensure chapter_type is the second column after chapter_name
        columns = ['chapter_name', 'chapter_type'] + [col for col in df.columns if col not in ['chapter_name', 'chapter_type', 'local_chapters']]
        df = df[columns]
        df.to_csv('arc_chapters_data.csv', index=False)
        print(f"Data has been saved to arc_chapters_data.csv (Processed {len(state_chapters)} states with up to {num_local_chapters} local chapters each)")
        
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape The Arc chapter data')
    parser.add_argument('--num-states', type=int, default=1,
                      help='Number of states to process (default: 1)')
    parser.add_argument('--num-local-chapters', type=int, default=10,
                      help='Number of local chapters to process per state (default: 10)')
    args = parser.parse_args()
    
    print(f"Starting scraper to process {args.num_states} states with up to {args.num_local_chapters} local chapters each...")
    asyncio.run(main(args.num_states, args.num_local_chapters)) 