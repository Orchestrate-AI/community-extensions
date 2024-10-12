import os
import json
import asyncio
from redis.asyncio import Redis
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time
import random
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

def connect_to_redis():

    return Redis.from_url(
        REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

def scrape_zillow(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.zillow.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    session = requests.Session()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Add a random delay between requests
            time.sleep(random.uniform(1, 3))
            
            response = session.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            debug_html = response.text
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Update the selector to target the correct container
            listings_container = soup.find('ul', {'class': 'List-c11n-8-84-3__sc-1smrmqp-0'})
            
            if not listings_container:
                print("Listings container not found. The page structure might have changed.")
                return [], debug_html

            listings = []
            
            # Update the selector to target individual listing items
            for item in listings_container.find_all('li', {'class': 'ListItem-c11n-8-84-3__sc-10e22w8-0'}):
                # Extract address
                address_elem = item.find('address')
                address = address_elem.text.strip() if address_elem else "Address not found"
                
                # Extract price
                price_elem = item.find('span', {'data-test': 'property-card-price'})
                price = price_elem.text.strip() if price_elem else "Price not found"
                
                # Extract bedrooms and bathrooms
                details_elem = item.find('ul', {'class': 'StyledPropertyCardHomeDetailsList-c11n-8-84-3__sc-1xvdaej-0'})
                beds = baths = "N/A"
                if details_elem:
                    beds_elem = details_elem.find('li', {'data-test': 'property-card-bed'})
                    baths_elem = details_elem.find('li', {'data-test': 'property-card-bath'})
                    beds = beds_elem.text.strip() if beds_elem else "N/A"
                    baths = baths_elem.text.strip() if baths_elem else "N/A"
                
                listings.append({
                    'address': address,
                    'price': price,
                    'beds': beds,
                    'baths': baths
                })
            
            return listings, debug_html

        except RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                raise

    return [], "Max retries reached. Unable to fetch data."

def scrape_zillow_with_selenium(zipcode, min_price, max_price):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    search_query_state = {
        "pagination": {},
        "isMapVisible": True,
        "mapBounds": {
            "north": 33.79679084216046,
            "south": 33.74449244976123,
            "east": -84.2613748383789,
            "west": -84.32660616162109
        },
        "filterState": {
            "sort": {"value": "globalrelevanceex"},
            "price": {"min": min_price, "max": max_price},
            "mp": {"min": min_price // 203, "max": max_price // 203}  # Approximate monthly payment
        },
        "isListVisible": True,
        "mapZoom": 14,
        "regionSelection": [{"regionId": 70815, "regionType": 7}]
    }
    
    url = f"https://www.zillow.com/{zipcode}/?searchQueryState={json.dumps(search_query_state)}"
    driver.get(url)

    # Wait for the page to load
    time.sleep(random.uniform(3, 5))

    # Extract listing information
    listings = []
    listing_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test='property-card-container']"))
    )
    
    for element in listing_elements:
        try:
            address = element.find_element(By.CSS_SELECTOR, "[data-test='property-card-addr']").text
            price = element.find_element(By.CSS_SELECTOR, "[data-test='property-card-price']").text
            details = element.find_element(By.CSS_SELECTOR, "[data-test='property-card-details']").text
            link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            
            listings.append({
                "address": address,
                "price": price,
                "details": details,
                "link": link
            })
        except Exception as e:
            print(f"Error extracting listing: {str(e)}")
            continue

    driver.quit()
    return listings

async def process_message(message):
    data = json.loads(message)
    inputs = data['inputs']
    zipcode = inputs['zipcode']
    min_price = inputs['min_price']
    max_price = inputs['max_price']

    listings, debug_html = scrape_zillow(url=f"https://www.zillow.com/homes/{zipcode}_rb/")

    return {
        'listings': listings,
        'count': len(listings),
        'debug_html': debug_html
    }

async def main():
    redis = Redis.from_url(
        REDIS_HOST_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )

    await redis.publish(REDIS_CHANNEL_READY, '')

    pubsub = redis.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL_IN)

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                result = await process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
            except Exception as e:
                output = {
                    "type": "failed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "error": str(e)
                }
            
            await redis.publish(REDIS_CHANNEL_OUT, json.dumps(output))
            await redis.close()
            break

    await pubsub.unsubscribe(REDIS_CHANNEL_IN)
    await redis.close()

if __name__ == "__main__":
    asyncio.run(main())
