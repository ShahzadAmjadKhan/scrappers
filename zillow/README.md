# 🏡 Real Estate Scraper (Playwright)

This project is a set of Playwright-based web scrapers to extract **new property listings** from:

- 🇺🇸 [Zillow](https://www.zillow.com)

The goal is to gather **listing title, address, agent name**, and **email addresses** (when available) for properties in specific regions (e.g., Gold Coast, Northern NSW, Los Angeles).

---

## 🚀 Features

- Headless browser automation using [Playwright](https://playwright.dev/)
- Anti-bot protection with **random delays**
- Extracts and structures key property data
- Supports pagination
- Export to CSV or JSON (customizable)

---

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/real-estate-scraper.git
cd real-estate-scraper
```

2. **Create a virtual environment (optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers:**

```bash
playwright install
```

---

## ⚙️ Usage

### 🏠 Scrape Zillow

```bash
python zillow_scraper.py
```
Script scrapes listings and saves results to a CSV (e.g., `zillow_listings.csv`).

---

## 🔧 Customization

### ✨ Delay Simulation

To mimic human behavior and reduce bot detection, the scraper uses random delays:

```python
await delay(page, min_delay=1.0, max_delay=3.0)
```

You can adjust these values in `utils.py` or wherever `delay()` is used.

---

### 📍 Change Regions or Filters

Update search URLs inside each script to target different areas or listing filters.

Example:

```python
base_url = "https://www.zillow.com/homes/los-angeles_rb/"
```

---

## 📝 Output

Data is stored as a list of dictionaries and saved to CSV:

| Title              | Address              | Agent Name     | Email           |
|--------------------|----------------------|----------------|-----------------|
| 3 Bed Apartment... | 123 Main St, CA      | John Doe       | john@agency.com |

---

## 📌 Notes

- Email scraping is limited as many sites do not expose emails publicly.
- Some sites may employ bot protection — the delay function and proper headers help mitigate this.

---

## 🤝 License

MIT License — free for personal and commercial use. Attribution appreciated.

---