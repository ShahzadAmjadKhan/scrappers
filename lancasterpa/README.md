
# Lancaster Parcel Scraper

This script scrapes property tax information from Lancaster County's online system. It takes a list of parcel numbers, visits the corresponding URLs, and extracts:
- **Parcel Number**
- **Tax Year**
- **Delinquent Tax Amount**
- **Owner Name**
- **Property Address**

Results are saved in Excel (`.xlsx`) format, with batch progress tracked and logged.

---

## 🚀 Features

✅ Supports scraping up to **500,000 parcel numbers** (batch processing).  
✅ Saves data incrementally in `.xlsx` files (one per batch).  
✅ Configurable **proxy support** (optional).  
✅ Built-in **logging** to file and console.  
✅ Includes **throttling** (delays between requests) to avoid blocking.

---

## 🛠️ Requirements

- Python 3.7+
- The following Python packages:
  - `pandas`
  - `beautifulsoup4`
  - `playwright`

You can install the requirements using:

```bash
pip install pandas beautifulsoup4 playwright
python -m playwright install
```

---

## 📂 Usage

1️⃣ Prepare your **parcel number file** (`parcel_numbers.txt`), one parcel number per line:
```
120-07947-0-0000
120-22182-0-0000
120-61924-0-0000
```

2️⃣ Run the script:

```bash
python lancaster_scraper.py --input-file parcel_numbers.txt
```

3️⃣ (Optional) Use a proxy:

```bash
python lancaster_scraper.py --input-file parcel_numbers.txt --proxy http://143.198.42.182:31280
```

---

## 🔧 Arguments

| Argument        | Description                                             |
|-----------------|---------------------------------------------------------|
| `--input-file`  | Path to the text file containing parcel numbers.        |
| `--proxy`       | Optional proxy URL (e.g., `http://IP:PORT`).            |

---

## 📝 Output

- Data saved as `lancaster_parcel_data_batch_1.xlsx`, `lancaster_parcel_data_batch_2.xlsx`, etc.
- Logs written to `lancaster_parcel_scraper.log`.

---

## 📌 Notes

- The script **respects polite scraping**: delays between requests and batch processing.
- Make sure you have the necessary permissions and adhere to the website’s Terms of Service.

---

## 👨‍💻 Development & Contributions

Feel free to fork, open issues, or contribute via pull requests! 😊
