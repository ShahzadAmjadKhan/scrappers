# Trading Economics Events Scraper

A Python-based web scraper that extracts economic events and indicators from Trading Economics.

## Overview

This tool automates the collection of economic events and indicators from [Trading Economics](https://tradingeconomics.com), providing comprehensive financial and economic data for analysis.

## Features

- Automated economic event extraction
- Real-time data collection
- Event categorization
- Historical data access
- Data export to JSON

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd trading-economics
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python events_scrapper.py
```

The script will:
1. Connect to Trading Economics
2. Extract current economic events
3. Process event information
4. Save data to `all_events.json`

## Data Collection

The scraper collects the following information for each economic event:

### Event Details
- Event Name
- Date and Time
- Country/Region
- Actual Value
- Forecast Value
- Previous Value
- Impact Level

### Additional Information
- Event Category
- Currency
- Frequency
- Source

## Technologies Used

- **Python**: Core programming language
- **Requests**: HTTP communication
- **BeautifulSoup4**: HTML parsing
- **JSON**: Data storage format

## Features

- Real-time event tracking
- Historical data collection
- Multiple country coverage
- Economic indicator monitoring
- Data validation

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Rate limiting
- Invalid data formats
- Missing event information
- API restrictions

## Data Format

The output JSON file contains structured data with the following format:
```json
{
    "events": [
        {
            "name": "GDP Growth Rate",
            "country": "United States",
            "actual": "2.1%",
            "forecast": "2.0%",
            "previous": "2.2%",
            "date": "2024-01-25 13:30",
            "impact": "High"
        }
    ]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Trading Economics' terms of service before use. 