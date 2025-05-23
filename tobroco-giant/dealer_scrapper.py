import requests
import json
import pandas as pd

def fetch_and_save_locations(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse response JSON
        data = response.json()

        # Extract the 'items' list
        items = data.get("items", [])

        normalized_data = []
        for item in items:
            flat_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "city": item.get("city"),
                "country": item.get("country"),
                "street": item.get("street"),
                "postalCode": item.get("postalCode"),
                "email": item.get("email"),
                "website": item.get("website"),
                "phone": item.get("phone"),
                "formattedPhone": item.get("formattedPhone"),
                "contacturl": item.get("contacturl"),
                "latitude": item.get("position", {}).get("lat"),
                "longitude": item.get("position", {}).get("lng"),
                "sectors": ", ".join([s.get("name") for s in item.get("sectors", [])]),
                "services": ", ".join([s.get("name") for s in item.get("services", [])])
            }
            normalized_data.append(flat_item)

        df = pd.DataFrame(normalized_data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ CSV saved as '{output_file}' with {len(df)} rows.")

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to decode JSON: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

# Run the function
if __name__ == "__main__":
    url = "https://www.tobroco-giant.com/calls/fetchLocations.php"
    output_file = "tobroco_locations.csv"
    fetch_and_save_locations(url, output_file)
