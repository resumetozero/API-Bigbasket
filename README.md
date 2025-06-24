# 🛒 BigBasket Product Scraper (Async)

This project scrapes **all product listings** from [BigBasket](https://www.bigbasket.com) using their **internal listing API** by extracting `slug` values from the category tree. The scraper is built using `asyncio` and `aiohttp` for high performance and concurrency.

---

## 🔁 Reverse Engineering the API

To get the data directly without browser automation (e.g., Selenium), we reverse-engineered BigBasket's internal API using the following steps:

1. **Open DevTools in Chrome** (F12) → Go to **Network tab**.
2. Visit any BigBasket category (e.g., `https://www.bigbasket.com/pc/fruits-vegetables/fresh-vegetables/`).
3. Filter `XHR` or search for the API URL:
   ```
   https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=...
   ```
4. Copy the **Request URL**, **Headers**, and **Cookies** from any product listing call.

This helps mimic real user behavior and bypass bot detection.

---

## 📁 Project Structure

```
.
├── webscrapper_bigbasket.py        # Fetch and save BigBasket category slugs
├── scrape_bigbasket_products.py  # Main async scraper
├── category_tree.json            # Saved list of categories/slugs
├── headers.json                  # Extracted request headers (for authentication)
├── cookies.json                  # Extracted request cookies (for session state)
├── all_processed_products.json   # Final output JSON with product details
└── README.md                     # This file
```

---

## 🚀 How It Works

### Step 1️⃣: Fetch Category Tree

Run:
```bash
python fetch_category_tree.py
```
This hits BigBasket’s category API and saves all slugs in `category_tree.json`.

### Step 2️⃣: Scrape Products for All Categories

Run:
```bash
python scrape_bigbasket_products.py
```

The script:
- Loads `category_tree.json`, `headers.json`, and `cookies.json`
- Iterates over all slugs
- Uses BigBasket’s internal paginated API
- Saves all product data to `all_processed_products.json`

---

## 📦 Product Fields Extracted

Each product includes:

- `Id`
- `EAN code`
- `Title` (formatted with brand, weight, unit, price)
- `Brand`
- `Magnitude` & `Unit`
- `w_mag`, `w_unit`, and `Count`
- `Price`
- `Category` (TLC / MLC / LLC)
- `Children` (if present)
- `Image` links

---

## 🧪 Technologies Used

- `Python 3.8+`
- `playwright`
- `aiohttp`, `asyncio`
- `re`, `json`, `urllib.parse`

---

## 🛡 Headers & Cookies Format

### `headers.json`
```json
{
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)...",
  "x-channel": "BB-WEB",
  "x-entry-context": "bbnow",
  "x-entry-context-id": "10",
  "x-tracker": "e9537d9a-3df1-4ec6-815c-5ed49406c245",
  "accept": "*/*",
  "content-type": "application/json",
  "common-client-static-version": "101",
  "osmos-enabled": "true"
}
```

### `cookies.json`
Extracted from browser request headers (DevTools → Application → Cookies tab). Example:
```json
{
  "_bb_locSrc": "default",
  "_bb_vid": "NzgzODA1NDgyMjMwNTkzNzc0",
  "_bb_nhid": "7427",
  "csrftoken": "hIpF4arqHeLdV0WaSiG...",
  "ts": "2025-06-24 23:16:50.815",
  "...": "..."
}
```

---

## 🛠 Setup

### ✅ Install Python dependencies
```bash
pip install aiohttp
```

### 📂 Place Files

Make sure you have:
- `headers.json`
- `cookies.json`
- (Optional) Freshly regenerated from your browser session for accuracy

---

## ✅ Output

Results are saved in:
```
all_processed_products.json
```

Use this file for:
- Price comparison
- Product database
- Analytics

---

## 🧠 Tips

- Add delay (`await asyncio.sleep(1)`) to avoid rate-limiting
- Use a rotating proxy service or different accounts if blocked
- Headers/cookies may expire – regenerate if you hit 403/204 errors

---

## 🧾 Error Reference

- `204 No Content`: Server is returning empty data (rate-limited or invalid slug)
- `403 Forbidden`: Headers or cookies are likely expired/invalid
- `404 Not Found`: Invalid API path (slug or endpoint issue)
- `429 Too Many Requests`: Rate limit exceeded (too many requests sent in a short time; server is throttling to prevent abuse)


---

## 📜 License

This code is for **educational purposes only**.  
Do not use it for commercial scraping or in violation of [BigBasket’s Terms](https://www.bigbasket.com/terms/).

---

## 🙋‍♂️ Author

Made with ❤️ by **Rishabh Kumar**  
Learning, building, and automating everything Python 🐍

> 📫 Feel free to fork, use, and contribute!
