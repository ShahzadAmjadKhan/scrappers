# Trust pilot Australia
- Extract information about the companies available from https://au.trustpilot.com/
- Stores information in CSV format

# Solution 
- Script uses playwright to browse to website and lookup for categories availbale at https://au.trustpilot.com/categories
- For each category it fetches list of claimed companies and extract Business name, website, and Pays for extra features 
- This information is stored in CSV format 

# Language & Tools
- Python
- Playwright
- CSV
