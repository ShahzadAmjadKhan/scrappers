from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

CHROMEDRIVER_PATH = "../chromedriver-win64/chromedriver.exe"
USER_AGENT = \
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# Function to initialize the web driver
def initialize_driver():
    serv = Service(CHROMEDRIVER_PATH);
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument(f"--user-agent={USER_AGENT}")
    driver = webdriver.Chrome(options=options, service=serv)

    return driver


# Function to search for jobs using provided text on Google and get the search results
def search_jobs_near_me(driver, text):
    driver.get("https://www.google.com/")
    search_box = driver.find_element("name", "q")
    search_box.send_keys(text)
    search_box.send_keys(Keys.RETURN)
    try:
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//*[@id=\"fMGJ3e\"]/a")))
        job_link = driver.find_element(By.XPATH,"//*[@id=\"fMGJ3e\"]/a")
        job_link.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,"//*[@id=\"immersive_desktop_root\"]/div/div[3]/div[1]/div[1]/div[3]/ul/li")))
        return True
    except TimeoutException as ex:
        print("Jobs Not found")
        driver.close()
        return False


# Function to scrape job listings from the search results
def scrape_job_listings(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    jobs = soup.find_all("li", class_="iFjolb gws-plugins-horizon-jobs__li-ed")

    for job in jobs:
        job_title = job.find("div", class_="BjJfJf PUpOsf").get_text()
        company = job.find("div", class_="vNEEBe").get_text()
        location = job.find("div", class_="Qk80Jf").get_text()
        print(f"Job Title: {job_title}, Company: {company}, Location: {location}")


def scroll_job_listings(driver):
    index = 1;
    job_list = []
    try:
        while True:
            before_count = len(job_list)
            if index == 1:
                job_list.extend(driver.find_elements(By.XPATH,"//*[@id=\"immersive_desktop_root\"]/div/div[3]/div[1]/div[1]/div[3]/ul/li"))
            else:
                job_list.extend(driver.find_elements(By.XPATH,"//*[@id=\"VoQFxe\"]/div["+str(index)+"]/div/ul/li"))
            after_count = len(job_list)
            driver.execute_script("return arguments[0].scrollIntoView(true);", job_list[len(job_list) - 1])
            index += 1
            if before_count == after_count:
                break

            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"VoQFxe\"]/div["+str(index)+"]/div/ul/li")))
    except TimeoutException as ex:
        print("jobs scroll complete")


# Main script
if __name__ == "__main__":
    driver = initialize_driver()

    try:
        search_text = input("Enter job search text:")
        print(f"Searching for jobs using query '{search_text}'")
        jobs_found = search_jobs_near_me(driver, search_text)
        if jobs_found:
            print("Scrolling jobs...")
            scroll_job_listings(driver)
            print("Here you go with all jobs:")
            scrape_job_listings(driver)
    finally:
        driver.quit()