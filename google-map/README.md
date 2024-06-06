# Google Map 
- Extract information about the different places available on google map based on user input text. 
- Places name are printed on console in below format:
  - Places found: {}

# Solution
- Script uses playwright to launch a chrome browser with url https://www.google.com/maps.
- Enters the search text provided by client in search text box 
- Scrolls the list of places till all places are loaded on page
- Use beautifulsoup4 to parse the places html and print them on console

# Language & Tools
- Python
- Playwright
- beautifulsoup4
