# Job Scrapper
- Retrieve job information in JSON format from API https://jobs.hochschuljobboerse.de/srv.php/Suche/offers for jobs offer of 2024
- Each job contains the url, which is scraped to fetch more metadata, job description and application related details
- Job page can contain PDF, which is also processed and text extracted
- Data is stored in JSON format

# Solution
- Requests is used to fetch JSON response from API. For each item in JSON get the URL of Job
- Go to the URL of job and extract information from page or PDF
- Store the extracted information in JSON format.
- BeautifulSoup4 is used process the html content of the job and extract the required fields
- Requests is used to pro
- pymupdf is used to 

# Language & Tools
- Python
- Requests 
- Selenium  
- pymupdf
- BeautifulSoup4 
