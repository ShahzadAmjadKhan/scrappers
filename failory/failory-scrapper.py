import requests
from lxml import html
import pandas as pd

# Function to fetch HTML content of a webpage
def fetch_html_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def initialize_dict():
   # List of keys
  keyList = ["name", "city", "started_in", "founders", "industries", "number_of_investments", "funding_amount", "Number_of_exits", "equity_taken", "accelerator_duration", "website_link"]
  # initialize dictionary
  d = {}
  for i in keyList:
      d[i] = None
  return d


def get_startup_info(startup_info, str_value):
    if "City" in str_value:
        startup_info["city"] = str_value.split(":")[1]
    elif "Started" in str_value:
        startup_info["started_in"] = str_value.split(":")[1]
    elif "Founders" in str_value:
        startup_info["founders"] = str_value.split(":")[1]
    elif "Industries" in str_value:
        startup_info["industries"] = str_value.split(":")[1]
    elif "investments" in str_value:
        startup_info["number_of_investments"] = str_value.split(":")[1]
    elif "Funding" in str_value:
        startup_info["funding_amount"] = str_value.split(":")[1]
    elif "exits" in str_value:
        startup_info["Number_of_exits"] = str_value.split(":")[1]
    elif "Equity" in str_value:
        startup_info["equity_taken"] = str_value.split(":")[1]
    elif "Accelerator" in str_value:
        startup_info["accelerator_duration"] = str_value.split(":")[1]  
    elif "website" in str_value:
        startup_info["website_link"] = str_value.split(":")[1]    
    else:
        print("Not mapped: " +str_value)
    


# Function to parse HTML and extract data using XPath
def parse_html_with_xpath(content):
    tree = html.fromstring(content)
    # Extract data
    data = []
    chunk = 1
    total_chunks = 3

    while chunk <= total_chunks:
        url_index = 3
        for i in range(1, 101):  # Loop through each article
            name_xpath = f'/html/body/div[6]/div[1]/div/div[1]/div/div[10]/article[{chunk}]/h3[{i}]'
            #101 /html/body/div[6]/div[1]/div/div[1]/div/div[10]/article[2]/h3[1]
            #201 /html/body/div[6]/div[1]/div/div[1]/div/div[10]/article[3]/h3[1]
        
            read_exits = True
            startup_info = initialize_dict()
            try:
                name = tree.xpath(name_xpath)[0].text.strip()
                startup_info["name"] = name
                attributes_xpath = f'/html/body/div[6]/div[1]/div/div[1]/div/div[10]/article[{chunk}]/ul[{i}]/li'
                count_str = f'count({attributes_xpath})'
                number_of_attributes_to_read = tree.xpath(count_str)
                print(number_of_attributes_to_read)
                index = 1
                while index <= int(number_of_attributes_to_read): 
                    xpath_str = attributes_xpath + f'[{index}]'
                    value_str = tree.xpath(xpath_str)[0].text.strip()
                    get_startup_info(startup_info, value_str)
                    index = index + 1
            
                website_link_xpath = f"/html/body/div[6]/div[1]/div/div[1]/div/div[10]/article[{chunk}]/p[{url_index}]/strong/a[1]/@href"
                startup_info["website_link"] = tree.xpath(website_link_xpath)[0]
                url_index += 4
                
                data.append(startup_info)
            except IndexError:
                print("index error " + str(i))
        
        chunk = chunk + 1        

    return data

# Function to save data to an Excel file
def save_to_excel(data, file_path):
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

# Main script
url = 'https://www.failory.com/startups/united-states-accelerators-incubators'
content = fetch_html_content(url)
accelerator_data = parse_html_with_xpath(content)
file_path = 'accelerators.xlsx'
save_to_excel(accelerator_data, file_path)

print(f"Data saved to {file_path}")
