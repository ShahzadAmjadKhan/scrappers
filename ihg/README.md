# 🏨 IHG Hotels Scraper (Playwright + BeautifulSoup)

This Python script scrapes hotel listings from [IHG Hotels – Alabama](https://www.ihg.com/alabama-united-states), visits each hotel page, and extracts **phone numbers** and **email addresses**.  

It uses **Playwright** for rendering dynamic pages and **BeautifulSoup** for parsing HTML efficiently.  
Works fully in **headless (stealth)** mode.

---

## ⚙️ Features

✅ Scrapes hotel names and detail page URLs  
✅ Visits each hotel page and extracts all phone and email links  
✅ Supports multiple phone numbers or emails (comma-separated)  
✅ Works even in headless mode (with stealth tweaks)  
✅ Allows user to limit how many hotels to scrape (default: 10)  
✅ Exports results to a clean CSV file

---

## 🧰 Requirements

- Python 3.8 or higher  
- Dependencies:
  ```bash
  pip install playwright beautifulsoup4
  playwright install
  ```

---

## 🚀 Usage

1. **Clone or save the script**
   ```bash
   git clone https://github.com/yourusername/ihg-hotels-scraper.git
   cd ihg-hotels-scraper
   ```

2. **Run the script**
   ```bash
   python ihg_hotels_scraper.py
   ```

3. **Enter how many hotels to scrape**
   ```
   Enter number of hotels to scrape (default 10): 20
   ```

4. **Wait for completion**
   Once done, you’ll see:
   ```
   ✅ Saved 20 hotels with contact info to ihg_hotels_alabama_with_contact.csv
   ```

---

## 📄 Output Example

| name | url | phone | email |
|------|-----|--------|--------|
| Holiday Inn Express & Suites Birmingham South - Pelham | /holidayinnexpress/hotels/us/en/pelham/bhmph/hoteldetail | +1 205-987-8888 | info@holidayinn.com |
| Candlewood Suites Mobile-Downtown | /candlewood/hotels/us/en/mobile/mobdw/hoteldetail | +1 251-690-7818, +1 251-690-7819 | contact@candlewood.com |

The output file is automatically saved as:

```
ihg_hotels_alabama_with_contact.csv
```

---

## ⚡ Tips

- If the website doesn’t load in headless mode, switch to visible mode:
  ```python
  browser = p.chromium.launch(headless=False)
  ```
- To scrape more results, increase the input number (e.g. 50, 100).  
- To add concurrency (faster scraping), the script can be upgraded to **async_playwright** or a **multi-tab approach**.

---

## 🧩 File Structure
```
.
├── ihg_hotels_scraper.py     # Main Python scraper
├── ihg_hotels_alabama_with_contact.csv  # Output data
└── README.md                 # This documentation
```

---

## 🛑 Disclaimer
This script is for **educational and research purposes only**.  
Please review [IHG’s Terms of Service](https://www.ihg.com/terms) before scraping or automating their website.
