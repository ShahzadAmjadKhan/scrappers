import requests
import csv
import time
import random
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIG ===
INPUT_CSV = "filers.csv"          # first column: filer codes
OUTPUT_CSV = "liquidation_data.csv"
API_URL = "https://trade.cbp.dhs.gov/ace/liquidation/LBNotice/search"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json; charset=UTF-8",
    "dnt": "1",
    "origin": "https://trade.cbp.dhs.gov",
    "pragma": "no-cache",
    "referer": "https://trade.cbp.dhs.gov/ace/liquidation/LBNotice/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "x-xsrf-token": "4b945893-7a3d-4b1e-8302-cb4e11e0026b",  # replace with valid token if expired
}

COOKIES = {
    "XSRF-TOKEN": "4b945893-7a3d-4b1e-8302-cb4e11e0026b",
}

# === HELPERS ===
def daterange_2024(step_days=30):
    """Yield tuples of (from_date, to_date) covering all of 2024 in 30-day ranges."""
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    current = start
    while current <= end:
        next_date = min(current + timedelta(days=step_days - 1), end)
        yield current, next_date
        current = next_date + timedelta(days=1)


def to_epoch_millis(dt: datetime) -> int:
    """Convert datetime to epoch milliseconds."""
    return int(dt.timestamp() * 1000)


def read_filers(path: str):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [row[0].strip() for row in reader if row]


def write_records(records, path: str):
    """Append JSON list of dicts to CSV file."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(records)


def fetch_liquidation_data(filer: str, from_date: datetime, to_date: datetime):
    """Fetch all pages of results for one filer within one date range."""
    all_records = []
    start_index = 0

    while True:
        payload = {
            "dtPageVars": {
                "columns": [
                    {"data": "postedDate"},
                    {"data": "eventDate"},
                    {"data": "voidedDate"},
                    {"data": "event"},
                    {"data": "basis"},
                    {"data": "action"},
                    {"data": "entryNumber"},
                    {"data": "portOfEntry"},
                    {"data": "entryDate"},
                    {"data": "entryType"},
                    {"data": "teamNumber"},
                ],
                "start": start_index,
                "length": 100,
            },
            "searchFields": {
                "filer": filer,
                "entryDateFrom": to_epoch_millis(from_date),
                "entryDateTo": to_epoch_millis(to_date),
            },
        }

        resp = requests.post(API_URL, headers=HEADERS, cookies=COOKIES, json=payload, verify=False)
        if resp.status_code != 200:
            print(f"[ERROR] Filer {filer} {from_date:%Y-%m-%d}–{to_date:%Y-%m-%d}: HTTP {resp.status_code}")
            break

        try:
            response_json = resp.json()
            result_data = response_json.get("data", {})
            data_list = result_data.get("data", [])
            total = result_data.get("recordsTotal", 0)
        except Exception as e:
            print(f"[ERROR] JSON parse failed: {e}")
            break

        if not data_list:
            break

        print(f"Fetched {len(data_list)} records (start={start_index}) for filer={filer}")
        all_records.extend(data_list)

        # pagination
        if len(data_list) < 100 or start_index + 100 >= total:
            break
        start_index += 100

        # Delay between paginated API calls
        delay = random.uniform(1.0, 3.0)
        print(f"  Sleeping {delay:.1f}s before next page...")
        time.sleep(delay)

    return all_records


# === MAIN ===
def main():
    filers = read_filers(INPUT_CSV)
    print(f"Loaded {len(filers)} filer codes")

    for filer in filers:
        print(f"\n=== Processing filer: {filer} ===")
        for start_date, end_date in daterange_2024():
            print(f"  Range: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}")
            records = fetch_liquidation_data(filer, start_date, end_date)
            if records:
                write_records(records, OUTPUT_CSV)
            # Delay between date range calls
            delay = random.uniform(1.5, 4.0)
            print(f"  Sleeping {delay:.1f}s before next date range...")
            time.sleep(delay)


if __name__ == "__main__":
    main()
