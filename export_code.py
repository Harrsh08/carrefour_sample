import html
import json
import re

import mysql.connector as my_connector
import pandas as pd
from decouple import config
from xlsxwriter.utility import xl_range

OUTPUT_FILE = "carrefour_sample.xlsx"

# Columns you want in the Excel file, in this order
EXPORT_COLS = [
    "Sr No",   # serial number 1..N, replaces the DB id
    "product_id",
    "product_name",
    "product_url",
    "listing_category",
    "brand",
    "ranking",
    "price",
    "unit_price",
    "mrp",
    "discount_percentage",
    "availability",
    "sellers",
    "currency_type",
    "description",
    "highlights",
    "information",
    "specification",
    "images",
    "pack_size",
    "variants",
    "type",
    "ratings",
    "review_count",
    "review_data",
    "frequantly_bought_products",
    "offers",
    "delivery_data"
]
# Needed by the rules even if not exported (sellers fallback, product_id repair)
HELPER_COLS = ["pl_seller_data", "product_url"]

# Columns forced to text in Excel (only used if present in the export)
TEXT_COLS = ["product_id", "category_id"]

# ---------------------------------------------------------------- 1. Read
conn = my_connector.connect(
    host=config("DB_HOST"),
    user=config("DB_USER"),
    password=config("DB_PASSWORD"),
    database="carrefour_sample",
)

select_cols = [c for c in dict.fromkeys(EXPORT_COLS + HELPER_COLS) if c != "Sr No"]
query = f"select {', '.join(select_cols)} from pdp order by id"   # same order as the DB

df = pd.read_sql(query, conn)
conn.close()
print(df)

# ---------------------------------------------------------------- 2. Helpers
NULL_VALUES = {"", "null", "none", "nan", "n/a", "{}", "[]"}


ZERO_RE = re.compile(r"0+(\.0+)?")   # 0, 00, 0.0, 0.00


def is_null(v):
    if v is None:
        return True
    s = str(v).strip().lower()
    if s[:1] in ("{", "["):
        s = re.sub(r"\s+", "", s)   # "{ }" / "[ ]" count as empty too
    if s in NULL_VALUES:
        return True
    return bool(ZERO_RE.fullmatch(s))   # any zero value -> N/A


CONTROL_RE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200f\u2028\u2029\ufeff\ufffd]"
)
LITERAL_ESC_RE = re.compile(r"\\[trn]")            # the 2-char text \t \r \n
PUNCT_RUN_RE = re.compile(r"\s*[.,](?:\s*[.,])+")  # ". , " / ", ," / ".,."


def unescape_html(s):
    """&#39; -> '   &eacute; -> é   &amp; -> &   (repeated, for double-encoded text like &amp;amp;)"""
    for _ in range(3):
        u = html.unescape(s)
        if u == s:
            break
        s = u
    return s


