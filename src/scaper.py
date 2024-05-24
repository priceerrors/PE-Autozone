from bs4 import BeautifulSoup
import requests, time, json, random

headers = {
    'authority': 'www.autozone.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.autozone.com/performance/plumbing-hosing',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
}

def generate_api_url( url: str) -> list:
    with open("proxies.txt", "r") as file:
        proxies = file.read().splitlines()
    proxy = random.choice(proxies).split(":")
    proxy_dict = {
        "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
    }
    
    catagory_request = requests.get("https://www.autozone.com"+url, headers=headers, proxies=proxy_dict)

    print("https://www.autozone.com"+url+"?recsPerPage=48")
    soup = BeautifulSoup(catagory_request.text, "html.parser")

    taxonomy_prev_path = soup.find("nav", {"class":"st-breadcrumbs az_bob"}).text.lower().replace(",","").replace(" ","-").replace("/","%2F").replace("∕", "%2F").replace("auto-parts", "parts")
    current_group = url.split("/")[-1].replace(",","").replace(" ","-").replace("/","%2F").replace("∕", "%2F")
    taxonomyPath = taxonomy_prev_path+"%2F"+current_group
    canonicalPath = url

    api_url = f"https://www.autozone.com/external/product-discovery/browse-search/v1/product-shelves?country=USA&customerType=B2C&salesChannel=ECOMM&preview=false&canonicalPath={canonicalPath}&pageNumber=[PAGENUMBER]&recordsPerPage=48&taxonomyPath=/{taxonomyPath}&partNumberSearch=false"
    with open("catagory_api_urls.json", "r") as file:
        api_urls = json.load(file)
    api_urls.append(
        {
            "api_url": api_url,
            "original_path": url
        }
    )
    with open("catagory_api_urls.json", "w") as file:
        json.dump(api_urls, file, indent=4)
    print(api_url)


with open("output.txt", "r") as file:
    categories = file.read().splitlines()


for category in categories:
    generate_api_url(category)
    time.sleep(20)
    
# https://www.autozone.com/ecomm/b2c/v1/browse/skus/price/755654,937705,832332,338292,1070711,319458?storeNumber=4461
    