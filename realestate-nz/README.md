# Queenstown Real Estate Scraper

This script scrapes residential property listings from [realestate.co.nz](https://www.realestate.co.nz/residential/sale/central-otago-lakes-district/queenstown) for the Queenstown area.

It uses Playwright for browser automation and BeautifulSoup for HTML parsing. The scraper automatically scrolls the page to load listings, extracts key property information, and saves results to Excel files.

## Features

- Scrolls listings incrementally (simulating user scrolls)
- Extracts key details from each listing, including:
  - Agent info
  - Address
  - Property features (bedrooms, bathrooms, etc.)
  - Capital value and sales method
- Saves results to a separate Excel file per page and a combined Excel file

## Requirements

- Python 3.7+
- Playwright
- BeautifulSoup
- Pandas

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers (only needed once):
   ```bash
   playwright install
   ```

## Usage

Run the script:

```bash
python scraper.py
```

To scrape more pages, update the `main()` call:

```python
asyncio.run(main(max_pages=5))
```

## Output

- `queenstown_page_1.xlsx`, `queenstown_page_2.xlsx`, ...: Per-page results.
- `queenstown_listings.xlsx`: Combined results.