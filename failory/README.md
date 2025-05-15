# Failory Startup Accelerator Scraper

A Python-based web scraper that extracts comprehensive information about top startup accelerators from Failory.com.

## Overview

This tool automates the collection of detailed information about the top 300 startup accelerators in the United States from [Failory's comprehensive list](https://www.failory.com/startups/united-states-accelerators-incubators).

## Features

- Automated extraction of accelerator information
- Excel report generation
- Clean data formatting
- Comprehensive accelerator metrics collection

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd failory
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python failory-scrapper.py
```

The script will:
1. Navigate to the Failory website
2. Extract information about top accelerators
3. Save the data to `accelerators.xlsx`

## Data Points Collected

The scraper collects the following information for each accelerator:

- **Accelerator Name**: Official name of the program
- **City**: Location of the accelerator
- **Started In**: Year the accelerator was founded
- **Founders**: Names of the founding team
- **Industries**: Target industries/sectors
- **Number of Investments**: Total investments made
- **Funding Amount**: Typical investment size
- **Number of Exits**: Successful exits from portfolio
- **Equity Taken**: Percentage of equity required
- **Accelerator Duration**: Program length
- **Website URL**: Official website link

## Technologies Used

- **Python**: Core programming language
- **lxml**: XML and HTML processing
- **requests**: HTTP requests handling
- **pandas**: Data manipulation and Excel generation

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Missing data fields
- Rate limiting
- Parsing errors

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Failory's terms of service before use.
