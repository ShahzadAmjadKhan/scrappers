# RealEstate.com.au Scraper

A Python-based web scraper that extracts property listings and information from RealEstate.com.au.

## Overview

This tool automates the collection of real estate listings from [RealEstate.com.au](https://www.realestate.com.au), providing comprehensive property information including prices, locations, and property details.

## Features

- Automated property listing extraction
- Location-based search
- Property details collection
- Anti-bot detection measures
- Data export capabilities

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd realestate-au
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

Run the scraper:
```bash
python realestate-scrapper.py "Sydney, NSW"
```

The script will:
1. Navigate to RealEstate.com.au
2. Search for properties in the specified location
3. Extract property information
4. Process and format the data

## Data Collection

The scraper collects the following information for each property:

### Property Details
- Address
- Price/Price Range
- Property Type
- Number of Bedrooms/Bathrooms
- Land Size
- Property Features
- Agent Information

### Additional Information
- Listing Date
- Inspection Times
- Auction Details (if applicable)
- Property Description

## Technologies Used

- **Python**: Core programming language
- **Playwright**: Web automation and anti-bot handling
- **BeautifulSoup4**: HTML parsing
- **JSON**: Data storage format

## Features

- Location-based search
- Price range filtering
- Property type filtering
- Pagination handling
- Data validation

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Anti-bot detection
- Invalid search parameters
- Missing property data
- Rate limiting

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with RealEstate.com.au's terms of service before use. 