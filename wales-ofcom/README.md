# Wales Postcode Scraper and Ofcom API Data Collection

This project includes scripts to:
1. Scrape postcode information from Wales from the Towns Counties Postcodes website
2. Call the Ofcom Connected Nations Broadband API for each postcode and collect data

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```
pip install -r requirements.txt
```

## Scraping Postcodes

Run the postcode scraper from the project root directory:
```
python ofcom/scrape_wales_postcodes.py
```

The script will:
1. Scrape postcode area links from the main Wales postcodes page
2. Visit each postcode area page to extract individual postcodes
3. Save all results to `ofcom/output/wales_postcodes.csv`

## Calling Ofcom API

To collect broadband data for the scraped postcodes, run:
```
python ofcom/call_ofcom_api.py --api-key YOUR_API_KEY
```

Options:
- `--api-key`: (Required) Your Ofcom API subscription key
- `--input`: Input CSV file containing postcodes (default: ofcom/output/wales_postcodes.csv)
- `--output`: Output CSV file for results (default: ofcom/output/broadband_data.csv)
- `--limit`: Limit the number of postcodes to process (optional)

Example for testing with 10 postcodes:
```
python ofcom/call_ofcom_api.py --api-key YOUR_API_KEY --limit 10
```

The script will:
1. Read postcodes from the input CSV
2. Call the Ofcom API for each postcode
3. Save a summary of results to the output CSV
4. Store full API responses as JSON files in `ofcom/output/api_responses/`

## Output Format

### Postcode CSV
- Column 1: Postcode Area (e.g., "CF", "SA", "LL")
- Column 2: Full Postcode

### Broadband Data CSV
- PostCode: The full postcode
- Status: 'success' or error type
- AddressCount: Number of addresses found in the postcode
- MaxDownSpeed: Maximum download speed found across all addresses
- MaxUpSpeed: Maximum upload speed found across all addresses
- ResponseFile: Name of the JSON file containing the full API response

## Notes

- Both scripts include delays between requests to avoid overloading servers
- Error handling is included for network issues and API errors 