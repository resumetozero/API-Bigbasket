import asyncio
import aiohttp
import json
import re
import random
from urllib.parse import parse_qs, urlparse

# Semaphore to limit concurrency
sem = asyncio.Semaphore(5)

async def process_slug(session, slug, headers, cookies, all_product_details):
    async with sem:
        page = 1
        while True:
            url = f"https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug={slug}&page={page}"
            try:
                async with session.get(url, headers=headers, cookies=cookies) as response:
                    await asyncio.sleep(random.uniform(3, 6))
                    if response.status != 200:
                        print(f"❌ Status {response.status} for {url}")
                        break

                    data = await response.json()
                    products = data.get("tabs", [{}])[0].get("product_info", {}).get("products", [])
                    if not products:
                        break

                    print(f"✓ {slug}: Page {page}, {len(products)} items")

                    for product in products:
                        id = product.get("id")
                        ean_code = product.get("ean_code")
                        price = product.get("pricing", {}).get("discount", {}).get("mrp")
                        image_link = product.get("images")
                        brand = product.get("brand", {}).get("name")
                        title = product.get("desc")
                        mag = product.get("magnitude")
                        unit = product.get("unit")
                        children = product.get("children") if product.get("children") else "NAN"
                        tlc = product.get("category", {}).get("tlc_name")
                        mlc = product.get("category", {}).get("mlc_name")
                        llc = product.get("category", {}).get("llc_name")

                        w = product.get("w")
                        if not all([id, ean_code, price, image_link, brand, title, mag, unit, w]) or ean_code == "0":
                            continue

                        # Parse weight string
                        parsed = re.match(r"(\d+)[Xx](\d+\.?\d*)([a-zA-Z/ ]+)", w)
                        if parsed:
                            count = int(parsed.group(1))
                            w_mag = float(parsed.group(2))
                            w_unit = parsed.group(3).strip()
                        else:
                            count = 1
                            w_mag = "".join(re.findall("[0-9.+Xx]", w))
                            w_unit = "".join(re.findall("[A-Za-z+/ ]", w)).strip()

                        title_fmt = f"({title}){brand}[{count}x{w_mag}]{{{w_unit}}}<{price}>" if w_mag and w_unit else f"({title}){brand}[{mag}]{{{unit}}}<{price}>"

                        all_product_details.append({
                            "Id": id,
                            "EAN code": f'"{ean_code}"',
                            "Title": title_fmt,
                            "Brand": brand,
                            "Magnitude": mag,
                            "Unit": unit,
                            "Count": count,
                            "w_mag": w_mag,
                            "w_unit": w_unit,
                            "Price": price,
                            "category_tlc": tlc,
                            "category_mlc": mlc,
                            "category_llc": llc,
                            "Children": children,
                            "Image": image_link
                        })
                    page += 1
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                break

async def fetch_and_process_all_categories():
    try:
        with open("category_tree.json", "r") as f:
            category_data = json.load(f)
        with open("category_tree_request_headers.json", "r") as f:
            headers = json.load(f)
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
    except Exception as e:
        print(f"Error loading JSON files: {e}")
        return

    slugs = []
    if isinstance(category_data, dict) and "categories" in category_data:
        for category in category_data["categories"]:
            slug = category.get("slug")
            if slug:
                slugs.append(slug)
            if "children" in category:
                for child in category["children"]:
                    if "dest_slug" in child:
                        params = parse_qs(urlparse(f"?{child['dest_slug']}").query)
                        child_slug = params.get("slug", [None])[0]
                        if child_slug:
                            slugs.append(child_slug)

    if not slugs:
        print("No valid slugs found.")
        return

    all_product_details = []

    async with aiohttp.ClientSession() as session:
        tasks = [process_slug(session, slug, headers, cookies, all_product_details) for slug in slugs]
        await asyncio.gather(*tasks)

    with open("all_processed_products.json", "w", encoding="utf-8") as f:
        json.dump(all_product_details, f, ensure_ascii=False, indent=2)
    print("✅ All processed product data saved to 'all_processed_products.json'")

if __name__ == "__main__":
    asyncio.run(fetch_and_process_all_categories())
