# US High Schools 
- Extract information about the US high schools from https://www.usnews.com/education/best-high-schools/search. 
- High school information is stored in Excel format

# Solution
- Script uses requests library to call the API 
- Processes the json response and use Pandas to convert it in excel format 
- Data is fetched till all high-schools are fetched which requires calling API with page parameter 

# Language & Tools
- Python
- requests
- Pandas