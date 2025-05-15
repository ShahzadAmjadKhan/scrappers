# Trustpilot Australia Business Scraper

A Python-based web scraper that extracts comprehensive business information from Trustpilot's Australian domain.

## Overview

This tool automates the collection of business data from [Trustpilot Australia](https://au.trustpilot.com), including company details, reviews, ratings, and contact information across various business categories.

## Features

- Automated business data extraction
- Category-based collection
- Comprehensive company information
- CSV data export
- Multi-category support

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd trustpilot
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
python trustpilot.py
```

The script will:
1. Navigate to Trustpilot's categories page
2. Extract all business categories
3. Collect company information for each category
4. Save data to CSV files in the `output` directory

## Data Collection

The scraper collects the following information for each business:

### Company Details
- Business Unit ID
- Display Name
- Premium Status (paysForExtraFeatures)
- Claimed Status
- Number of Reviews
- Star Rating
- Trust Score

### Contact Information
- Website URL
- Phone Number
- Email Address

### Location Details
- Street Address
- City
- ZIP Code

### Additional Information
- Business Categories
- Review Statistics

## Technologies Used

- **Python**: Core programming language
- **Playwright**: Web automation
- **Pandas**: Data processing and CSV generation
- **Requests**: API communication

## Features

- Category-based scraping
- Comprehensive data collection
- Error handling and retry logic
- Rate limiting compliance
- Data validation

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Rate limiting
- Missing company data
- Invalid responses
- Pagination errors

## Output Format

Data is saved in CSV format with the following structure:
```csv
businessUnitId,displayName,paysForExtraFeatures,claimed,numberOfReviews,stars,website,phone,email,address,city,zipCode,trustScore,categories
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Trustpilot's terms of service before use.
