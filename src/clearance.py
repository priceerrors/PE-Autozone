from utility import header_gen, database
from bs4 import BeautifulSoup
import requests, time, json, random, math 
from typing import List

import discord_handler



class ScrapeCatagory:
    def __init__(self) -> None:
        self.products_list = [ ]
        self.sale_products_list = [ ]
        self.headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'accept-language': 'en-US,en;q=0.9','cache-control': 'max-age=0', 'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'}
        self.cookies = {'eCookieId': f"{self.generate_cookie_id()}",}


    
    def generate_cookie_id(self) -> str:
        """Generates a random cookie id for the request"""
        return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=16))



    def main_handler(self) -> None:
        print(f"[Autozone] Starting Scrape on Clearance")
        # Send the inital request to the base catagory url
        with open("../database/proxies.txt", "r") as proxies_file:
            proxies_list = proxies_file.readlines()
        # Split the proxy and format it accordingly
        proxy = random.choice(proxies_list).replace( "\n", "").split(":")
        resources_proxy_dict = {
            "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        }

        try:
            inital_request = requests.get(f"https://www.autozone.com/external/product-discovery/browse-search/v1/product-shelves?country=USA&customerType=B2C&salesChannel=ECOMM&preview=false&canonicalPath=%2Fdeals%2Fclearance&pageNumber=1&recordsPerPage=48&storeId=4973&ruleTags=CLEARANCE&isLandingPage=true", headers=self.headers, cookies=self.cookies, proxies=resources_proxy_dict, timeout=10)
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
            products = self.request_api_base(f"https://www.autozone.com/external/product-discovery/browse-search/v1/product-shelves?country=USA&customerType=B2C&salesChannel=ECOMM&preview=false&canonicalPath=%2Fdeals%2Fclearance&pageNumber={page}&recordsPerPage=48&storeId=4973&ruleTags=CLEARANCE&isLandingPage=true", self.headers)
            time.sleep(2)

            if products == None: print(f"{page} Has Unavalible Products")
            else: self.save_product_data(products)

            print(f"Scraping Page {page}/{total_pages+1}")
        
        self.generate_product_pricing()
        print(f"[Autozone] Found {len(self.sale_products_list)} Products on Clearance")

        self.check_duplicates()

        for product in self.sale_products_list:
            discord_handler.send_webhook(product)
    




    def check_duplicates(self) -> None:
        """This function checks for duplicates in the products list and removes them"""
        with open("../database/sent_products.json", "r") as saved_products_file:
            saved_products_data = json.load(saved_products_file)
        
        skus_list = saved_products_data.keys()

        for product in self.sale_products_list:
            if product["sku"] in skus_list:

                if saved_products_data[product["sku"]] == product["price"]:
                    self.sale_products_list.remove(product)
                    print(f"[Autozone] Product {product['sku']} Already Exists | Same Price | Removing")

                elif saved_products_data[product["sku"]] != product["price"]:
                    saved_products_data[product["sku"]] = product["price"]
                    print(f"[Autozone] Product {product['sku']} Already Exists | Different Price | Updating")

            else:
                saved_products_data[product["sku"]] = product["price"]
                print(f"[Autozone] Product {product['sku']} Added to Database")
        
        with open("../database/sent_products.json", "w") as saved_products_file:
            json.dump(saved_products_data, saved_products_file, indent=4)





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

        # Batch the product skus into groups of 24
        batched_skus = [product_skus_querry[i:i+24] for i in range(0, len(product_skus_querry), 24)]

        # Iterate through each batch and make the pricing API request
        for batch in batched_skus:
            pricing_api_url = f"https://www.autozone.com/ecomm/b2c/browse/v3/skus/price-availability/{','.join(batch)}"
            pricing_response = requests.get(pricing_api_url, headers=self.headers, cookies=self.cookies, proxies=resources_proxy_dict, timeout=10)

            for index, product in enumerate(pricing_response.json()):
                for p in self.products_list:
                    if p["sku"] == product['skuPricingAndAvailability']["skuId"]:
                        p["price"] = product['skuPricingAndAvailability']["retailPrice"]
                        
                        if not product['skuPricingAndAvailability']['wasRetailPrice'] == None:
                            p['old_price'] = product['skuPricingAndAvailability']['wasRetailPrice']
                            p['shipping_quantity'] = product['availabilityInfoVO']['sthQuantity']
                            self.sale_products_list.append(p)
            time.sleep(2)

                

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



ScrapeCatagory().main_handler()


# https://www.autozone.com/external/product-discovery/browse-search/v1/product-shelves?country=USA&customerType=B2C&salesChannel=ECOMM&preview=false&canonicalPath=%2Fdeals%2Fclearance&pageNumber=1&recordsPerPage=24&storeId=4973&ruleTags=CLEARANCE&isLandingPage=true