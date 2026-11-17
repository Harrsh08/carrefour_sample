import gzip
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from parsel import Selector
from rich import print

from db_script import CarrefourDB
from utils import (
    get_all_sellers,
    get_category_id,
    get_currency,
    get_delivery_data,
    get_description,
    get_discount_percentage,
    get_highlights,
    get_information,
    get_ingredients,
    get_listing_category,
    get_mrp,
    get_nutrition,
    get_pack_size,
    get_price,
    get_product_brand,
    get_product_category,
    get_product_image_urls,
    get_product_name,
    get_product_sku,
    get_ratings,
    get_review_count,
    get_review_data,
    get_specification,
    get_stock_status,
    get_type,
    get_unit_price,
    get_variations,
    unescape_next_payload,
)

with CarrefourDB() as db:
    product_listing = db.execute_query("""
                    SELECT * FROM product_listing where status='done'
                     """)

def fetch_data(product):
    db_id = product.get('id')
    product_id = product.get('product_id')
    product_type = product.get('product_type')
    ranking = product.get('ranking')
    product_url = product.get('product_url')
    seller_data = json.loads(product.get('other_fields'))

    FOLDER_PATH = './PAGESAVE'

    try:
      file_path = os.path.join(FOLDER_PATH, str(product_id) + ".html.gz")

      with gzip.open(file_path, 'r') as f:
        html_content = f.read()
        print(db_id, 'reading......')

      selector = Selector(body=html_content)

      scripts = selector.xpath(
          "//script[contains(., 'self.__next_f.push')]/text()"
      ).getall()

      content = unescape_next_payload("\n".join(scripts))

      other_sellers = get_all_sellers(html_content.decode('utf-8'))

      item = {
        "master_id": db_id,
        "product_id": product_id,
        "product_sku": get_product_sku(content),
        "product_type": product_type,
        "product_name": get_product_name(content),
        "product_url": product_url,
        "listing_category": get_listing_category(content),
        "product_category": get_product_category(content),
        "brand": get_product_brand(content),
        "ranking": ranking,
        "price": get_price(content),
        "mrp": get_mrp(content),
        "unit_price": get_unit_price(content),
        "availability": get_stock_status(content),
        "sellers": json.dumps(other_sellers, ensure_ascii=False),
        "category_id": get_category_id(content),
        "currency_type": get_currency(content),
        "description": get_description(html_content.decode('utf-8')),
        "discount_percentage": get_discount_percentage(content),
        "highlights": get_highlights(html_content.decode('utf-8')),
        "information": json.dumps(get_information(html_content.decode('utf-8')), ensure_ascii=False),
        "ingredients": get_ingredients(content),
        "get_nutrition": json.dumps(get_nutrition(content), ensure_ascii=False),
        "specification": json.dumps(get_specification(html_content.decode('utf-8')), ensure_ascii=False),
        "images": json.dumps(get_product_image_urls(html_content.decode('utf-8')), ensure_ascii=False),
        "pack_size": get_pack_size(content, html_content.decode('utf-8')),
        "variants": get_variations(html_content.decode('utf-8')),
        "type": get_type(html_content.decode('utf-8')),
        "ratings": get_ratings(html_content.decode('utf-8')),
        "review_count": get_review_count(html_content.decode('utf-8')),
        "review_data": json.dumps(get_review_data(html_content.decode('utf-8')), ensure_ascii=False),
        "frequantly_bought_products": None,
        "pl_seller_data": json.dumps(seller_data, ensure_ascii=False),
        "delivery_data": json.dumps(get_delivery_data(html_content.decode('utf-8')), ensure_ascii=False),
        "offers": None
      }
      return item
    except Exception as e:
      print(str(e))


with CarrefourDB() as db:
  db.execute_query("""
            CREATE TABLE IF NOT EXISTS PDP(
              id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
              master_id BIGINT NOT NULL,
              product_id VARCHAR(255) UNIQUE,
              product_sku VARCHAR(255) NOT NULL,
              product_type VARCHAR(65),
              product_name TEXT,
              product_url TEXT,
              listing_category TEXT,
              product_category VARCHAR(50),
              brand VARCHAR(200),
              ranking INT,
              price DECIMAL(10, 2),
              mrp DECIMAL(10, 2),
              unit_price DECIMAL(10, 2),
              discount_percentage INT,
              availability VARCHAR(100),
              sellers JSON,
              category_id VARCHAR(50),
              currency_type VARCHAR(10) DEFAULT 'AED',
              description TEXT,
              highlights TEXT,
              information JSON,
              ingredients TEXT,
              get_nutrition JSON,
              specification JSON,
              images TEXT,
              pack_size VARCHAR(100),
              variants VARCHAR(100),
              type VARCHAR(100),
              ratings VARCHAR(50),
              review_count INT,
              review_data JSON,
              frequantly_bought_products JSON,
              pl_seller_data JSON,
              offers JSON,
              delivery_data JSON
            )
          """)

with ThreadPoolExecutor(max_workers=10) as executor:
  futures = [
    executor.submit(
     fetch_data, product 
    ) for product in product_listing
  ]

  for future in as_completed(futures):
    response = future.result()
    columns = ["master_id","product_id","product_sku", "product_type", "product_name",
               "product_url", "listing_category", "product_category", "brand", "ranking",
               "price", "mrp", "unit_price", "discount_percentage", "availability", "sellers", "category_id", 
               "currency_type", "description",  "highlights", 
               "information", "ingredients", "get_nutrition", "specification", "images",
               "pack_size", "variants", "type", "ratings", "review_count", "review_data", "frequantly_bought_products", 
               "pl_seller_data", "offers", "delivery_data"]
    
    VALUES = ', '.join(["%s"]*len(columns))

    with CarrefourDB() as db:
      db.execute_query(f"""
                  INSERT INTO PDP ({', '.join(columns)}) VALUES({VALUES})
                """, tuple([response[column] for column in columns]))
      db.execute_query("""
                      UPDATE product_listing SET status=%s WHERE id=%s
                      """, ('read_done', response.get('master_id')))
      print(f"{response.get('master_id')} updated.......")


