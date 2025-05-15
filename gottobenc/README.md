# Got to Be NC Scraper

This script scrapes manufacturer information from the Got to Be NC website.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the scraper:
```bash
# Process default 5 companies
python scraper.py

# Process specific number of companies
python scraper.py --limit 10
```

The script will:
1. Visit the Got to Be NC manufacturers page
2. Extract company information from the listing
3. Visit each company's detail page (up to the specified limit)
4. Extract additional information including:
   - Website
   - Type of Production Facility
   - Co-Packer information
   - Business Availability
   - Products Sold
5. Save all data to `companies.csv`

### Command Line Arguments

- `--limit`: Maximum number of companies to process (default: 5)

## Output

The script generates a CSV file (`companies.csv`) containing the following columns:

- company_name: Name of the company
- location: Full address string
- location_city: Extracted city name
- location_state: State abbreviation (NC)
- location_zip: ZIP code
- href: URL to the company's detail page
- website: Company's website URL (if available)
- type_of_production: Type of production facility
- co_packer: Co-packer information
- business_availability: Business availability status
- products_sold: List of products sold by the company

Example row:
```csv
company_name,location,location_city,location_state,location_zip,href,website,type_of_production,co_packer,business_availability,products_sold
"Example Company","City, NC ZIP","City","NC","ZIP","https://gottobenc.com/member-list/example-company/","https://example.com","Home Based","N/A","Seasonal","Dry / Baking Goods, Sauces / Condiments / Rubs / Spices"
``` 