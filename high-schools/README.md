# US High Schools Data Scraper

A Python-based data extraction tool that collects comprehensive information about US high schools from US News & World Report.

## Overview

This tool automates the collection of high school data from [US News & World Report's Best High Schools](https://www.usnews.com/education/best-high-schools/search) database, providing detailed information about educational institutions across the United States.

## Features

- Automated API data collection
- Pagination handling
- Excel report generation
- Clean data formatting
- Comprehensive school information

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd high-schools
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python highschool.py
```

The script will:
1. Connect to the US News API
2. Fetch data for all available high schools
3. Process the JSON responses
4. Save the data to `highschools.xlsx`

## Data Collection

The scraper collects the following information for each school:
- School name
- Location (City, State)
- Rankings
- Student population
- Academic performance metrics
- Additional school details

## Technologies Used

- **Python**: Core programming language
- **requests**: API communication
- **pandas**: Data processing and Excel generation
- **json**: Response parsing

## Features

- Automated API pagination
- Rate limiting compliance
- Data validation
- Excel formatting
- Error handling

## Error Handling

The scraper includes error handling for:
- API rate limits
- Network connectivity issues
- Invalid responses
- Data processing errors
- File I/O operations

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with US News & World Report's terms of service before use.