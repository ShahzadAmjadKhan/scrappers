# PGA Member Directory Async Scraper

This project is an **asynchronous web scraper** built using **Playwright** and **BeautifulSoup** to extract member details from the [PGA Member Directory](https://directory.pga.org/).  
It logs progress, retries failed requests, and saves results to a CSV file.

---

## 🚀 Features
- Fully **asynchronous** scraping using Playwright.
- Handles **GraphQL API responses** (e.g., `GetMember` queries).
- Smartly merges contact data from multiple endpoints.
- **Logging system** for progress tracking and error handling.
- Saves structured member data into `member_data.csv`.
- Automatically skips non-essential network requests (ads, analytics, etc.).

---

## 📦 Requirements
Install dependencies before running the scraper:

```bash
pip install playwright beautifulsoup4
playwright install
```

---

## ⚙️ Usage
Run the scraper from your terminal:

```bash
python pga_scraper.py
```

You can adjust how many pages to scrape by modifying:

```python
asyncio.run(start_scraping(max_pages=2))
```

This defines how many directory pages are processed.

---

## 🧩 Output
The scraper generates two output files:
- **`member_data.csv`** — contains structured member data.
- **`scraper.log`** — detailed progress and error logs.

---

## 📁 Sample CSV Columns
| Column | Description |
|--------|--------------|
| url | Profile URL |
| Full Name | Member’s full name |
| Member Type/Role | Role or certification |
| Facility Name/Organization | Associated facility |
| City & State | Member location |
| Email | Extracted email (merged from GraphQL if missing) |
| Phone | Facility or public phone |
| Mobile | Mobile number if available |
| Certification | Awards or certifications |

---

## 🧠 Notes
- The scraper automatically merges phone and email data from both `MemberFacilityDirectory` and `GraphQL` endpoints.
- Failed requests retry up to **3 times** before logging as errors.
- Logs are stored both on-screen and in `scraper.log` for easy debugging.

---

## 📜 Example Log Output
```
2025-10-14 17:22:31 [INFO] 📄 Scraping directory page 1 -> https://directory.pga.org/?page=1&...
2025-10-14 17:22:34 [INFO] 🔗 Found 6 unique member links on page
2025-10-14 17:22:35 [INFO] 🔍 Scraping member 999865216 (Attempt 1/3)
2025-10-14 17:22:37 [INFO] ✅ Finished scraping member 999865216
2025-10-14 17:22:39 [INFO] 💾 Data saved to member_data.csv (12 records)
2025-10-14 17:22:39 [INFO] 🏁 Scraping complete!
```

---

## 🧩 License
This project is for **educational and research purposes** only.  
Respect the target website’s **robots.txt** and **terms of use**.
