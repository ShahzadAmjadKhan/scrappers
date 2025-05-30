# QLD Solar Panel Statistics Scraper

This Python script scrapes solar panel statistics from the [Solar Answered](https://www.solaranswered.com.au/solar-panel-pricing/qld/) website for suburbs in Queensland, Australia. It collects information such as:
- Suburb Name
- Postcode
- Number of homes
- Number of homes with solar

The script saves the results into a CSV file named `qld_solar_panel_statistics.csv`.

---

## Features

✅ Fetches the main page and finds all suburb links  
✅ Fetches each suburb's statistics page and extracts:  
&nbsp;&nbsp;&nbsp;&nbsp;• Postcode  
&nbsp;&nbsp;&nbsp;&nbsp;• Number of homes  
&nbsp;&nbsp;&nbsp;&nbsp;• Number of homes with solar  
✅ Saves the data in a structured CSV file  
✅ Includes logging for debugging and monitoring  
✅ Allows limiting the number of suburbs to scrape (default: 10)

---

## Installation

1. Clone this repository or download the script file:

```bash
git clone https://github.com/yourusername/qld-solar-panel-scraper.git
cd qld-solar-panel-scraper
```

2. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the script using Python:

```bash
python scraper.py
```

By default, it scrapes data for 10 suburbs. To specify a different limit:

```bash
python scraper.py --limit 20
```

---

## Output

The scraped data is saved in a CSV file named:

```
qld_solar_panel_statistics.csv
```

It includes the following columns:
- Suburb Name
- Postcode
- Number of homes
- Number of homes with solar

---

## Logging

The script uses the built-in `logging` module to provide feedback during scraping. Adjust the logging level in the script (`logging.basicConfig(level=logging.INFO, ...)`) as needed.

---

## License

This project is licensed under the MIT License.

---

## Disclaimer

This script is intended for educational purposes and personal use only. Use it responsibly and comply with the website's terms of service.

---

## Contact

If you have any questions, please reach out via email or GitHub issues.