import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

def extract_name_value_cookies(cookies_list, domain_filter=None):
    filtered = cookies_list
    if domain_filter:
        filtered = [c for c in cookies_list if domain_filter in c["domain"]]
    return {cookie["name"]: cookie["value"] for cookie in filtered}

async def fetch_bigbasket_data():
    request_headers_data = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        def handle_request(request):
            if "category-tree" in request.url:
                request_headers_data.update(request.headers)

        page.on("request", handle_request)

        try:
            async with page.expect_response(lambda res: "category-tree" in res.url and res.status == 200) as response_info:
                await page.goto("https://www.bigbasket.com/")
                await page.wait_for_timeout(8000)

            response = await response_info.value
            print(f"✅ Found category-tree URL: {response.url}")

            # Save category_tree.json
            json_data = await response.json()
            with open("category_tree.json", "w") as f:
                json.dump(json_data, f, indent=2)
            print("✅ Saved category_tree.json")

            # Save response headers
            response_headers = dict(response.headers)
            with open("category_tree_response_headers.json", "w") as f:
                json.dump(response_headers, f, indent=2)
            print("✅ Saved category_tree_response_headers.json")

            # Save request headers
            with open("category_tree_request_headers.json", "w") as f:
                json.dump(request_headers_data, f, indent=2)
            print("✅ Saved category_tree_request_headers.json")

            # Save cookies
            cookies = await context.cookies()
            cookies_filtered = extract_name_value_cookies(cookies, domain_filter="bigbasket.com")
            with open("cookies.json", "w") as f:
                json.dump(cookies_filtered, f, indent=2)
            print("✅ Saved cookies.json")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_bigbasket_data())
