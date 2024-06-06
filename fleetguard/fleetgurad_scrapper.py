from playwright.sync_api import sync_playwright, expect
import json
import re
import sys

class FleetguardDataRetriever:
    def __init__(self, searchTerm):
        self.fleetguard_url = "https://www.fleetguard.com/s/searchResults?propertyVal="+searchTerm+"&hybridSearch=false&language=en_US"
        self.searchTerm = searchTerm

    def retrieve_data(self):
        with sync_playwright() as p:
            print("Starting headless chromium browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                print("Scraping...")
                # Navigate to the Fleetguard website
                page.goto(self.fleetguard_url)

                print("Navigation to site completed")
                accept_close_button = page.get_by_role("button", name="Accept & Close")
                accept_close_button.click()
                
                #print(page.text_content)

                print("Page loaded Successfully")
                
                add_all_to_list_button = page.get_by_role("button", name="ADD ALL TO LIST")
                expect(add_all_to_list_button).to_be_visible()
                
                # Wait for page content to load
                page.wait_for_load_state()
                
                #print("page content")
                #page.content()
                
                exact_results =  page.locator("xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/c-product-listing-page/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div")
                exact_results.get_by_role("heading").is_visible();
                
                add_to_list_button = page.get_by_role("button", name="ADD TO LIST")
                total_results = add_to_list_button.count()
                print("Number of Search Results are: " +str(total_results))
                count = 1
                list = []
                while (count <= total_results):
                    
                    xpath = "xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/c-product-listing-page/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[" + str(count) + "]/div[1]/div/div[2]/div[2]"
                    desc_loc = page.locator(xpath)  
                    desc_str = desc_loc.get_by_role("paragraph").text_content()
                    #print(desc_str)
                    desc_str = re.sub(r'[^\x00-\x7F]+','', desc_str)
                    s1 = self.get_product_and_supplier(desc_str.lstrip())
                    list.append(s1)
                    count = count + 1
                
                json_array = json.dumps([ob.__dict__ for ob in list])

                return json_array
            except Exception as e:
                print(f"Error: {e}")
                return None
            finally:
                browser.close()

    def get_product_and_supplier(self, product_description):
        supplier = product_description.split(' ', 2)[0]
        product_code= product_description.split(' ', 2)[1]
        s1 = SearchData(supplier, product_code, self.searchTerm) 
        return s1
    
class SearchData: 
    def __init__(self, Manufacturer, SupplierPartNumber, SearchTerm): 
        self.Manufacturer = Manufacturer 
        self.SupplierPartNumber = SupplierPartNumber 
        self.SearchTerm = SearchTerm
    
        
# Usage
if __name__ == "__main__":
    
    searchTerm = "P553000"
    if (len(sys.argv) > 1):
        searchTerm =sys.argv[1] 
    print("Searching https://www.fleetguard.com for search term: " +str(searchTerm))
    data_retriever = FleetguardDataRetriever(str(searchTerm))
    retrieved_data = data_retriever.retrieve_data()
    if retrieved_data:
      print("Result is : " +retrieved_data)
    else:
      print("No Search Results Found")  



