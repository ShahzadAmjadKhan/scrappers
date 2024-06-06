from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

javascript = "results = document.querySelectorAll('div[aria-label=" + '"Results for {}"' + "]'); results[0].scrollTop=results[0].scrollHeight;"


def start(search_text, max_places=200):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com/maps")
        page.get_by_role("textbox", name="Search Google Maps").click()
        page.get_by_role("textbox", name="Search Google Maps").fill(search_text)
        page.get_by_label("Search", exact=True).click()
        page.wait_for_selector("//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]")
        places = page.locator("//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]")
        place_found = places.locator("//a[contains(@href, 'https://www.google.com/maps/place')]").count()
        if place_found > 0:
            print("Iterating places...")
            print("Places found: {}".format(place_found))
            new_place_found = 0
            links = places.locator("//a[contains(@href, 'https://www.google.com/maps/place')]").all()
            while place_found != new_place_found and place_found <= max_places:
                new_place_found = place_found
                page.evaluate(javascript.format(search_text))
                page.wait_for_timeout(1000)
                place_found = places.locator("//a[contains(@href, 'https://www.google.com/maps/place')]").count()
                new_links = places.locator("//a[contains(@href, 'https://www.google.com/maps/place')]").all()[new_place_found:]
                if place_found > new_place_found:
                    links.extend(new_links)
                else:
                    if not places.get_by_text("You've reached the end of the list.").is_visible():
                        page.wait_for_timeout(2000)
                        place_found = places.locator("//a[contains(@href, 'https://www.google.com/maps/place')]").count()
                        new_links = places.locator("//a[contains(@href, 'https://www.google.com/maps/place')]").all()[new_place_found:]
                        if place_found > new_place_found:
                            links.extend(new_links)

                process_place(page, new_links)
                print("Places found: {}".format(place_found))


def process_place(page, links):
    for link in links:
        link.scroll_into_view_if_needed()
        link.click()
        page.wait_for_load_state()
        page.wait_for_selector('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div')
        place_content = page.locator('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div')
        place_html = place_content.inner_html()
        place = BeautifulSoup(place_html, 'html.parser')
        print("Name:" + place.find('h1').text)
        place_content.get_by_role('button', name='Close', exact=True).click()
        page.wait_for_load_state()

if __name__ == "__main__":
    # search_text = input("Enter map search text:")
    search_text = "restaurants"
    print(f"Searching for jobs using query '{search_text}'")
    start(search_text)