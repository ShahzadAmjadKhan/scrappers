# D&B Business Directory Scraper

This project is a Python-based web scraper for extracting business information from the Dun & Bradstreet (D&B) Business Directory using Playwright. It is designed to mimic human browsing behavior and includes anti-bot measures such as random delays and user-agent rotation.

## Features
- Scrapes business name, address, phone, and website from D&B search results
- Handles pagination and extracts data from multiple pages
- Uses Playwright for robust browser automation
- Randomizes user agents and introduces delays to reduce the risk of blocking
- Logs progress and errors for easier debugging

## Requirements
- Python 3.7+
- [Playwright for Python](https://playwright.dev/python/)
- asyncio

## Installation
1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd dnb
   ```
2. Install dependencies:
   ```bash
   pip install playwright
   playwright install
   ```

## Usage
Run the scraper with the default search query ("restaurants in New York") and a page limit:

```bash
python scrapper.py
```

To customize the search query or number of pages, modify the following lines at the bottom of `scrapper.py`:
```python
search_query = "restaurants in New York"
max_pages = 3
```

## Output
The script prints the extracted business data to the console. Each business is shown as a dictionary with keys: `name`, `full_address`, `phone`, and `website`.

## Notes & Troubleshooting
- The scraper opens a visible browser window (`headless=False`). You can change this to `True` in `scrapper.py` for headless operation.
- If you encounter errors related to selectors, the D&B website structure may have changed. Update the CSS selectors in `scrapper.py` accordingly.
- Excessive scraping may result in temporary blocks. Use reasonable `max_pages` and delays.
- For best results, use a stable internet connection and avoid running multiple scrapers in parallel.

## License
This project is for educational and personal use only. Scraping websites may violate their terms of service. Use responsibly. 