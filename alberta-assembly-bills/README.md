# Alberta Assembly Bills Scraper

A Python-based web scraper that extracts information about bills presented in the Alberta Legislative Assembly from their official website.

## Overview

This scraper automates the collection of bill information from [Alberta Assembly Dashboard](https://www.assembly.ab.ca/assembly-business/assembly-dashboard), providing a comprehensive dataset of legislative activities.

## Features

- Automated extraction of bill information
- Data export to CSV format
- Robust error handling
- Clean data formatting

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd alberta-assembly-bills
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
python bill.py
```

The script will:
1. Navigate to the Alberta Assembly website
2. Extract information about all available bills
3. Save the data to `bills_readings.csv`

## Output Format

The script generates a CSV file with the following information:
- Bill number
- Bill title
- Current status
- Reading dates
- Additional metadata

## Technologies Used

- **Playwright**: Web automation and navigation
- **BeautifulSoup4**: HTML parsing and data extraction
- **Pandas**: Data manipulation and CSV generation
- **Python**: Core programming language

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Page loading failures
- Data parsing errors

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with the Alberta Legislative Assembly website's terms of service before use.
