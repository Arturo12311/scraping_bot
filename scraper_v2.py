import json
import requests
import time
import random
import re

PRICE_WEBHOOK_URL = "https://discord.com/api/webhooks/1318701551958626397/qpwIDxYhowPW3pyK8j65gZIac9yuYQRQSlTry4oehq51hZF_lJuRxca0taAaiLGY9-D3"
STOCK_WEBHOOK_URL = "https://discord.com/api/webhooks/1318750061449969765/G9c7_g5eESXEjYzxEJkhjr963XNnQm4Sa31ELludBrNxn-56MrNOvhrBj0bZhp_fyTqc"
ERROR_WEBHOOK_URL = "https://discord.com/api/webhooks/1318705849169874984/fZukKBD0Mo4dttlmfEi7VtzQAjHVK2HtXib1Cl0reUCMtIb1UpqBtvE1CzEHkq0iymX2"

def load_json(filename, default=None):
    if default is None:
        default = {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def send_notification(webhook_url, message):
    response = requests.post(webhook_url, json={"content": message})
    if response.status_code != 204:
        requests.post(ERROR_WEBHOOK_URL, json={"content": "SCRIPT TERMINATED (FAILED TO SEND NOTIFICATION)"})
        exit()
    else:
        print("NOTIFICATION SENT SUCCESSFULLY!")

def run_scrape():
    links = load_json("links.json", [])
    old_data = load_json("data.json", {})

    print(f"\n-Loaded {len(links)} Links To Scrape-")

    print("\n================================")
    print("INITIALIZING SESSION")

    proxy_url = "http://customer-artur6184_DhSdf-cc-CA:QPalzmalqpalzm_1@pr.oxylabs.io:7777"
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
    print("SCRAPING LINKS")

    data = {}
    count = 0

    for url in links:
        count += 1
        print(f"\n{count}. {url}")

        time.sleep(random.uniform(1, 5))
        response = session.get(url)

        if "We like real shoppers, not robots!" in response.text:
            print("\nFLAGGED")
            send_notification(ERROR_WEBHOOK_URL, "SCRIPT TERMINATED (BOT FLAGGED)")
            exit()

        if "Out of stock" in response.text:
            new_price = None
            data[url] = None
            print("OUT OF STOCK")
        else:
            # Attempt to extract price
            match = re.search(r'"price":\s*([^,]+)', response.text)
            if match:
                new_price = match.group(1)
            else:
                print("PRICE NOT FOUND AND IN STOCK")
                send_notification(ERROR_WEBHOOK_URL, "SCRIPT TERMINATED (PRICE NOT FOUND FOR IN STOCK PRODUCT)")
                exit()

            data[url] = new_price
            print("IN STOCK")
            print(f"Price: {new_price}")

        old_price = old_data.get(url)
        message = None
        webhook_url = None

        # Determine what notification to send (if any)
        if url not in old_data:
            message = f"NOW MONITORING: {url}"
            webhook_url = STOCK_WEBHOOK_URL
            print("MESSAGE")
        else:
            if old_price == data[url]:
                print("NO PRICE CHANGE")
            else:
                # Price changed
                if old_price is not None and data[url] is not None:
                    # Both in stock and price changed
                    webhook_url = PRICE_WEBHOOK_URL
                    message = (f"!!!PRICE CHANGE DETECTED!!!\n\n"
                               f"  OLD PRICE ${old_price} -> NEW PRICE ${data[url]}\n\n  PRODUCT: {url}")
                    print(message)
                else:
                    # Stock change
                    webhook_url = STOCK_WEBHOOK_URL
                    if old_price is None:
                        # Went from out of stock to in stock
                        message = (f"!!!STOCK CHANGE DETECTED!!!\n\n  BACK IN STOCK -> ${data[url]}\n\n  PRODUCT: {url}")
                    else:
                        # Went from in stock to out of stock
                        message = (f"!!!STOCK CHANGE DETECTED!!!\n\n  OUT OF STOCK\n\n  PRODUCT: {url}")
                    print(message)

        if 'Sold and shipped by Walmart' in response.text:
            print("WALMART PRODUCT")
            if message and webhook_url and float(data[url]) < float(old_price):
                send_notification(webhook_url, message)
        else:
            print("THIRD PARTY SELLER")

    data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    save_json('data.json', data)
    print(f"\n-Updated 'data.json'-")

    print("\n-Scraping Cycle Completed-\n")

if __name__ == "__main__":
    while True:
        run_scrape()
        sleep_duration = random.uniform(5*60, 15*60)
        print(f"\n-\nSleeping for {sleep_duration/60:.2f} minutes...\n-\n")
        time.sleep(sleep_duration)
