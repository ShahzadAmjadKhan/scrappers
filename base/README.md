# Base.gov.pt Contracts Scraper

This Python script scrapes contract data from the [base.gov.pt](https://www.base.gov.pt/Base4/en/) website using Playwright's asynchronous API. It retrieves multiple pages of contract results and saves each page's data into separate CSV files.

---

## Features

- Uses Playwright with Chromium in headful mode (browser window visible).
- Performs an advanced contract search with a blank query to fetch all results.
- Parses JSON responses from the site's API endpoints.
- Handles pagination by sending POST requests for subsequent pages.
- Saves each page's results to a separate CSV file.
- Configurable maximum number of pages to fetch via command-line argument.

---

## Requirements

- Python 3.7+
- Playwright
- asyncio (built-in)
- Other standard libraries (`csv`, `json`, `math`, `argparse`, `urllib`)

### Installation

1. Install Playwright and dependencies:

```bash
pip install playwright
playwright install
```

2. Save the script (e.g., `scrape_base.py`).

---

## Usage

Run the script from the command line:

```bash
python scrape_base.py --max_page 5
```

- `--max_page`: Optional argument to specify the maximum number of pages to fetch (default is 5).

---

## How It Works

1. Opens Chromium browser.
2. Navigates to the advanced contracts search page.
3. Performs a blank search to fetch all contracts.
4. Listens for network responses to the contracts API endpoint.
5. Extracts total records and computes total pages.
6. Saves page 1 results immediately.
7. Iteratively fetches and saves subsequent pages using POST requests.
8. Outputs CSV files named `results_page1.csv`, `results_page2.csv`, etc.

---

## Notes

- The browser runs in non-headless mode (`headless=False`) so you can watch the scraping process.
- CSV files are saved in the current working directory.
- If no data is found for a page, it logs a message but continues gracefully.
- The script gracefully handles exceptions during response processing.

---

## Example Output

```
Total records: 125 | Pages to fetch: 5
Page 1: 25 records.
Data saved to results_page1.csv
Page 2: 25 records.
Data saved to results_page2.csv
...
```

---

## License

This script is provided as-is for educational and personal use.

---

## Contact

For questions or suggestions, feel free to open an issue or contact the author.
