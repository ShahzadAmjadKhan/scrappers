# Endole & Companies House Data Extractor

A Python-based tool that interfaces with both Endole and Companies House APIs to extract comprehensive company information and export it to Excel format.

## Overview

This tool provides a streamlined way to gather company data from two major UK business information sources:
- Endole: Detailed business analytics and financial data
- Companies House: Official UK company registration and filing information

## Features

- Dual API integration (Endole & Companies House)
- Automated data collection
- Excel report generation
- Configurable search parameters
- Rate limiting compliance
- Error handling and retry logic

## Prerequisites

- Python 3.7+
- API keys for both services:
  - Endole API key
  - Companies House API key
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd endole-companies-house
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
Create a `config.py` file with your API keys:
```python
ENDOLE_API_KEY = "your_endole_api_key"
COMPANIES_HOUSE_API_KEY = "your_companies_house_api_key"
```

## Usage

The tool provides two main client classes:

### EndoleApiClient
```python
from EndoleApiClient import EndoleApiClient

client = EndoleApiClient(api_key="your_api_key")
company_data = client.get_company_info("company_number")
```

### CompaniesHouseApiClient
```python
from CompaniesHouseApiClient import CompaniesHouseApiClient

client = CompaniesHouseApiClient(api_key="your_api_key")
company_data = client.get_company_details("company_number")
```

## Output Format

The tool generates an Excel file containing:
- Company details
- Financial information
- Director information
- Filing history
- Additional metadata

## Technologies Used

- **Python**: Core programming language
- **Requests**: API communication
- **xlsxwriter**: Excel file generation
- **JSON**: Data parsing and handling

## Error Handling

The tool includes comprehensive error handling for:
- API rate limits
- Authentication errors
- Network issues
- Invalid company numbers
- Data parsing errors

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please ensure you comply with both Endole and Companies House terms of service and API usage guidelines.
