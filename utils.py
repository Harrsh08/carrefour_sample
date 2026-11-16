import html as html_lib
import html as html_module
import json
import os
import re
from urllib.parse import urljoin

import requests
from parsel import Selector

RE_MAIN  = r'\\"sellerDetails\\":(\{.*?\\"isStoreFront\\":\w+\})'
RE_OTHER = r'\\"otherSellers\\":(\[.*?\])\}\}'
RE_PRICE = r'\\"PriceDetails\\".*?\\"finalPrice\\":\\"([\d.]+)\\"'
RE_OFFER = r'\\"offerId\\":\\"([^\\]*)\\"'

def unescape(raw):
    # raw is inside a JS string: decode the escapes first, then parse the JSON
    return json.loads(json.loads('"' + raw + '"'))

def get_all_sellers(html):
    sellers = []

    # main seller (Carrefour or whoever the default seller is)
    m = re.search(RE_MAIN, html, re.S)
    if m:
        d = unescape(m.group(1))
        price = re.search(RE_PRICE, html, re.S)
        offer = re.search(RE_OFFER, html)
        sellers.append({
            "type": "main",
            "sellerId": d["sellerID"],
            "sellerName": d["sellerName"].strip("*"),
            "offerId": offer.group(1) if offer else None,
            "price": price.group(1) if price else None,
            "rating": d.get("ratingSummary", {}).get("averageRating", 'N/A'),
            "deliveryPromise": None,
        })

    # other sellers
    m = re.search(RE_OTHER, html, re.S)
    if m:
        for s in unescape(m.group(1)):
            sellers.append({
                "type": "other",
                "sellerId": s["sellerId"],
                "sellerName": s["sellerName"],
                "offerId": s["offerId"],
                "price": s["price"]["finalPrice"],
                "rating": None,
                "deliveryPromise": s.get("deliveryPromise"),
            })
    return sellers
  
# with open("test.html", 'r', encoding='utf-8') as f:
#   html = f.read()

# for s in get_all_sellers(html):
#     print(s)


def unescape_next_payload(script_text: str) -> str:
    """Extract every self.__next_f.push([1, "...")]) payload and flatten
    all escaping so plain "key":"value" regexes match correctly."""
    cleaned_parts = []
    pattern = re.compile(r'self\.__next_f\.push\(\[1,\s*"((?:\\.|[^"\\])*)"\]\)', re.DOTALL)

    for payload in pattern.findall(script_text):
        try:
            decoded = json.loads(f'"{payload}"')
        except json.JSONDecodeError:
            continue

        # strip the leading "<chunk id>:" prefix, e.g. "7:[[...]]"
        decoded = re.sub(r'^[0-9a-fA-F]+:', '', decoded, count=1)

        decoded = decoded.replace('\\"', '"')

        cleaned_parts.append(decoded)

    return "\n".join(cleaned_parts)


def get_product_id(html):
    match = re.search(r'"productId"\s*:\s*"([^"]+)"', html)
    return match.group(1) if match else 'N/A'


def get_product_name(html):
    match = re.search(r'"productTitle"\s*:\s*"([^"]+)"', html)
    return match.group(1) if match else 'N/A'


