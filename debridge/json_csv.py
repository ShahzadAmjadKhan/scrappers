import requests
import time
import json
import os
import csv
from datetime import datetime, timedelta

# ---- Default Dates ----
DEFAULT_START = "2023-01-10"
DEFAULT_END = "2025-10-27"  # example one month later

# ---- User Input with Defaults ----
start_date_str = input(f"Enter start date (YYYY-MM-DD) [default {DEFAULT_START}]: ").strip() or DEFAULT_START
end_date_str = input(f"Enter end date (YYYY-MM-DD) [default {DEFAULT_END}]: ").strip() or DEFAULT_END

try:
    START_DATE = datetime.strptime(start_date_str, "%Y-%m-%d")
    END_DATE = datetime.strptime(end_date_str, "%Y-%m-%d")
except ValueError:
    print("❌ Invalid date format. Please use YYYY-MM-DD.")
    exit(1)

# ---- Config ----
SAVE_DIR = "data"
SLEEP_SECONDS = 3
API_URL = "https://stats-api.dln.trade/api/Satistics/getDaily"
OUTPUT_CSV = "dln_daily_summary.csv"

# ---- Chain Mapping ----
CHAIN_MAP = {
    1: "Ethereum",
    56: "BNB",
    128: "Heco",
    137: "Polygon",
    42161: "Arbitrum",
    43114: "Avalanche",
    43113: "AvalancheTest",
    42: "Kovan",
    97: "BNBTest",
    256: "HecoTest",
    80001: "PolygonTest",
    421611: "ArbitrumTest",
    7565164: "Solana",
    250: "Fantom",
    59144: "Linea",
    8453: "Base",
    10: "Optimism",
    100000001: "Neon",
    100000002: "Gnosis",
    100000003: "LightLink",
    100000004: "Metis",
    100000005: "Bitrock",
    100000006: "CrossFi",
    100000009: "Flow",
    100000010: "zkEvmCronos",
    100000013: "Story",
    100000014: "Sonic",
    100000015: "Zircuit",
    100000017: "Abstract",
    100000020: "Berachain",
    100000021: "Bob",
    100000022: "HyperEVM",
    100000008: "Zilliqa",
    100000023: "Mantle",
    100000024: "Plume",
    100000025: "Sophon",
    900000026: "Shasta",
    100000026: "Tron",
    100000027: "Sei",
    100000028: "Plasma",
}

# ---- Ensure folder exists ----
os.makedirs(SAVE_DIR, exist_ok=True)

# ---- Request Headers ----
HEADERS = {
    "accept": "text/plain",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "origin": "https://app.debridge.com",
    "referer": "https://app.debridge.com/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36"
    ),
}

# ---- Step 1: Fetch monthly data ----
current_start = START_DATE
while current_start <= END_DATE:
    current_end = min(current_start + timedelta(days=30), END_DATE)
    range_str = f"{current_start.strftime('%Y-%m-%d')}_to_{current_end.strftime('%Y-%m-%d')}"
    filename = os.path.join(SAVE_DIR, f"{range_str}.json")

    if os.path.exists(filename):
        print(f"⏭️ Skipping {range_str} (already exists)")
        current_start = current_end + timedelta(days=1)
        continue

    params = {
        "dateFrom": f"{current_start.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "dateTo": f"{current_end.strftime('%Y-%m-%d')}T00:00:00.000Z",
    }

    try:
        print(f"📅 Fetching {range_str} ...")
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Saved -> {filename}")

    except Exception as e:
        print(f"❌ Error fetching {range_str}: {e}")

    time.sleep(SLEEP_SECONDS)
    current_start = current_end + timedelta(days=1)

print("\n✅ Data download complete. Now generating CSV...")

rows = []
# ---- Step 2: Parse all JSON files and write CSV ----
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Chain A", "Chain B", "Date (YYYY-MM-DD)", "USD amount transferred"])

    for file in sorted(os.listdir(SAVE_DIR)):
        if not file.endswith(".json"):
            continue

        path = os.path.join(SAVE_DIR, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "dailyData" not in data:
                continue

            for record in data["dailyData"]:
                give_chain_id = record["giveChainId"]["bigIntegerValue"]
                take_chain_id = record["takeChainId"]["bigIntegerValue"]
                usd_amount = record.get("totalAmountGivenUsd", 0)
                date_epoch = record.get("date")

                # Convert epoch → YYYY-MM-DD and ensure string format
                if date_epoch:
                    date_str = datetime.utcfromtimestamp(date_epoch).strftime("%Y-%m-%d")
                    # Force Excel to treat as text by prefixing with a single quote
                    date_str = f"{date_str}"
                else:
                    date_str = "'unknown"

                give_chain = CHAIN_MAP.get(give_chain_id, f"unknown({give_chain_id})")
                take_chain = CHAIN_MAP.get(take_chain_id, f"unknown({take_chain_id})")

                rows.append((give_chain, take_chain, date_str, usd_amount))

        except Exception as e:
            print(f"⚠️ Error parsing {file}: {e}")

rows.sort(key=lambda x: x[2])  # Sort by date_str (YYYY-MM-DD)

# ---- Write sorted CSV ----
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Chain A", "Chain B", "Date (YYYY-MM-DD)", "USD amount transferred"])

    for row in rows:
        # Prefix date with quote so Excel treats it as text
        writer.writerow([row[0], row[1], f"{row[2]}", row[3]])

print(f"\n🎉 CSV file '{OUTPUT_CSV}' generated successfully!")
