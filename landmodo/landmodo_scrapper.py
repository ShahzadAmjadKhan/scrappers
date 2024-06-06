from playwright.sync_api import sync_playwright, expect
import json
import re
import sys

class LandModoDataRetriever:
    def __init__(self, searchTerm):
        self.landmodo_url = "https://www.landmodo.com"
        self.searchTerm = searchTerm

    def retrieve_data(self):
        with sync_playwright() as p:
            print("Starting headless chromium browser...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            list = []

            try:
                print("Scraping...")
                # Navigate to the Landmodo website
                page.goto(self.landmodo_url)

                print("Navigation to site completed")
                location_value_field = page.get_by_placeholder('Where are you looking?')
                expect(location_value_field).to_be_visible()
                location_value_field.fill(self.searchTerm)
                
                search_now_button = page.get_by_role("button", name="Search Now")
                search_now_button.click()
                

                print("Page loaded Successfully")
                
                heading = page.get_by_role("heading", name="Results in Mohave County, AZ")
                expect(heading).to_be_visible()
                
                # Wait for page content to load
                page.wait_for_load_state()
                
                page_counter = 1
                next_page_exists = True
                
                while next_page_exists:
                    print("Data from Page: " + str(page_counter))
                    counter = 1
                    total_count_per_page = page.locator('div.mid_section.xs-nopad.col-sm-8').count()
                    print(total_count_per_page)
                    div_counter = counter
                    while (counter <= total_count_per_page):
                        property =  page.locator("xpath=/html/body/div[3]/div/div[2]/div[1]/div[3]/div["+str(div_counter)+"]/div/div[5]/a")
                        print("Getting Details: " + str(counter) + ". " + property.get_attribute('title'))
                        #print(property.get_attribute('href'))
                        s1 = self.get_property_data(page, property, counter)
                        list.append(s1)
                        div_counter = div_counter + 2
                        counter = counter + 1
                        page.go_back()
                        page.wait_for_load_state()
                    
                    if (page.locator('div.post-pagination-block').get_by_label("next").is_visible()):
                        page.locator('div.post-pagination-block').get_by_label("next").click()
                        page.wait_for_load_state()
                        page_counter = page_counter + 1
                    else:
                        next_page_exists = False
                                    
                json_array = json.dumps([ob.__dict__ for ob in list])
                return json_array
            except Exception as e:
                print(f"Error: {e}")
                return None
            finally:
                browser.close()

    def get_property_data(self, page, property, counter):
        property.click()
        page.wait_for_load_state("domcontentloaded")
        
        #with context.expect_page() as new_page_info:
        #    page.click("xpath=/html/body/div[3]/div/div[2]/div[1]/div[3]/div[1]/div/div[5]/a") # Opens a new tab
        #page2 = new_page_info.value

        print(page.title())
        link = page.url
        #print(page.locator('div.col-sm-8').count())
        #print(page.locator('span.textbox.textbox-apn').count())
        #print(page.locator('div.col-sm-8').all_text_contents())
        apn = page.locator('span.textbox.textbox-apn').text_content()
        print(apn)
        first_apn = self.get_apn(apn)
        acerage = page.locator('span.textbox.textbox-property_acreage').text_content()
        print(acerage)
        months = page.locator('span.textbox.textbox-months').text_content()
        print(months)
        monthly_payment = page.locator('span.textbox.textbox-monthly_payment').text_content()
        print(monthly_payment)
        down_payment = page.locator('span.textbox.textbox-down_payment').text_content()
        print(down_payment)
        term_price = self.calculate_term_price(int(months), float(monthly_payment[1:].replace(',','')), float(down_payment[1:].replace(',','')))
        price_per_acre = self.calculate_per_acre_price(float(term_price), float(acerage))
        #WSPrice
        #ws_price = page.locator('span.textbox.textbox-ws_price').text_content()
        ws_price = 0
        posted_date = page.locator('span.posted-by-snippet-date').text_content()
        print(posted_date)
        month_listed = self.get_month(posted_date)
                
        seller = page.locator('span.inline-block.posted-by-snippet-author').get_by_role("link").text_content()
        print(seller)
        
        s1 = SearchData(counter, first_apn, acerage, term_price, price_per_acre, ws_price, month_listed, seller.strip(), link) 
        return s1
        
    def calculate_term_price(self, months, monthly_payment, down_payment):
        return (months * monthly_payment) + down_payment
    
    def calculate_per_acre_price(self, term_price, acerage):
        return term_price / acerage   
    
    def get_month(self, posted_date):
        month,date,year=posted_date.split('/')
        return month.strip()
    
    def get_apn(self, apn):
        try:
            result = apn.split(',')
            apn1,apn2,apn3=result[0].split('-')
            return apn1.strip()
        except Exception as e:
                print(f"Error: {e}")
                print("Error for apn" + str(apn))
        return apn        
    
class SearchData: 
    def __init__(self, no, apn, acerage, term_price, price_per_acre, ws_price, month_listed, seller, link): 
        self.no = no 
        self.apn = apn 
        self.acerage = acerage
        self.term_price = term_price 
        self.price_per_acre = price_per_acre 
        self.ws_price = ws_price
        self.month_listed = month_listed 
        self.seller = seller 
        self.link = link
    
        
# Usage
if __name__ == "__main__":
    
    searchTerm = "Mohave County, AZ"
    if (len(sys.argv) > 1):
        searchTerm =sys.argv[1] 
    print("Searching https://www.landmodo.com for search term: " +str(searchTerm))
    data_retriever = LandModoDataRetriever(str(searchTerm))
    retrieved_data = data_retriever.retrieve_data()
    if retrieved_data:
      print("Result is : " +retrieved_data)
    else:
      print("No Search Results Found")  



