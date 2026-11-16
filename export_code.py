import pandas as pd
import mysql.connector as my_connector
from decouple import config

conn = my_connector.connect(
  host = config("DB_HOST"),
  user = config("DB_USER"),
  password= config("DB_PASSWORD"),
  database = "carrefour_sample"

)


query = 'select * from pdp'



OUTPUT_FILE = "products_export.xlsx"

TEXT_COLS = ["id", "product_id", "category_id"]


df = pd.read_sql(query, conn)

print(df)

# 2. Null handling
NULL_VALUES = {"", "null", "none", "nan", "n/a"}

def is_null(v):
    return v is None or str(v).strip().lower() in NULL_VALUES

# 3. sellers == [] -> use pl_seller_data
def fix_sellers(row):
    s = str(row["sellers"]).strip()
    if s in ("[]", "") or is_null(s):
        return row["pl_seller_data"]
    return row["sellers"]

df["sellers"] = df.apply(fix_sellers, axis=1)

# 4. Remaining nulls -> N/A
df = df.apply(lambda col: col.map(lambda v: "N/A" if is_null(v) else v))

# 5. Restore product_id corrupted into scientific notation, using the URL
mask = df["product_id"].str.contains(r"E\+", case=False, na=False)
df.loc[mask, "product_id"] = df.loc[mask, "product_url"].str.extract(r"/p/(\d+)$")[0]

# 6. Excel cells max out at 32,767 characters, so trim any longer text
df = df.apply(lambda col: col.map(lambda v: v[:32767] if isinstance(v, str) else v))

# 7. Export with ExcelWriter
with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Products", index=False)

    wb = writer.book
    ws = writer.sheets["Products"]

    text_fmt   = wb.add_format({"num_format": "@"})                   # force text
    header_fmt = wb.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1})

    # Header styling
    for col_idx, name in enumerate(df.columns):
        ws.write(0, col_idx, name, header_fmt)

    # Text format + width for ID columns
    for name in TEXT_COLS:
        if name in df.columns:
            i = df.columns.get_loc(name)
            ws.set_column(i, i, 18, text_fmt)
            # rewrite as explicit strings so Excel never treats them as numbers
            for r, val in enumerate(df[name], start=1):
                ws.write_string(r, i, str(val), text_fmt)

    # Hide the green "number stored as text" warning triangles
    ws.ignore_errors({"number_stored_as_text": f"A1:{chr(64 + min(len(df.columns), 26))}{len(df) + 1}"})

    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(df), len(df.columns) - 1)

print(f"Exported {len(df)} rows to {OUTPUT_FILE}")