# Mark Cuban Companies Scraper

## 🧠 Overview
This Python script scrapes the [Mark Cuban Companies](https://markcubancompanies.com/) website to collect information about all listed companies.

For each company, it extracts:
- **Brand Name**
- **Company Page URL**
- **Website**
- **Facebook**
- **Instagram**
- **Twitter / X**
- **LinkedIn**

All results are saved into a structured **CSV file** (`companies.csv`).

---

## ⚙️ Requirements

- Python 3.8 or higher  
- Libraries:
  ```bash
  pip install requests beautifulsoup4 lxml
  ```

---

## ▶️ Usage

1. Clone or download this repository.
2. Run the scraper script:

   ```bash
   python mcc_companies_scraper.py
   ```

3. The script will:
   - Visit the main Mark Cuban Companies pages
   - Find all links starting with `https://markcubancompanies.com/companies/`
   - Extract all data fields from each company page
   - Save results to `companies.csv`

---

## 💾 Output Format

The generated CSV file includes the following columns:

| brand_name | company_page | website | facebook | instagram | twitter | linkedin |
|-------------|---------------|----------|-----------|------------|----------|-----------|

Example:

| brand_name | company_page | website | facebook | instagram | twitter | linkedin |
|-------------|---------------|----------|-----------|------------|----------|-----------|
| Simple Sugars | https://markcubancompanies.com/companies/simple-sugars/ | https://www.simplesugarsskincare.com/ | https://www.facebook.com/simplesugars/ | https://www.instagram.com/simplesugars/ |  |  |

---

## 🧩 Notes

- **Rate limiting:** Script includes polite delays between requests (`0.8s`) to avoid overloading the server.
- **Filtering:** Generic Mark Cuban social links are automatically removed:
  - Instagram: `https://www.instagram.com/markcubancompanies/`
  - Facebook: `https://www.facebook.com/markcuban?fref=ts`
- **Error handling:** Automatic retries on network errors (HTTP 429, 500, 502, 503, 504).

---

## ⚖️ Disclaimer

This script is intended for **educational and personal use only**.  
Always review a website’s robots.txt and terms of service before scraping.
