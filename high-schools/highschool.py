import json
import requests
import pandas as pd
import math
import re


URL = "https://www.usnews.com/education/best-high-schools/search?format=json&ranked=true&page={}"

class Highschool:

    def __init__(self, name, location, enrolled):
        self.Name = name
        self.Location = location
        self.City = re.split(',', location)[0]
        self.State = re.split(',', location)[1]
        self.Enrollment = enrolled

    def as_dict(self):
        return {'Name': self.Name, 'City': self.City, 'State': self.State, 'Enrollment': self.Enrollment}


def get_json(page=1):
    try:
        print("Fetching JSON from URL: {}".format(URL.format(page)))
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        response = requests.get(URL.format(page), headers=headers, timeout=30)
        if response.status_code == 200:
            print("JSON retrieved successfully")

        return response.content
    except Exception as ex:
        print("Exception {} Fetching JSON from URL: {}".format(type(ex).__name__, URL))

def get_highschools(data):
    schools = []
    for school in data["matches"]:
        highschool = Highschool(school["name"], school["school"]["location"], school["data"][2]["raw_value"])
        schools.append(highschool)

    return schools


def start_process(max=0):
    highschools = []
    page_size = 20
    data = json.loads(get_json())
    total_records = data["totalMatches"]
    total_pages = math.ceil(total_records / page_size)
    if max > 0:
        total_pages = max
    page = 1
    while page <= total_pages:
        data = json.loads(get_json(page))
        highschools.extend(get_highschools(data))
        page += 1

    df = pd.DataFrame([x.as_dict() for x in highschools])
    df.to_excel('highschools.xlsx', index=False)

if __name__ == "__main__":

    start_process(max=2)

