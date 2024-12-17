import json
import requests
import time
import random
import re

WEBHOOK_URL = "https://discord.com/api/webhooks/1318701551958626397/qpwIDxYhowPW3pyK8j65gZIac9yuYQRQSlTry4oehq51hZF_lJuRxca0taAaiLGY9-D3"
ERROR_WEBHOOK_URL = "https://discord.com/api/webhooks/1318705849169874984/fZukKBD0Mo4dttlmfEi7VtzQAjHVK2HtXib1Cl0reUCMtIb1UpqBtvE1CzEHkq0iymX2"

def run_scrape():
    with open("links.json") as f:
        links = json.load(f)
    print(f"\n-Loaded {len(links)} Links To Scrape-")

    try:
        with open("data.json", "r") as f:
            old_data = json.load(f)
    except FileNotFoundError:
        old_data = {}

    print("\n================================")
    print("INITIALIZING SESSION")

    proxy_url = f"http://customer-artur6184_DhSdf-cc-CA:QPalzmalqpalzm_1@pr.oxylabs.io:7777"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    print(f"\nProxy URL: {proxy_url}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.walmart.ca/search?q=pokemon",
        "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"99\", \"Google Chrome\";v=\"115\", \"Chromium\";v=\"115\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1"
    })
    session.proxies = proxies
    response = session.get("https://ipinfo.io/json")

    print("\nProxy Test:", response.text)

    print("\n-Session Initialized-")

    print("\n================================")
    print(f"SCRAPING LINKS")

    data = {}
    count = 0

    for url in links:
        count += 1

        print(f"\n{count}. {url}")

        sleep_duration = random.uniform(1, 5)
        time.sleep(sleep_duration)

        response = session.get(url)

        if "We like real shoppers, not robots!" in response.text:
            print("\nFLAGGED")
            requests.post(ERROR_WEBHOOK_URL, json={"content": "SCRIPT TERMINATED (BOT FLAGGED)"})
            exit()
        elif "Out of stock" in response.text:
            new_price = None
            data[url] = None
            print("OUT OF STOCK")
        else:
            pattern = r'"price":\s*([^,]+)'
            match = re.search(pattern, response.text)
            if match:
                new_price = match.group(1)
            else: 
                print("PRICE NOT FOUND AND IN STOCK")
                requests.post(ERROR_WEBHOOK_URL, json={"content": "SCRIPT TERMINATED (PRICE NOT FOUND FOR IN STOCK PRODUCT)"})
                exit()

            data[url] = new_price
            print("IN STOCK")
            print(f"Price: {new_price}")

        if url not in old_data:
            message = f"NOW MONITORING: {url}"
            print("MESSAGE")
        elif old_data[url] == data[url]:
            message = None
            print("NO PRICE CHANGE")
        else:
            message = f"!!!PRICE CHANGE DETECTED!!!\n\n  OLD PRICE {old_data[url]} -> NEW PRICE {data[url]}\n\n  PRODUCT: {url}"
            print(message)

        if message:
            response = requests.post(WEBHOOK_URL, json={"content": message})
            if response.status_code == 204:
                print("NOTIFICATION SENT SUCCESSFULLY!")
            else:
                print("FAILED TO SEND NOTIFICATION")
                requests.post(ERROR_WEBHOOK_URL, json={"content": "SCRIPT TERMINATED (FAILED TO SEND NOTIFICATION)"})
                exit()

    data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open('data.json', "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n-Updated 'data.json'-")

    print("\n-Scraping Cycle Completed-\n")

if __name__ == "__main__":
    while True:
        run_scrape()
        sleep_duration = random.uniform(5*60, 15*60)
        print(f"\n-\nSleeping for {sleep_duration/60:.2f} minutes...\n-\n")
        time.sleep(sleep_duration)
