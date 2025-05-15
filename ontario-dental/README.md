# Ontario Dental Practitioners Scraper

A Python-based web scraper that extracts dentist information from the Royal College of Dental Surgeons of Ontario (RCDSO) directory.

## Overview

This tool automates the collection of dental practitioner information from the [RCDSO Find a Dentist](https://www.rcdso.org/find-a-dentist) directory, providing comprehensive details about registered dentists in Ontario.

## Features

- Automated dentist information extraction
- Specialty-based search functionality
- Comprehensive practitioner details
- JSON data output
- Multi-specialty support

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd ontario-dental
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
python dental.py
```

The script will:
1. Connect to the RCDSO website
2. Search through each dental specialty
3. Extract practitioner information
4. Save the data to `all_dentists.json`

## Data Collection

The scraper collects the following information for each dentist:

### Practitioner Details
- Full Name
- Registration Number
- Current Status
- Primary Practice Address
- Contact Phone Number
- Specialty Area

## Sample Output

```json
[
    {
        "Name": "Andrew-Christian Adams",
        "Registration number": "85172",
        "Status": "Member",
        "Primary practice address": ", 883 Upper Wentworth St #201",
        "Phone": "(905) 318-5888",
        "Specialty": "Dental Anesthesiology"
    }
]
```

## Technologies Used

- **Python**: Core programming language
- **Playwright**: Web automation and form handling
- **BeautifulSoup4**: HTML parsing
- **JSON**: Data storage format

## Features

- Specialty-based search
- Comprehensive data extraction
- Error handling and retry logic
- Clean data formatting
- Bulk data processing

## Error Handling

The scraper includes error handling for:
- Network connectivity issues
- Form submission errors
- Missing practitioner data
- Invalid responses
- Rate limiting

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please review and comply with RCDSO's terms of service before use.
