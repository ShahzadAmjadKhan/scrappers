# fleetguard-scrapper
1. This function scraps data from https://www.fleetguard.com
2. It takes search term as input and then navigate to site e.g for search term 'P553000' resulting url will be https://www.fleetguard.com/s/searchResults?propertyVal=P553000&hybridSearch=false&language=en_US
3. It loads the url, get data (supplier and product information) and build Json & print it.
4. Script uses Playwright library for navigation and data extraction
5. Sample output would be
```json
[
      {
            "Manufacturer": "FLEETGUARD",
            "SupplierPartNumber": "LF9009",
            "SearchTerm": "P553000"
      },
      {
            "Manufacturer": "FLEETGUARD",
            "SupplierPartNumber": "LF3000",
            "SearchTerm": "P553000"
      },
      {
            "Manufacturer": "FLEETGUARD",
            "SupplierPartNumber": "LF14009NN",
            "SearchTerm": "P553000"
      },
      {
            "Manufacturer": "FLEETGUARD",
            "SupplierPartNumber": "LF14002NN",
            "SearchTerm": "P553000"
      }
]
