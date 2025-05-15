# Google Jobs Scraper

A Python-based web scraper that extracts job listings from Google Jobs based on user-defined search criteria.

## Overview

This tool automates the process of searching and collecting job listings from Google Jobs, providing detailed information about job opportunities including titles, companies, and locations.

## Features

- Automated job search functionality
- Dynamic content loading through scrolling
- Customizable search parameters
- Clean data formatting
- Console-based output

## Prerequisites

- Python 3.7+
- pip (Python package installer)
- Chrome browser installed
- ChromeDriver (matching your Chrome version)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd google-jobs
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure ChromeDriver is installed and in your system PATH

## Usage

Run the scraper with your job search query:
```bash
python jobs.py "software engineer"
```

The script will:
1. Navigate to Google Jobs
2. Enter the search query
3. Scroll through results to load all listings
4. Extract and display job information

### Output Format

Jobs are displayed in the following format:
```
Job Title: Software Engineer, Company: Google, Location: Mountain View, CA
```

## Data Fields

The scraper collects the following information for each job:
- **Job Title**: Position name/title
- **Company**: Hiring company name
- **Location**: Job location

## Technologies Used

- **Python**: Core programming language
- **Selenium**: Web automation and dynamic content handling
- **BeautifulSoup4**: HTML parsing
- **ChromeDriver**: Browser automation

## Features

- Dynamic content loading through scrolling
- Real-time job data extraction
- Clean, formatted output
- Search customization
- Error handling

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Page loading failures
- No search results
- Browser automation errors

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with Google's terms of service before use.
