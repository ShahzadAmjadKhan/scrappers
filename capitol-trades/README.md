# CapitolTrades Politician Trades Scraper

This Python script scrapes politician trade transaction data from [CapitolTrades](https://www.capitoltrades.com/) using Playwright and BeautifulSoup. The data is extracted, parsed, and saved into an Excel file.

## 📦 Features

- Fetches trades from a specified number of days in the past (default: 365 days).
- Supports pagination (default: up to 5 pages).
- Saves the data into an Excel file for easy analysis.
- Logs progress and errors to both console and a log file.

## 🚀 Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`.

## 🔧 Installation

1. **Clone this repository (or download the script)**:
   ```bash
   git clone https://github.com/yourusername/capitoltrades-scraper.git
   cd capitoltrades-scraper
   ```

2. **Create and activate a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

## 📝 Usage

Run the script from the command line:

```bash
python scraper.py [-d DAYS] [-p PAGE]
```

### Arguments:

| Flag | Description | Default |
|------|-------------|---------|
| `-d`, `--days` | Number of days of transaction history to scrape. | 365 |
| `-p`, `--page` | Number of pages to scrape. | 5 |

### Example:

```bash
python scraper.py -d 90 -p 10
```

This command scrapes transactions from the last 90 days, up to 10 pages.

## 📊 Output

The script will generate an Excel file named:

```
politician_trades_<DAYS>d_page1_to_<TOTAL_PAGES>.xlsx
```

## 🐞 Logging

- Console and file logs are stored in `scraper.log`.

## 🤝 Contributions

Feel free to open issues or submit pull requests to improve this scraper!

## 📝 License

MIT License. See `LICENSE` file (if applicable).
