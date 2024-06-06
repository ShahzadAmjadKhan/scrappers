from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import fitz
import io
import json
import requests
import datetime


# Job class to hold data of job
class Job:

    def __init__(self, job_id, date, title, type, extern, lat, long, logo, firma, url):
        self.JobID = job_id
        self.datum = date
        self.titel = title
        self.typ = type
        if extern is None or extern == "":
            self.extern = "hochschuljobboerse"
        else:
            self.extern = extern
        self.lat = lat
        self.long = long
        self.logo = logo
        self.firma = firma
        self.url = url
        self.Is_pdf = False
        self.address = None
        self.german_kenntnisse = None
        self.homeoffice = None
        self.contract = None
        self.valid_from = None
        self.working_hours = None
        self.job_description = None
        self.application_text = None
        self.application_link = None
        self.application_email = None


JOBS_JSON_URL = "https://jobs.hochschuljobboerse.de/srv.php/Suche/offers"

# Function to initialize the browser
def initialize_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    my_browser = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
    my_browser.implicitly_wait(5)
    return my_browser


# Function to fet JSON from defined JOBS_JSON_URL
def get_jobs_from_json():
    try:
        print("Fetching JSON from URL: {}".format(JOBS_JSON_URL))
        response = requests.get(JOBS_JSON_URL, timeout=30)
        if response.status_code == 200:
            print("Jobs JSON retrieved successfully")

        return response.content
    except Exception as ex:
        print("Exception {} Fetching JSON from URL: {}".format(type(ex).__name__, JOBS_JSON_URL))


# Function to get html of job url
def get_job_html(browser, url):
    print("{}: Getting Job content from URL: {}".format(datetime.datetime.now(), url))
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        page = BeautifulSoup(response.content, 'html.parser')
        first_frame_url = page.find(id="suchFrame").attrs['src']
        browser.get(first_frame_url)
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        browser.switch_to.frame(browser.find_element(By.TAG_NAME, 'iframe'))
        body = browser.find_element(By.TAG_NAME, 'body')
        if body.text == "Die Seite, die Sie aufrufen wollten, ist auf diesem Server nicht vorhanden.":
            return "No Job Text"

        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, '__next')))
        job_div = browser.find_element(By.ID, '__next')
        print("{}: Retrieved Job content from URL: {}".format(datetime.datetime.now(), url))
        return job_div.get_attribute('innerHTML')
    else:
        print("URL {} not opened".format(url))


# Function get extract the text of pdf and set in job_description
def set_job_description_from_pdf(browser, my_job):
    print("No description found. Checking for PDF..")
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/iframe')))
    pdf_frame = browser.find_element(By.XPATH, '//*[@id="__next"]/div/iframe')
    pdf_url = pdf_frame.get_attribute('src')
    pdf_response = requests.get(pdf_url)
    text = ''

    if pdf_response.status_code == 200:
        filestream = io.BytesIO(pdf_response.content)

        with fitz.open(stream=filestream, filetype="pdf") as doc:
            for p in doc:
                text += p.get_text()

    my_job.Is_pdf = True
    my_job.job_description = text


# function to set the job meta data i.e. address, home office, contract, valid from, working hours, german
def set_job_metadata(divs, my_job):
    if len(divs) >= 1:
        job_title_div = divs[0].find('h1', recursive=False)

        address = job_title_div.parent.find('img', src=lambda v: v and v.endswith('pin.svg'))
        if address:
            my_job.address = address.parent.text

        home_office = job_title_div.parent.find('img', src=lambda v: v and v.endswith('haus.svg'))
        if home_office:
            my_job.homeoffice = home_office.parent.text

        contract = job_title_div.parent.find('img', src=lambda v: v and v.endswith('arbeit.svg'))
        if contract:
            my_job.contract = contract.parent.text

        valid_from = job_title_div.parent.find('img', src=lambda v: v and v.endswith('kalender.svg'))
        if valid_from:
            my_job.valid_from = valid_from.parent.text

        working_hours = job_title_div.parent.find('img', src=lambda v: v and v.endswith('uhr.svg'))
        if working_hours:
            my_job.working_hours = working_hours.parent.text

        german_kenntnisse = job_title_div.parent.find('img', src=lambda v: v and v.endswith('sprache.svg'))
        if german_kenntnisse:
            my_job.german_kenntnisse = german_kenntnisse.parent.text


