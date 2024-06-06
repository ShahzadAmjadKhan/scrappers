from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CHROMEDRIVER_PATH = "../chromedriver-win64/chromedriver.exe"
serv = Service(CHROMEDRIVER_PATH);
options = Options()
#options.add_experimental_option("detach", True)
#options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options, service=serv)
driver.implicitly_wait(0.5)

driver.get("https://www.google.com")
text_box = driver.find_element(By.XPATH, "//*[@id=\"APjFqb\"]")
text_box.send_keys("Jobs near me")
text_box.send_keys(Keys.ENTER)

WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//*[@id=\"fMGJ3e\"]/a")))
job_link = driver.find_element(By.XPATH,"//*[@id=\"fMGJ3e\"]/a")
job_link.click()

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,"//*[@id=\"immersive_desktop_root\"]/div/div[3]/div[1]/div[1]/div[3]/ul/li")))
job_list = driver.find_elements(By.XPATH,"//*[@id=\"immersive_desktop_root\"]/div/div[3]/div[1]/div[1]/div[3]/ul/li")

first_job_title_path = "./div/div[1]/div[2]/div/div/div[2]/div[2]"
first_job_company_path = "./div/div[1]/div[2]/div/div/div[4]/div/div[1]"
rest_job_title_path = "./div/div[2]/div[2]/div/div/div[2]/div[2]"
rest_job_company_path = "./div/div[2]/div[2]/div/div/div[4]/div/div[1]"
for index, job in enumerate(job_list):
    if(index == 0):
        title_path = first_job_title_path
        company_path = first_job_company_path
    else:
        title_path = rest_job_title_path
        company_path = rest_job_company_path

    title = job.find_element(By.XPATH, title_path)
    company = job.find_element(By.XPATH, company_path)

    print("Job Title: " + title.text, ", Company: "+ company.text)

driver.close()

