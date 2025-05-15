# ProPublica Nonprofits Scraper

A Python-based web scraper that extracts nonprofit organization data from ProPublica's Nonprofit Explorer database. This tool uses Playwright for browser automation and implements various anti-detection measures for reliable data collection.

## Features

- Asynchronous web scraping using Playwright
- Random user agent rotation to avoid detection
- Configurable delay between requests
- Built-in error handling and logging
- Support for pagination
- Customizable search parameters

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/propublica-nonprofits.git
cd propublica-nonprofits
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Usage

The scraper can be run directly from the command line:

```python
python propublica_scrapper.py
```

To modify the search parameters, you can edit the following variables in the script:
- `search_query`: The search term for nonprofits
- `max_pages`: Maximum number of pages to scrape

## Configuration

The script includes several configurable parameters:

- `USER_AGENTS`: List of user agents to rotate through
- `min_delay` and `max_delay`: Range for random delays between requests
- Logging level and format can be adjusted in the logging configuration

## Error Handling

The scraper includes comprehensive error handling for:
- Network issues
- Navigation timeouts
- Missing elements
- Anti-bot detection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please review and comply with ProPublica's terms of service before use. 