# Fleetguard Product Scraper

A Python-based web scraper that extracts product and supplier information from Fleetguard's official website.

## Overview

This tool automates the process of searching and retrieving product information from [Fleetguard's website](https://www.fleetguard.com), providing detailed manufacturer and supplier data based on part numbers.

## Features

- Automated product search functionality
- JSON data output
- Cross-reference part number lookup
- Clean data formatting
- Batch processing capability

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd fleetguard
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

Run the scraper with a part number:
```bash
python fleetgurad_scrapper.py "P553000"
```

The script will:
1. Navigate to the Fleetguard website
2. Search for the specified part number
3. Extract all matching product information
4. Output the results in JSON format

### Example URL Format
For a search term 'P553000', the script will navigate to:
```
https://www.fleetguard.com/s/searchResults?propertyVal=P553000&hybridSearch=false&language=en_US
```

### Sample Output

```json
[
    {
        "Manufacturer": "FLEETGUARD",
        "SupplierPartNumber": "LF9009",
        "SearchTerm": "P553000"
    },
    {
        "Manufacturer": "FLEETGUARD",
        "SupplierPartNumber": "LF3000",
        "SearchTerm": "P553000"
    },
    {
        "Manufacturer": "FLEETGUARD",
        "SupplierPartNumber": "LF14009NN",
        "SearchTerm": "P553000"
    },
    {
        "Manufacturer": "FLEETGUARD",
        "SupplierPartNumber": "LF14002NN",
        "SearchTerm": "P553000"
    }
]
```

## Data Fields

The scraper collects the following information for each product:
- **Manufacturer**: Product manufacturer name
- **SupplierPartNumber**: Unique product identifier
- **SearchTerm**: Original search query used

## Technologies Used

- **Python**: Core programming language
- **Playwright**: Web automation and navigation
- **JSON**: Data formatting and output
- **argparse**: Command-line argument parsing

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Invalid part numbers
- No search results
- Page loading failures

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Fleetguard's terms of service before use.