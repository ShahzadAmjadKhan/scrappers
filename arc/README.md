# The Arc Chapters Scraper

This project provides a Python script to scrape contact information for state and local chapters from [thearc.org](https://thearc.org/find-a-chapter/#). The script uses Playwright for browser automation and BeautifulSoup for HTML parsing, saving the results to a CSV file.

## Features
- Scrapes state and local chapter contact info (name, address, phone, email, website)
- Saves data to `arc_chapters_data.csv`
- Configurable number of states and local chapters to process

## Requirements
- Python 3.7+
- [Playwright](https://playwright.dev/python/)
- [pandas](https://pandas.pydata.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

## Installation
1. Clone this repository or download the script.
2. Install dependencies:
   ```bash
   pip install pandas beautifulsoup4 playwright
   playwright install
   ```
   The last command installs browser binaries required by Playwright.

## Usage
Run the script from the command line:

```bash
python scrape_arc.py --num-states 2 --num-local-chapters 5
```

- `--num-states`: Number of states to process (default: 1)
- `--num-local-chapters`: Number of local chapters to process per state (default: 10)

The script will output progress to the console and save the results to `arc_chapters_data.csv` in the current directory.

## Output
The CSV file will contain columns:
- `chapter_name`
- `chapter_type` (State or Local)
- `street_address`
- `city`
- `state`
- `zip_code`
- `phone`
- `email`
- `website`
- `state_name`

## Notes
- The script runs Playwright in headless mode (no browser window).
- If you encounter issues with Playwright, try running `playwright install` again.

## License
MIT License 