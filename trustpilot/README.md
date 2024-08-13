# Trust pilot Australia
- Extract information about the companies available from https://au.trustpilot.com/
- Stores information in CSV format

# Solution 
- Script uses playwright to browse to website and lookup for categories available at https://au.trustpilot.com/categories
- For each category it fetches list of claimed companies and extract following information:
  - businessUnitId,
  - displayName
  - paysForExtraFeatures
  - claimed
  - numberOfReviews
  - stars
  - contact.website
  - contact.phone
  - contact.email
  - location.address
  - location.city
  - location.zipCode
  - trustScore
  - categories
  
- This information is stored in CSV format 

# Language & Tools
- Python
- Playwright
- Pandas
- Requests