def _map_json_strings(obj, fn):
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, dict):
        return {k: _map_json_strings(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_map_json_strings(v, fn) for v in obj]
    return obj


def unescape_value(v):
    """Decode HTML entities. In JSON cells only the string values are decoded,
    so a decoded quote (&quot;) can never break the JSON."""
    s = v.lstrip()
    if s[:1] in ("{", "["):
        try:
            data = json.loads(s)
        except ValueError:
            return unescape_html(v)
        return json.dumps(_map_json_strings(data, unescape_html), ensure_ascii=False)
    return unescape_html(v)


def clean_text(v):
    if not isinstance(v, str):
        return v
    v = unescape_value(v)                # HTML entities -> real characters
    v = LITERAL_ESC_RE.sub(" ", v)       # literal \t \r \n
    v = CONTROL_RE.sub("", v)            # junk / invisible characters
    v = re.sub(r"[\t\r\n]+", " ", v)     # real tabs / newlines
    return re.sub(r"\s+", " ", v).strip()


def clean_description(v):
    v = clean_text(v)
    if not isinstance(v, str):
        return v
    v = re.sub(r"^[\s.,]+", "", v)       # leading stray punctuation
    # collapse punctuation runs: keep "." if any, else ","
    v = PUNCT_RUN_RE.sub(lambda m: ". " if "." in m.group() else ", ", v)
    v = re.sub(r"[\s,]+$", "", v)        # trailing stray commas
    return re.sub(r"\s+", " ", v).strip()


def replace_json_nulls(obj):
    """Recursively turn every JSON null (None) into "N/A"."""
    if obj is None:
        return "N/A"
    if isinstance(obj, dict):
        return {k: replace_json_nulls(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_json_nulls(v) for v in obj]
    return obj


def fix_json_nulls(v):
    if not isinstance(v, str):
        return v
    s = v.lstrip()
    if s[:1] not in ("{", "["):
        return v
    try:
        data = json.loads(s)
    except ValueError:
        return v                      # not valid JSON, leave as is
    return json.dumps(replace_json_nulls(data), ensure_ascii=False)


# ---------------------------------------------------------------- 3. sellers == [] -> pl_seller_data
SELLER_KEYS = ["type", "price", "rating", "offerId", "sellerId", "sellerName", "deliveryPromise"]
PL_KEY_MAP = {"seller_id": "sellerId", "seller_name": "sellerName"}
SELLER_DEFAULTS = {"type": "main", "offerId": "offer_carrefour_"}   # all other missing keys -> "N/A"


def pl_to_sellers(pl):
    """{"seller_id":..,"brand_name":..,"seller_name":..} -> [{type, price, ..., deliveryPromise}]
    Keys that pl_seller_data does not have are set to "N/A"."""
    if is_null(pl):
        return pl
    try:
        data = json.loads(pl) if isinstance(pl, str) else pl
    except ValueError:
        return pl                                   # not valid JSON, leave as is
    items = data if isinstance(data, list) else [data]

    out = []
    for d in items:
        if not isinstance(d, dict):
            continue
        seller = {k: SELLER_DEFAULTS.get(k, "N/A") for k in SELLER_KEYS}
        for k in SELLER_KEYS:                       # keys already in sellers format
            if d.get(k) not in (None, ""):
                seller[k] = d[k]
        for src, dst in PL_KEY_MAP.items():         # seller_id -> sellerId, ...
            if d.get(src) not in (None, ""):
                seller[dst] = d[src]
        out.append(seller)
    return json.dumps(out, ensure_ascii=False) if out else pl


def fix_sellers(row):
    s = str(row["sellers"]).strip()
    if s in ("[]", "") or is_null(s):
        return pl_to_sellers(row["pl_seller_data"])
    return row["sellers"]


df["sellers"] = df.apply(fix_sellers, axis=1)

# ---------------------------------------------------------------- 4. Clean junk in every column
df = df.apply(lambda col: col.map(clean_text))
for _col in ("description", "highlights"):
    if _col in df.columns:
        df[_col] = df[_col].map(clean_description)

# null inside JSON data -> "N/A"  (e.g. "deliveryPromise": null)
df = df.apply(lambda col: col.map(fix_json_nulls))

# ---------------------------------------------------------------- 5. Remaining nulls -> N/A
df = df.apply(lambda col: col.map(lambda v: "N/A" if is_null(v) else v))

# ---------------------------------------------------------------- 6. Restore product_id from URL if in scientific notation
df["product_id"] = df["product_id"].astype(str)
mask = df["product_id"].str.contains(r"E\+", case=False, na=False)
if mask.any():
    extracted = df.loc[mask, "product_url"].astype(str).str.extract(r"/p/(\d+)")[0]
    df.loc[mask, "product_id"] = extracted.fillna(df.loc[mask, "product_id"])

# ---------------------------------------------------------------- 7. Excel cell limit (32,767 chars)
df = df.apply(lambda col: col.map(lambda v: v[:32767] if isinstance(v, str) else v))

# ---------------------------------------------------------------- 8. Keep only the wanted columns
df.insert(0, "Sr No", range(1, len(df) + 1))
df = df[EXPORT_COLS]

# ---------------------------------------------------------------- 9. Export
with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="xlsxwriter",
    engine_kwargs={"options": {"strings_to_urls": False}},   # keep URLs as plain text
) as writer:
    df.to_excel(writer, sheet_name="Products", index=False)

    wb = writer.book
    ws = writer.sheets["Products"]

    text_fmt = wb.add_format({"num_format": "@"})
    header_fmt = wb.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1})

    for col_idx, name in enumerate(df.columns):
        ws.write(0, col_idx, name, header_fmt)

    for name in TEXT_COLS:
        if name in df.columns:
            i = df.columns.get_loc(name)
            ws.set_column(i, i, 18, text_fmt)
            for r, val in enumerate(df[name], start=1):
                ws.write_string(r, i, str(val), text_fmt)

    ws.ignore_errors(
        {"number_stored_as_text": xl_range(0, 0, len(df), len(df.columns) - 1)}
    )

    ws.freeze_panes(1, 0)
    # ws.autofilter(0, 0, len(df), len(df.columns) - 1)

print(f"Exported {len(df)} rows to {OUTPUT_FILE}")