import html
import json
import re
from urllib.parse import urljoin

import jmespath
import requests
from decouple import config
from rich import print

from db_script import CarrefourDB

LISTING_LIMIT = 100

ranking = 1

def clean_text(value):
  if not value:
    return None
  cleaned_text = html.unescape(str(value))
  cleaned_text = cleaned_text.replace("\xa0", " ")
  return re.sub(r"\s+", " ", cleaned_text).strip()

def build_payload(page):
    return json.dumps({
        "needOOSProducts": False,
        "needVariantsData": False,
        "verticalCategory": True,
        "pageType": "SLP",
        "keyword": "shampoo and conditioner",
        "currentPage": page,
        "filter": "",
        "sortBy": "relevance",
        "requireSponsProducts": True,
    })

url = "https://www.carrefouruae.com/mafrp/api/v1/search/listing/keyword?latitude=25.2171003&longitude=55.3613635"

headers = {
  'accept': 'application/json',
  'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
  'access-control-allow-credentials': 'true',
  'appflavour': 'carrefour',
  'appid': 'Reactweb',
  'channel': 'c4online',
  'content-type': 'application/json; charset=utf-8',
  'currency': 'AED',
  'emiratecode': 'DUBAI',
  'env': 'prod',
  'hashedemail': 'anonymous',
  'lang': 'en',
  'langcode': 'en',
  'latitude': '25.2171003',
  'loadbeaconspixel': 'true',
  'longitude': '55.3613635',
  'mw_sellerflex_enabled': 'true',
  'nbinfo': 'true',
  'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6ImE0MzQ5OTg0MDNmMjE1YmMiLCJ0ciI6Ijk4MmE1ODRhYjYyOGI2MDAzMTQ0NjVhZmM2OTYzZGE0IiwidGkiOjE3OTQ1NzE5NDE2NTZ9fQ==',
  'origin': 'https://www.carrefouruae.com',
  'posinfo': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F01_Zone04,QMKP=F04_Zone01',
  'posinfo2': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F01_Zone04|F04_Zone01',
  'priority': 'u=1, i',
  'producttype': 'ANY',
  'referer': 'https://www.carrefouruae.com/mafuae/en/search?currentPage=1&keyword=shampoo+and+conditioner',
  'sec-ch-ua': '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'servicetypes': 'SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL',
  'sessionid': '962A6916-E075-4D5B-8F1D-315F7E5D0F55',
  'storeid': 'mafuae',
  'tabinfo': 'SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY',
  'traceparent': '00-982a584ab628b600314465afc6963da4-a434998403f215bc-01',
  'tracestate': '3355720@nr=0-1-3355720-1134601443-a434998403f215bc----1794571941656',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
  'userid': 'anonymous',
  'visitorid': '962A6916-E075-4D5B-8F1D-315F7E5D0F55',
  'web-view-type': 'desktop-web',
  'x-maf-account': 'carrefour',
  'x-maf-env': 'prod',
  'x-maf-revamp': 'true',
  'x-maf-tenant': 'mafretail',
  'x-requested-with': 'XMLHttpRequest',
   'cookie': config('COOKIES')
}

products = []


for pagination in range(100):
  if len(products) == LISTING_LIMIT:
    break

  payload = build_payload(pagination)
  response = requests.request("POST", url, headers=headers, data=payload)

  if response.status_code == 200:
    product_listings = jmespath.search('data.sections', response.json())
    for product_card in product_listings:
      componentDTO = jmespath.search('componentDTO', product_card)
      product_rating = [jmespath.search('componentDTO.rating.value', card) for card in jmespath.search('productCardComponents', componentDTO) if card.get('uid') == 'product-rating']
      price = jmespath.search('additionalAttributes.sellingPrice', componentDTO)
      mrp = jmespath.search('additionalAttributes.markedPrice', componentDTO)
      item = {
          "product_id": jmespath.search("additionalAttributes.productId", componentDTO),
          "product_type": jmespath.search("additionalAttributes.productType", componentDTO),
          "product_name": clean_text(jmespath.search('additionalAttributes.productName', componentDTO)),
          "ranking": ranking,
          "availibility": jmespath.search('additionalAttributes.stock.stockLevelStatus', componentDTO) == 'inStock',
          "product_url": urljoin("https://www.carrefouruae.com", jmespath.search('additionalAttributes.productUrl', componentDTO)),
          "selling_price": price,
          "original_price": mrp,
          "discount_price": round(mrp - price, 2),
          "discount_percentage": round((mrp - price) / mrp * 100, 2),
          "currency_type": jmespath.search('additionalAttributes.currency', componentDTO),
          "rating": product_rating[0] if product_rating else "",
          "other_fields": {
            "seller_name": jmespath.search('additionalAttributes.shopName', componentDTO),
            "seller_id": jmespath.search('additionalAttributes.shopId', componentDTO),
            "brand_name": jmespath.search('analytics.brandName' ,componentDTO),
            "offerId": jmespath.search('additionalAttributes.offerId', componentDTO)
          } 
      }
      products.append(item)
      ranking += 1

      if len(products) == LISTING_LIMIT:
        break
  else:
    print(response.content)

if products:
  with open('pl_data.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2)

  with CarrefourDB() as db:
    db.execute_query("""
      CREATE TABLE IF NOT EXISTS product_listing(
        id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        product_id VARCHAR(64) NOT NULL,
        product_type VARCHAR(64),
        product_name TEXT,
        ranking INT,
        availability BOOLEAN,
        product_url TEXT,
        selling_price DECIMAL(10, 2),
        original_price DECIMAL(10, 2),
        discount_price DECIMAL(10, 2),
        discount_percentage DECIMAL(10, 2), 
        currency_type VARCHAR(10) DEFAULT 'UAE',
        rating DECIMAL(3, 2) NULL,
        other_fields JSON,
        status VARCHAR(255) DEFAULT 'pending',
        UNIQUE KEY uq_product (product_id)
        )
    """)

    columns = [
            "product_id", "product_type", "product_name", "ranking",
            "availability", "product_url", "selling_price", "original_price",
            "discount_price", "discount_percentage", "currency_type", "rating", "other_fields",
        ]
    
    placeholders = ", ".join(["%s"]* len(columns))
    updates = ", ".join(
      f"{c} = VALUES({c})" for c in columns if c!= "product_id"
    )
    
    rows = [
      (
        p["product_id"], p["product_type"], p["product_name"],
        p["ranking"], p["availibility"], p["product_url"],
        p["selling_price"], p["original_price"], p["discount_price"],
        p["discount_percentage"], p["currency_type"], p["rating"] or None,
        json.dumps(p["other_fields"], ensure_ascii=False)
      ) for p in products
    ]

    db.execute_query(
      f"INSERT INTO product_listing ({', '.join(columns)})"
      f"VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}",
      rows,
      many=True
    )