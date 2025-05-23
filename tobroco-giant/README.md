# TOBROCO-GIANT Dealer Location Scraper

This Python script fetches dealer location data from [TOBROCO-GIANT](https://www.tobroco-giant.com), normalizes the nested JSON, and exports it into a CSV file for easy analysis or integration into other systems.

## 📦 Features

- Retrieves JSON data from the official TOBROCO-GIANT locations endpoint.
- Extracts and flattens key details such as name, address, coordinates, sectors, and services.
- Saves the data into a clean, UTF-8 encoded CSV file.

## 📁 Output

The script generates a file named:

```
tobroco_locations.csv
```

Each row represents a dealer, with the following columns:

- `id`
- `name`
- `city`
- `country`
- `street`
- `postalCode`
- `email`
- `website`
- `phone`
- `formattedPhone`
- `contacturl`
- `latitude`
- `longitude`
- `sectors` (comma-separated)
- `services` (comma-separated)

## 🛠 Requirements

- Python 3.7+
- Required libraries:
  - `requests`
  - `pandas`

Install them using:

```bash
pip install requests pandas
```

## 🚀 Usage

Run the script with:

```bash
python fetch_locations.py
```

After successful execution, `tobroco_locations.csv` will be created in the same directory.

## 🔗 API Endpoint

- URL: [`https://www.tobroco-giant.com/calls/fetchLocations.php`](https://www.tobroco-giant.com/calls/fetchLocations.php)

## 📄 License

This project is provided for educational and personal use. TOBROCO-GIANT data is publicly accessible but respect their terms of service and data usage policies.