# Function to set the job description
def set_job_description(divs, my_job):
    if len(divs) >= 2:
        my_job.job_description = divs[1].text


# Function to set the application text, link and email if available
def set_job_application(divs, my_job):
    if len(divs) >= 3:
        application_div = divs[2].find_all('div', recursive=False)

        if len(application_div) >= 1:
            my_job.application_text = application_div[0].text
            if len(application_div) >= 2:
                links = application_div[1].find_all('a', recursive=False)
                for link in links:
                    href = link['href']
                    if href.__contains__("mailto"):
                        my_job.application_email = href[7:len(href)]
                    else:
                        my_job.application_link = href


# Function to set the scrapped data in my_job
def set_job_scrapped_data(browser, job_html, my_job):

    page = BeautifulSoup(job_html, 'html.parser')
    text = page.text
    if len(text) == 0:
         set_job_description_from_pdf(browser, my_job)
    else:
        divs = page.find_all('div', {"class": "inserat-block"})
        set_job_metadata(divs, my_job)
        set_job_description(divs, my_job)
        set_job_application(divs, my_job)


# Function to get the initial object of Job
def get_job(job):
    return Job(job["ID"], job["datum"], job["titel"], job["typ"], job["extern"], job["lat"], job["lng"], job["logo"], job["firma"], job["url"])


# Function will start scraping for jobs. It will only scrape data for jobs where Year is greater than 2024
# In case of error where html is not available, it will try again one more time.
#
def start_scraping(browser, jobs):
    my_jobs = []
    records_read = 0
    for job in jobs["jobs"][:50]:
        date = datetime.datetime.strptime(job["datum"], '%d.%m.%Y')
        retry = 2
        if date.year >= 2024:
            while retry > 0:
                try:
                    my_job = get_job(job)
                    job_html = get_job_html(browser, job["url"])
                    if job_html != "No Job Text":
                        set_job_scrapped_data(browser, job_html, my_job)
                    else:
                        print("No Job Text available to scrape for url: ".format(job["url"]))
                    my_jobs.append(my_job)
                    retry = 0
                    records_read += 1
                except Exception as ex:
                    print("Exception has been thrown: {}".format(type(ex).__name__))
                    if retry == 2:
                        print("First Try fail. Going to Try again.....")
                    else:
                        print("Second Try failed. Not Trying again.....")

                    browser = initialize_browser()
                    retry -= 1
            if records_read >= 10:
                records_read = 0
                print("Writing records in Json file")
                write_in_json(my_jobs)

    return my_jobs


# Function to write the jobs list in json file
def write_in_json(my_jobs):

    with open('jobs.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps([vars(j) for j in my_jobs], sort_keys=False, ensure_ascii=False))


if __name__ == "__main__":
    print("Initializing Browser...")
    browser = initialize_browser()
    jobs_json = get_jobs_from_json()

    if jobs_json:
        print("Loading Json data received...") 
        jobs = json.loads(jobs_json)
        print("Going to start scraping...")
        print("Start Time: {}".format(datetime.datetime.now()))
        my_jobs = start_scraping(browser, jobs)
        print("Scraping done. writing data in jobs.json")
        write_in_json(my_jobs)
        print("jobs.json is ready")
        print("End Time: {}".format(datetime.datetime.now()))
    else:
        print("No jobs returned from URL: {}".format(JOBS_JSON_URL))

    browser.close()