def get_product_brand(html):
    match = re.search(r'"brandStockDetails"\s*:\s*\{(.*?)\}', html, re.DOTALL)
    if match:
        name_match = re.search(r'"brandName"\s*:\s*"([^"]+)"', match.group(1))
        if name_match:
            return name_match.group(1)

    match = re.search(r'"brand"\s*:\s*\{(.*?)\}', html, re.DOTALL)
    if match:
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', match.group(1))
        if name_match:
            return name_match.group(1)

    match = re.search(r'"brand"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1)

    match = re.search(r'"brandName"\s*:\s*"([^"]+)"', html)
    return match.group(1) if match else 'N/A'



def get_product_image_urls(html):
    """Extract just the product image URLs (PRIMARY + GALLERY), in order."""

    image_html = Selector(text=html).xpath("//div[@data-testid='ProductImageThumbnails-container']")[0].xpath(".//img/@src").getall()
    if not image_html:
        image_html = Selector(text=html).xpath(
            "//div[@data-testid='ProductImageThumbnails-container']")[0].xpath(".//button//@src").getall()

    urls = [image.split("?")[0] for image in image_html]
    return ' | '.join(urls)



def get_product_sku(html):
    match = re.search(r'"sku"\s*:\s*"([^"]+)"', html)
    return match.group(1) if match else 'N/A'


def get_product_category(html):
    match = re.search(r'"productCategory"\s*:\s*"([^"]+)"', html)
    return match.group(1) if match else 'N/A'


def get_listing_category(html):
    match = re.search(r'"breadCrumbs":\[(.*?)\]\}\]', html, re.DOTALL)
    if not match:
        match = re.search(r'"breadCrumbs":\[(.*?)\]', html, re.DOTALL)
    if match:
        names = re.findall(r'"name"\s*:\s*"([^"]+)"', match.group(1))
        return " | ".join(names) if names else 'N/A'
    return 'N/A'


def get_price(html):
    match = re.search(
        r'"componentDTO"\s*:\s*\{\s*"price"\s*:\s*\{[^}]*?"finalPrice"\s*:\s*"([^"]+)"',
        html
    )
    return match.group(1) if match else 'N/A'

def get_unit_price(html):
    # Match unitPrice only when it has a non-empty quoted value
    match = re.search(
        r'"unitPrice"\s*:\s*"([^"]+)"\s*,\s*"unitPriceMeasureText"\s*:\s*"[^"]*"',
        html
    )
    if match:
        return match.group(1)

    # Reverse key order
    match = re.search(
        r'"unitPriceMeasureText"\s*:\s*"[^"]*"\s*,\s*"unitPrice"\s*:\s*"([^"]+)"',
        html
    )
    if match:
        return match.group(1)

    return 0


def get_mrp(html):
    match = re.search(
        r'"componentDTO"\s*:\s*\{\s*"price"\s*:\s*\{[^}]*?"originalPrice"\s*:\s*"([^"]+)"',
        html
    )
    return match.group(1) if match else get_price(html)



def get_pack_size(html, html_content=None):
    # 1) Preferred: direct "Pack Size" field from productInformation
    #    (this regex requires a quoted value, so "Pack Size":null won't
    #    match and we correctly fall through to the next options below)
    match = re.search(r'"Pack Size"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1)

    # 2) Some products give an approximate count instead, e.g.
    # "productInformation":{"Origin":"Pakistan","Approx":"2PCS","Pack Size":null,...}
    match = re.search(r'"Approx"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1)

    # 3) Others only have a "unit" object instead, e.g.
    # "unit":{"unitOfMeasure":"Kilo","itemsPerUnit":2,"incrementBy":0.5,"size":null}
    match = re.search(r'"unit"\s*:\s*\{(.*?)\}', html, re.DOTALL)
    if match:
        unit_block = match.group(1)

        # If "size" is set directly (not null), just use that
        size_match = re.search(r'"size"\s*:\s*"([^"]+)"', unit_block)
        if size_match:
            return size_match.group(1)

        # Otherwise build it from itemsPerUnit + unitOfMeasure
        items_match = re.search(r'"itemsPerUnit"\s*:\s*([\d.]+)', unit_block)
        uom_match = re.search(r'"unitOfMeasure"\s*:\s*"([^"]+)"', unit_block)
        if items_match and uom_match:
            uom_map = {
                'kilo': 'kg', 'kilogram': 'kg', 'kg': 'kg',
                'litre': 'ltr', 'liter': 'ltr', 'ltr': 'ltr',
                'gram': 'g', 'g': 'g',
                'millilitre': 'ml', 'milliliter': 'ml', 'ml': 'ml',
                'piece': 'pc', 'pieces': 'pc', 'pc': 'pc',
            }
            uom = uom_map.get(uom_match.group(1).lower(), uom_match.group(1))

            items = float(items_match.group(1))
            items_str = str(int(items)) if items == int(items) else str(items)

            return f"{items_str}{uom}"
    else:
        if html_content:
            size = Selector(html_content).xpath("//span[contains(text(), 'Size')]/following-sibling::span//text()").get() 
            if size:
                size = size.strip()
            return size or "N/A"
        else:
            return 'N/A'
    
def get_variations(html_content):
    variations = Selector(html_content).xpath("//span[contains(text(), 'Variants')]/following-sibling::span//text()").get()
    if variations:
        variations = variations.strip()
    return variations or 'N/A'

def get_type(html_content):
    type = Selector(html_content).xpath("//span[contains(text(), 'Type')]/following-sibling::span//text()").get()
    if type:
        type = type.strip()
    return type or 'N/A'


def get_discount_percentage(html):
    match = re.search(
        r'"componentDTO"\s*:\s*\\?\{\s*'
        r'"price"\s*:\s*\\?\{.*?'
        r'"discountPercentage"\s*:\s*\\?"([\d.]+)',
        html,
        re.DOTALL
    )
    return match.group(1) if match else '0'


def get_category_id(html):
    match = re.search(r'"categories"\s*:\s*\[(.*?)\]', html)
    if match:
        cats = re.findall(r'"([^"]+)"', match.group(1))
        return cats[-1] if cats else 'N/A'
    return 'N/A'


def get_currency(html):
    match = re.search(r'"priceCurrency"\s*:\s*"([^"]+)"', html)
    return match.group(1) if match else 'N/A'


def get_description(html):
    selector = Selector(text=html)
    description = (
        selector.xpath("//div[contains(text(), 'Description')]/following-sibling::div//text()").getall()
    )
    return ', '.join(description)



def get_highlights(html):
    selector = Selector(text=html)
    highlights = (
        selector.xpath("//div[contains(text(), 'Highlights')]/following-sibling::div//text()").getall()
    )

    return ', '.join(highlights) if highlights else 'N/A'


def get_ratings(html):
    ratings = Selector(html).xpath("//div[contains(text(), 'Ratings & Review')]/following-sibling::div//div[@class='text-6xl leading-10 font-bold']//text()").get()
    return ratings or "N/A"

with open('test.html', 'r', encoding='utf-8') as f:
    htmla = f.read()


def get_review_count(html):
    review_count = Selector(html).xpath("//div[contains(text(), 'Ratings & Review')]/following-sibling::div//a/text()").get()
    if review_count:
            review_count = review_count.replace('Verified Ratings', '').strip() 
    return review_count or 0


def get_review_data(html):
    review_data = []
    reviews = Selector(html).xpath("//div[contains(text(), 'Ratings & Review')]/parent::div/following-sibling::div[@class='flex w-full flex-col py-2xs']")
    for review in reviews:
        review_data.append({
            "user_name": review.xpath(".//span[@class='text-md leading-5 font-regular']/text()").get(),
            "review_date": ''.join(review.xpath(".//span[@class='text-md leading-5 font-regular text-gray-600']//text()").getall()).replace('|','').strip(),
            "description": review.xpath(".//div[@class='text-md leading-5 font-regular line-clamp-1 text-left']//text()").get()
        })
    
    return review_data 

print(get_review_data(htmla))


def _clean(text):
    """Clean scraped text and fix Unicode/HTML encoding."""
    if not isinstance(text, str):
        return text

    text = text.strip()

    # Decode escaped Unicode
    if '\\' in text:
        try:
            text = json.loads(f'"{text}"')
        except (json.JSONDecodeError, ValueError):
            pass

    # Fix UTF-8 decoded as Latin-1/CP1252
    try:
        if 'Â' in text or 'Ã' in text:
            text = text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    text = html_module.unescape(text)

    return re.sub(r'\s+', ' ', text).strip()




def get_ingredients(html_text):
    match = re.search(r'"ingredientText"\s*:\s*"([^"]+)"', html_text)

    if match:
        data = match.group(1)
        if "$" not in data:
            return _clean(data) if match else 'N/A'
    else:
        ref_match = re.search(
            r'"ingredientText"\s*:\s*"\$([^"]+)"',
            html_text
        )

        if not ref_match:
            return 'N/A'

        ref = ref_match.group(1)

        value_match = re.search(
            rf'{re.escape(ref)}:T[^,]*,(.*?)(?=[a-zA-Z0-9]+:T|[a-zA-Z0-9]+:\{{)',
            html_text,
            re.DOTALL
        )

        if not value_match:
            return 'N/A'

        return _clean(value_match.group(1))

    return 'N/A'


# 1. Flight chunks: self.__next_f.push([1,"...."])
_PUSH = re.compile(r'self\.__next_f\.push\(\[\s*1\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]\)')
# 2. A flight reference such as "$103"
_REF = re.compile(r'^\$([0-9a-f]+)$')
# 3. Start of a flight row: "103:" (hex id + colon)
_ROW_ID = re.compile(rb'([0-9a-f]+):')
_JSON = json.JSONDecoder(strict=False)
# Structural anchor for the info panel - present for every brand/product,
# unlike any single field name.
_INFO_ANCHOR = '"infoMap"'
_MAX_REF_HOPS = 5
def _clean(text) -> str:
    text = html_lib.unescape(str(text)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()
def _unescape_strict(s, chunk_index=None):
    try:
        return json.loads(f'"{s}"')
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Chunk {chunk_index} failed to unescape cleanly ({e}); "
            f"downstream byte offsets will be corrupted"
        ) from e
def _payload_strict(html_text: str) -> str:
    """Join and decode all flight chunks; raise rather than silently corrupt."""
    parts = [_unescape_strict(c, i) for i, c in enumerate(_PUSH.findall(html_text))]
    return "".join(parts) or html_text
def _parse_rows(payload: str) -> dict:
    """
    Split the flight stream into {row_id: value}.
      JSON row:  103:{...}\\n
      Text row:  103:T1a4,<text>   (hex length in BYTES, no newline after the text)
    """
    data = payload.encode("utf-8")
    rows, pos, n = {}, 0, len(data)
    while pos < n:
        if data[pos:pos + 1] == b"\n":
            pos += 1
            continue
        m = _ROW_ID.match(data, pos)
        if not m:  # not a row start, skip this line
            nl = data.find(b"\n", pos)
            if nl == -1:
                break
            pos = nl + 1
            continue
        row_id, pos = m.group(1).decode(), m.end()
        if data[pos:pos + 1] == b"T":  # text row
            comma = data.find(b",", pos)
            length = int(data[pos + 1:comma], 16)
            start = comma + 1
            rows[row_id] = data[start:start + length].decode("utf-8", "replace")
            pos = start + length
        else:  # JSON row (I[...], HL[...] fail and are skipped)
            nl = data.find(b"\n", pos)
            nl = n if nl == -1 else nl
            try:
                rows[row_id] = _JSON.decode(data[pos:nl].decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            pos = nl + 1
    return rows
def _resolve(value, rows: dict):
    """Follow a chain of "$xx" refs (up to _MAX_REF_HOPS) until a real value."""
    for _ in range(_MAX_REF_HOPS):
        if isinstance(value, str) and (m := _REF.match(value)):
            value = rows.get(m.group(1))
        else:
            break
    return value

def get_information(html_text: str) -> dict:
    information = {}
    information_selector = Selector(html_text).xpath("//div[contains(text(), 'Information')]/following-sibling::div")
    for component in information_selector.xpath('./b'):
        information[component.xpath('./text()').get()] = component.xpath('./following-sibling::p//text()').get()
    
    return information  



def get_specification(html_text):
    specification = {}
    specification_components = Selector(html_text).xpath("//div[contains(text(), 'Product Specification')]/following-sibling::div//div[@class='flex flex-row gap-xl']")

    for compoenent in specification_components:
        key = compoenent.xpath("./div[@class='text-sm leading-4 font-regular w-full text-nightblack']//text()").get().strip()
        value = compoenent.xpath("./div[@class='text-sm leading-4 font-bold w-full text-nightblack']//text()").get().strip()
        specification[key] = value
    
    return specification

    

def get_delivery_data(html_text):
    delivery_data = {}
    delivery_component = Selector(html_text).xpath("//div[contains(text(), 'Get It Delivered By')]/parent::div/following-sibling::div//div[@class='text-left']")
    if delivery_component:
        delivery_data[delivery_component.xpath("./div[@class='text-sm leading-4 font-regular italic']//text()").get().strip()] = delivery_component.xpath("./div[@class='text-sm leading-4 font-bold italic']//text()").get().strip()
    else:
        delivery_data['Get It Delivered By'] = delivery_component = Selector(html_text).xpath("//div[contains(text(), 'Get It Delivered By')]/parent::div/following-sibling::p//text()").get().strip()
        
    return delivery_data 


def get_nutrition(html_text):
    match = re.search(
        r'"nutritionFactHeader".*?"features":\[(.*?)\]\}\]\}\}\}',
        html_text,
        re.DOTALL
    )
    if not match:
        return {}
    nutrition_text = match.group(1)
    pairs = re.findall(
        r'"featureKey"\s*:\s*"([^"]+)"\s*,\s*"featureValue"\s*:\s*"([^"]+)"',
        nutrition_text
    )
    return {_clean(k): _clean(v) for k, v in pairs}

def get_product_link(html):
    # Preferred: "productUrl":{"href":"/mafuae/en/tomato/tomato-ep/p/1767482","rel":"self",...}
    # href is relative, so join it against the site's base URL.
    match = re.search(r'"productUrl"\s*:\s*\{(.*?)\}', html, re.DOTALL)
    if match:
        href_match = re.search(r'"href"\s*:\s*"([^"]+)"', match.group(1))
        if href_match:
            return urljoin("https://www.carrefouruae.com/", href_match.group(1))

    # Fallback: absolute link from the schema.org JSON-LD block
    match = re.search(r'"url"\s*:\s*"(https://www\.carrefouruae\.com/mafuae/en/p/[^"]+)"', html)
    return match.group(1) + "?offer=offer_carrefour_&sid=SLOTTED&sellerId=0000" if match else 'N/A'


def get_stock_status(html):
    # "availability":"https://schema.org/InStock" or ".../OutOfStock"
    match = re.search(r'"availability"\s*:\s*"[^"]*schema\.org/([A-Za-z]+)"', html)
    if match:
        avail = match.group(1).lower()
        if avail == 'instock':
            return 'TRUE'
        if avail == 'outofstock':
            return 'FALSE'
        return match.group(1)  # e.g. LimitedAvailability, PreOrder, etc.

    # Fallback: internal "stockStatus" field (e.g. "normal", "outofstock")
    match = re.search(r'"stockStatus"\s*:\s*"([^"]+)"', html)
    if match:
        status = match.group(1).lower()
        if status == 'normal':
            return 'TRUE'
        if status in ('outofstock', 'oos'):
            return 'FALSE'
        return match.group(1)

    return 'N/A'
