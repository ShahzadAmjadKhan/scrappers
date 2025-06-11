# VBA Practitioner Scraper

This Python script uses Playwright to scrape practitioner details from the VBA Practitioner Search page.

---

## 🚀 Features

✅ Uses Playwright to:
- Open the practitioner search page.
- Select the registration category "Domestic Builder Individual."
- Click the search button.
- Scrape paginated practitioner details from AJAX responses.
- Save results to a CSV file (`practitioners.csv`).

---

## 🛠️ Prerequisites

- Python 3.7 or higher.
- Playwright installed.

---

## 📦 Installation

```bash
# Clone the repository or download the script
pip install -r requirements.txt
python -m playwright install
```

---

## ⚡ Usage

Run the script:

```bash
python scrape.py
```

By default, it scrapes the first **3 pages** of results. You can adjust this by modifying the call to `run()`:

```python
asyncio.run(run(max_pages=5))
```

---

## 🔎 Output

- CSV file: `practitioners.csv`
- Columns:
  - practitionerName
  - registrationNumber
  - registrationType
  - registrationClass
  - registrationCategoryWithClass
  - phoneNumber

---

## ⚠️ Disclaimer

Use this script responsibly. Scraping websites may violate their terms of service. This script is intended for educational and demonstration purposes only.
