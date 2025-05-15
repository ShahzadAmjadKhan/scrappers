# Hochschuljobboerse Job Scraper

A Python-based data extraction tool that collects job listings and detailed information from the German academic job portal Hochschuljobboerse.

## Overview

This tool automates the collection of job postings from [Hochschuljobboerse](https://jobs.hochschuljobboerse.de), including detailed job descriptions, application requirements, and associated documents. The scraper focuses on jobs posted for the year 2024.

## Features

- Automated API data collection
- PDF document processing
- Detailed metadata extraction
- JSON data output
- Multi-format content handling

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd hochschuljobboerse
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python job-scrapper.py
```

The script will:
1. Connect to the Hochschuljobboerse API
2. Fetch all available job listings
3. Process each job's detailed page
4. Extract information from PDFs if present
5. Save all data to `jobs.json`

## Data Collection

The scraper collects the following information for each job:
- Job title and reference number
- Institution/employer details
- Location information
- Job description
- Application requirements
- PDF content (when available)
- Additional metadata

## Technologies Used

- **Python**: Core programming language
- **Requests**: API communication and web scraping
- **BeautifulSoup4**: HTML parsing
- **Selenium**: Dynamic content handling
- **PyMuPDF**: PDF processing
- **JSON**: Data storage format

## Features

- API integration
- PDF text extraction
- HTML content parsing
- Metadata aggregation
- Error handling and retry logic

## Error Handling

The scraper includes error handling for:
- API rate limits
- Network connectivity issues
- PDF processing errors
- Invalid HTML content
- File I/O operations

## Data Format

The output JSON file contains structured data with the following format:
```json
{
    "jobs": [
        {
            "title": "Job Title",
            "url": "Job URL",
            "description": "Full job description",
            "pdf_content": "Extracted PDF text",
            "metadata": {
                // Additional job details
            }
        }
    ]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Hochschuljobboerse's terms of service before use.
