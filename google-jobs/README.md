# Google Jobs 
- Extract information about the different jobs available on google based on user input text. 
- Jobs are printed on console in below format:
  - Job Title: {job_title}, Company: {company}, Location: {location}

# Solution 
- Script uses selenium to browse to website and lookup for list of jobs.
- Scrolls the list of jobs to ensure that all jobs are available on page
- Use beautifulsoup4 to parse the jobs html and print them on console

# Language & Tools
- Python
- Selenium (chrome driver)
- beautifulsoup4
