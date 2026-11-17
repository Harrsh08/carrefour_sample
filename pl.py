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
  'Cookie': '_abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQnPnaF+ctRMShAQAA2rap6BBcl0q39gedvlmV0Gr/4f5mRW4zUEnWyy8oGZe+QQ9jC7zxB1rGyKpPZcDob5ZbbyLaB7fn4Alijb9TNQBect475dFt5PhR3rbj7exvePS6vvYqjwy3hCvQKeLq8I9Ja0GDioVHQwnT9CQBtqA5r1aJTiB8NfuB7vlG7gkh5ZMUX1wiBiyOQIdly6TjFxm4GYvC6TDfnEUrqC9m9O7e/PydlyJXGQwEAF+7G/tVU9a5o5Qk9tpgzi163l36XPrdphU+65OHOWhFLKImY9lDyj9HzxIFVBfWCBqHh7eVEgoB1Pk8uE4KVP3v8ysu3MoIiEcdQouP4F23XyVz8IXMRlISqvonAOZWd1lazE03kV5DYmKGVf/1iPT4GzyceEC3+Ccq9DF0R2Q1nmSMBwvJ+Zz+dC2puNojKqMUGOjRbzz/Aqohlj+rqhYyJNhoZi8Owyl/UrMLztR/fG5a1wr8qDl/QyDCz4PGiI7L5eC9RzlTy1pTmANFdPW5QMz+1BRs1PSSM9wpslhLQNOgD0AVkJI/SfmgxA5cG1bjjc2gIVvs8kiVGixpwNru6IvhwOm59YgCA88d/bTJ182zczsbl8kYJV8su3YA01oUOwP2X1/o1KlcH3dsWan10wKeV9BjNfvmBOPyheAJEC5r9x78vC1G8UJeHIebcGgub3tS4zzTXUbShkBfd9FDu07EontTUJ2MNULQ5raa3/juHhqg1htzqFg0KfXYLYnl40USQxYjEliJH6tl2EZI7IW08V0Cz/UePAeI3GqpBKO7r5iSUeI5oEscC9GsJf42a8OZO+RWyT9fYjBLrbH5I0Og1LlPazPk4LVebrNyL8Jp5k5vAFoBPwdjmANtSnq882aMAPRHkfyV+RTf256+HD11s4a42K0Gh7dwh4LQMQFf1W+yqkn7di7OMak2l8Tow++e8PQBCv3ONBJI9L4PypjlYGiSoZ2acI7s1HTo/INg0/Z+3mu14j5uO93ZJgrBwJmXyNs8MQnNm6Xtf6VZiwgUYGBdiSPmYY9TuiFESKVlcsrvNirR3E//rI6BuHcz/TCTeRG3I7qhA6Lqg8KjwB8abeDyPtl1TwZXocC4FzJhA+05sJLIM+1KBRaFQYbbf2i7EuwCLm0pAQzb1xs4vormZFRIWEqzV9V6Frs6f5JadXHWYr5oZPSgJ52MvgCkEzKTjtY6ObUBNFSHEyu6NLK8PqGq1m5NveE02Q==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f2LzrlboIgQLpoXC84vO%2fE49cQs9MwTSs4utmIx7MlQi2XdxSEt9tzx3gkkXdfBhvOnA0Ph3Uy8bbDfh8mY2UYIxglX%2fWDrXFHg8Y74ZxeLgEHRi94TWpCd+llRRKWcht69gRaQ%3d~-1; bm_s=YAAQnPnaF+gtRMShAQAA2rap6AbK7BUQ1KxSNYXvL0KpMRnYDITWrwlSv2qKar46Ljgl13SgJ1lUgckA7QUmV+jU4/rGeqWpuxDeu5enjnVKTgxdQZtGzAYL1gU6liL2Fy2QpNBf5oFty65ghAG+IaY6r7nNyi90QOmy/WMIV0tssRKvNk1rncQqkI1UbAe/YajLQ4nyb5ZFpyn6RZ5K/1AgFnDXxl39diDNH2oI2ogfdemTOdDqHwoNhpoZfXE56ysfPlwzxPDiCGGGKtaDBpiavD9GGF4OlUUtSJ49Kkj6asPZaxnawoQvLyMmpGXG0NNks1u1OmAPStcRBh402re34IgbKYFBE3P5U0FKMaXZWDcS4bLZsEUUge7t4LT7VatpHp7cJhaXlcLrmi+prEWcGm2I+8JyOxC7lVyU08ARdjj6FjTBN8zyAbc1meLvtlDSkxViNdlCWIv5RgikF4fMpL1Qv7xBPQwsjLcPiAATBzBRWCgR8+ifIkscik0UhMnVcXHNocFqaOkVxMRvW2tCk9dUvjfw+TyVWqJrq6QAqeK+UU3Fxs0Fk45Hl0Fr2EpM33djxdnDCQmc7XwHeNNgUwWVbkyn2SMP9UEQKVtUcbheN7lrnbvkE7LMGDyvkm2D/fmGcrErt4cyQT1dggzUZssysIDqSbx9oj/gvwuCwlyapRd5WNEv44a/fvJGpLsaSc1q5gcXaljnb1+D4WRjmWyXAmPp7E41wQ5/h9Y0EOc3yYkIwVE4Jz+qODPbKyXZe7wNktnSQPQ=; bm_sz=7B3EB4CAF61F9758DDF3501F2230F0C3~YAAQnPnaF+ktRMShAQAA2rap6AFdgwthmi6jFb1you5R3lSKkFE3mZX+gzn7XXU9HjEpw5alYCZFyecA4GM86+mclUtFlwIQrod/UAptv3bYOfXBxGXD1m/t0Maqxlgw0nSnCeLbwm03EyVtbaTc8lcFyvbXhbzdm0yFA61+bLzOaZsoW4gqlRZO0m7t7KvXU/6PFkRkZvS7o8kxRJc1M8R8GeyQnC5O4svb4vk7LkyLldaaDnJVRCjQZzii/wJkQcf/MSOz/dDbl+H4SEVQCjncrC3ORbWoDOXgYFuF/Y6+x4Qj+ekOrToQt3i1IcXF/RHBPeTA01dT6T8RT7FLD7Y2l2tS9Ylzlw2sy1XuCwBbKd+s3bDjnvBmJbASy1o4d1xNLl7BxgKtTA==~4600646~4469043; cart_api=v2'
  }
products = []


for pagination in range(100):
  if len(products) == LISTING_LIMIT:
    break

  payload = build_payload(pagination)
  response = requests.request("POST", url, headers=headers, data=payload)

  if response.status_code == 200:
    with open(f"./PAGESAVE/shampoo_and_conditioner_{pagination}.html", 'wb') as f:
      f.write(response.content)
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