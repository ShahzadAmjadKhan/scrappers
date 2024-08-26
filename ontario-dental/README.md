# Royal College of Dental Surgeons of Ontario
- Extract information about the Dentist from https://www.rcdso.org/find-a-dentist 
- Extracted information is stored in JSON format

# Solution
- Script uses playwright to interact with https://www.rcdso.org/find-a-dentist 
- It searches for each specialty of the dentistary 
- For each search result, it extracts the Name, status, registeration number, primary practice address and phone (if available)
using beautiful soup

# Language & Tools
- Python
- Playwright
- Beautiful Soup
 
# Sample JSON Response

```json
[
 {
        "Name": "Andrew-Christian Adams",
        "Registration number": "85172",
        "Status": "Member",
        "Primary practice address": ", 883 Upper Wentworth St #201",
        "Phone": "(905) 318-5888",
        "Specialty": "Dental Anesthesiology"
    },
    {
        "Name": "Paul Azzopardi",
        "Registration number": "96067",
        "Status": "Member",
        "Primary practice address": "Smile Town Dentistry, 545 Parkside Dr",
        "Phone": "519-749-9981",
        "Specialty": "Dental Anesthesiology"
    },
    {
        "Name": "Jasdev Bhalla",
        "Registration number": "61789",
        "Status": "Member",
        "Primary practice address": "MM Family and Sleep Dentistry, 325 Winterberry Dr #106",
        "Phone": "(905) 512-8877",
        "Specialty": "Dental Anesthesiology"
    }
]

