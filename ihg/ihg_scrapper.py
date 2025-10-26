from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import time

OUTPUT_FILE = "ihg_hotels_alabama_with_contact.csv"
START_URL = "https://www.ihg.com/alabama-united-states"

def extract_contacts(html):
    """Extract all phone and email values from hotel page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select(
        'div[class*="aem-Grid--phone--"] a[href^="tel:"], '
        'div[class*="aem-Grid--phone--"] a[href^="mailto:"]'
    )

    phones, emails = [], []
    for a in links:
        href = a.get("href", "")
        if href.startswith("tel:"):
            phone = href.replace("tel:", "").strip()
            if phone and phone not in phones:
                phones.append(phone)
        elif href.startswith("mailto:"):
            email = href.replace("mailto:", "").strip()
            if email and email not in emails:
                emails.append(email)

    return ", ".join(phones), ", ".join(emails)


def main():
    # 🧩 Ask for number of records (default 10)
    try:
        limit = int(input("Enter number of hotels to scrape (default 10): ") or 10)
    except ValueError:
        limit = 10

    print(f"🔢 Will scrape {limit} hotels.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # Stealth headless mode
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--window-size=1366,768",
            ],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/141.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )

        page = context.new_page()

        print("🌐 Loading main hotel list...")
        page.goto(START_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(3)

        soup = BeautifulSoup(page.content(), "html.parser")
        hotel_links = soup.select('a[class*="cmp-card__title-link"]')

        total = len(hotel_links)
        print(f"🔍 Found {total} hotel links. Limiting to {limit}.\n")

        hotels = []

        for idx, link in enumerate(hotel_links[:limit], 1):
            name = link.get_text(strip=True)
            href = link.get("href", "").strip()

            print(f"[{idx}/{limit}] Visiting: {name} -> {href}")

            try:
                page.goto(href, wait_until="domcontentloaded", timeout=90000)
                time.sleep(3)
                phone, email = extract_contacts(page.content())
            except Exception as e:
                print(f"⚠️ Error loading {href}: {e}")
                phone, email = "", ""

            hotels.append({
                "name": name,
                "url": href,
                "phone": phone,
                "email": email
            })

        browser.close()

    # Save results
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url", "phone", "email"])
        writer.writeheader()
        writer.writerows(hotels)

    print(f"\n✅ Saved {len(hotels)} hotels with contact info to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
