# Alberta Assembly 
- Extract information about the different bills presented in alberta assembly from https://www.assembly.ab.ca/assembly-business/assembly-dashboard
- Stores information in CSV format

# Solution 
- Script uses playwright to browse to website and lookup for list of bills.
- Bills html content is then parsed using beautifulsoup4 to extract the required fields
- Pandas is used to create the CSV

# Language & Tools
- Python
- Playwright
- beautifulsoup4
- Pandas
