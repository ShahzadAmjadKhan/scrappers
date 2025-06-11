
# Florida Corporation Document Scraper

This Python scraper uses Playwright and BeautifulSoup to extract corporation details from [Florida Sunbiz](https://search.sunbiz.org/Inquiry/CorporationSearch/ByDocumentNumber) based on document numbers.

---

## Features

- Reads a list of document numbers from a text file.
- Searches each document number on Sunbiz.
- Scrapes key details:
  - Corporation Name
  - Document Number
  - FEI/EIN Number
  - Date Filed
  - State
  - Status
  - Principal Address
  - Registered Agent Name
  - Officer Titles and Names
- Supports proxy configuration.
- Uses multiple browser pages concurrently for faster scraping.
- Saves results incrementally every 100 records to `scraped_results.json`.
- Includes logging for progress tracking.
- Batching with configurable delays to avoid blocking.

---

## Requirements

- Python 3.8+
- Playwright
- BeautifulSoup4

Install dependencies:

```bash
pip install playwright beautifulsoup4
python -m playwright install
```

---

## Usage

1. Prepare a text file (e.g., `documents.txt`) with one document number per line.

2. Run the scraper:

```bash
python scraper.py --input documents.txt --proxy http://your.proxy:port
```

- `--input`: Path to your document numbers file (default: `documents.txt`).
- `--proxy`: Optional proxy URL (default: none).

---

## Configuration (in script)

- `BATCH_SIZE`: Number of documents processed per batch (default: 50).
- `CONCURRENT_REQUESTS`: Number of concurrent browser pages (default: 5).
- `DELAY_BETWEEN_REQUESTS`: Delay range (seconds) between individual requests (default: 1-3).
- `DELAY_BETWEEN_BATCHES`: Delay range between batches (default: 5-10).

---

## Output

Scraped results are saved incrementally to `scraped_results.json` as a JSON array of corporation details.

---

## Logging

Logs info about batches, progress, errors, and saves. Check console output during scraping.

---

## Notes

- Be mindful of the website’s usage policies.
- Adjust concurrency and delays to avoid IP blocking.
- Using proxies can help distribute load.

---

## License

MIT License

---
