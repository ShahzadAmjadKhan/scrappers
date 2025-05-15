# Landmodo Real Estate Scraper

A Python-based web scraper that extracts property listings and detailed information from Landmodo.com real estate platform.

## Overview

This tool automates the collection of real estate listings from [Landmodo](https://www.landmodo.com), including property details, pricing information, and location data. It handles pagination and performs additional calculations for property analysis.

## Features

- Automated property listing extraction
- Pagination handling
- Price calculations (Term Price, Price per Acre, WS Price)
- JSON data output
- Location-based search functionality

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd landmodo
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

Run the scraper with a location search:
```bash
python landmodo_scrapper.py "Mohave County, AZ"
```

The script will:
1. Search for properties in the specified location
2. Navigate through all result pages
3. Extract property information
4. Calculate pricing metrics
5. Output results in JSON format

## Data Collection

The scraper collects and calculates the following information for each property:

### Basic Information
- Property acreage
- APN (Assessor's Parcel Number)
- Property URL
- Listing month
- Seller information

### Calculated Metrics
- Term Price
- Price per Acre
- WS Price

## Sample Output

```json
{
    "acerage": "2.07",
    "apn": "207-03-124",
    "link": "https://www.landmodo.com/properties/282478/...",
    "month_listed": "05",
    "no": 1,
    "price_per_acre": 3671.49,
    "seller": "La Vie Style",
    "term_price": 7600.0,
    "ws_price": 0
}
```

## Technologies Used

- **Python**: Core programming language
- **Playwright**: Web automation and navigation
- **JSON**: Data formatting and storage
- **re**: Regular expression processing

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Pagination errors
- Data extraction failures
- Calculation errors
- Invalid search queries

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Landmodo's terms of service before use.
