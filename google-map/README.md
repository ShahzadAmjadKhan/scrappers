# Google Maps Location Scraper

A Python-based web scraper that extracts location information from Google Maps based on user search queries.

## Overview

This tool automates the process of searching and collecting place information from Google Maps, providing a comprehensive list of locations matching the search criteria.

## Features

- Automated location search functionality
- Dynamic content loading through scrolling
- Customizable search parameters
- Clean data formatting
- Console-based output

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd google-map
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the scraper with your location search query:
```bash
python scrapper.py "coffee shops in seattle"
```

The script will:
1. Navigate to Google Maps
2. Enter the search query
3. Scroll through results to load all locations
4. Extract and display place information

### Output Format

Places are displayed in the following format:
```
Places found:
- Starbucks Reserve Roastery Seattle
- Seattle Coffee Works
- etc...
```

## Data Collection

The scraper collects the following information for each location:
- Place name
- Additional details can be configured in the script

## Technologies Used

- **Python**: Core programming language
- **Playwright**: Web automation and dynamic content handling
- **BeautifulSoup4**: HTML parsing
- **requests**: HTTP request handling

## Features

- Headless browser automation
- Dynamic content loading
- Infinite scroll handling
- Search result aggregation
- Error handling

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Page loading failures
- No search results
- Rate limiting
- Invalid search queries

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Google's terms of service before use.
