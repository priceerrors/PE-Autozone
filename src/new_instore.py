from utility import header_gen, database
from bs4 import BeautifulSoup
import requests, time, json, random, math 
from typing import List

import discord_handler



class ScrapeCatagory:
    def __init__(self) -> None:
        self.products_list = [ ]
        self.headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'accept-language': 'en-US,en;q=0.9','cache-control': 'max-age=0', 'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'}
        self.cookies = {'eCookieId': f"{self.generate_cookie_id()}",}


    
    def generate_cookie_id(self) -> str:
        """Generates a random cookie id for the request"""
        return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=16))



    def main_handler(self, base_catagory_url: str, api_url: str) -> None:
        print(f"[Autozone] Starting Scrape on {base_catagory_url}")
        # Send the inital request to the base catagory url
        with open("../database/proxies.txt", "r") as proxies_file:
            proxies_list = proxies_file.readlines()
        # Split the proxy and format it accordingly
        proxy = random.choice(proxies_list).replace( "\n", "").split(":")
        resources_proxy_dict = {
            "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        }

        try:
            inital_request = requests.get(api_url.replace("[PAGENUMBER]","1"), headers=self.headers, cookies=self.cookies, proxies=resources_proxy_dict, timeout=10)
        except Exception as e:
            print(e)
        # Add the products from the inital request to the products list
        self.save_product_data(inital_request.json()["productShelfResults"]["skuRecords"])
        
        # Now we extract critial information from the inital request to continue the scraping process
        self.total_products = inital_request.json()["productShelfResults"]["totalNumberOfRecords"]
        total_pages = math.ceil(int(self.total_products) // 48)

        if total_pages > 10: total_pages = 10
        # Iterate through the pages gathering products
        for page in range(2, total_pages + 2):
            products = self.request_api_base(api_url.replace("[PAGENUMBER]", str(page)), self.headers)
            time.sleep(2)

            if products == None: print(f"{page} Has Unavalible Products")
            else: self.save_product_data(products)

            print(f"{page}/{total_pages+1}")
        
        if self.generate_product_pricing() == None:
            pass
        else:
            print(f"[Autozone] Uploading {len(products)} Products to Database")
            for product in self.products_list:
                database.save_product(product)

    def generate_product_pricing(self) -> None:
        """This function makes calls to the product pricing API to get the pricing for each product"""
        # Sending requests for 128 products at a time
        with open("../database/proxies.txt", "r") as proxies_file:
            proxies_list = proxies_file.readlines()
        # Split the proxy and format it accordingly
        proxy = random.choice(proxies_list).replace( "\n", "").split(":")
        resources_proxy_dict = {
            "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        }

        product_skus_querry = [product["sku"] for product in self.products_list]
        
        pricing_api_url = f"https://www.autozone.com/ecomm/b2c/v1/browse/skus/price/{','.join(product_skus_querry)}?storeNumber=4461"
        pricing_response = requests.get(pricing_api_url, headers=self.headers, cookies=self.cookies, proxies=resources_proxy_dict, timeout=10)
        
        if "Internal Server Error" in pricing_response.text:
            print("Internal Server Error")
            return None
        elif "Access Denied" in pricing_response.text:
            print("Access Denied")
            return None

        print("[Auzozone] Requesting Pricing")

        try:

            for index, product in enumerate(pricing_response.json()):
                if self.products_list[index]["sku"] == product["skuId"]:
                    self.products_list[index]["price"] = product["retailPrice"]
                else:
                    print("Error indexing price")
        except:
            print(pricing_response.text)
        
                

    def save_product_data(self, product_data: List[dict]) -> None:
        """This function saves the nessary product data to the products_list"""
        for product in product_data:
            self.products_list.append(
                {
                    "sku": product["itemId"],
                    "name": product["itemDescription"],
                    "part_number": product["partNumber"],
                    "image": product["itemImageUrl"].replace("https", "http"),
                    "product_url": product["productDetailsPageUrl"]
                }
            )


    def request_api_base(self, api_url: str, headers: dict) -> None:
        with open("../database/proxies.txt", "r") as proxies_file:
            proxies_list = proxies_file.readlines()
        # Split the proxy and format it accordingly
        proxy = random.choice(proxies_list).replace( "\n", "").split(":")
        resources_proxy_dict = {
            "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        }
        api_response = requests.get(api_url, headers=headers, cookies=self.cookies, proxies=resources_proxy_dict, timeout=10)
        try:
            api_data = api_response.json()
        except:
            print("No API Json Data")
            return None

        api_data = api_data["productShelfResults"]["skuRecords"]

        return api_data
        


database = database.DatabaseHandler()

while True:

    with open("catagory_api_urls.json", "r") as json_file:
        json_data = json.load(json_file)

    data = random.choice(json_data)


    ScrapeCatagory().main_handler(data["original_path"], data["api_url"])