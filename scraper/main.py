import os
import logging
import time

import pandas as pd
from database.db import list_distinct_funds, list_funds
from modules.email import email_portfolio
from modules.ftscraper import get_ft_current_price
from modules.ftscraper_usd import get_ft_current_price_usd
from pretty_html_table import build_table
from rfc5424logging import Rfc5424SysLogHandler

NAS = os.getenv('NAS')


logger = logging.getLogger("scraping")
logger.setLevel(logging.INFO)

handler = Rfc5424SysLogHandler(address=(NAS, 514))
logger.addHandler(handler)


logger.info(
    f"Obtained {len(list_distinct_funds())} unique funds from MongoDB... starting to scrape"
)
start = time.time()
data = list_funds()

df = pd.DataFrame(list(data))
# del df["_id"]


def get_prices(row):
    return get_ft_current_price(row["url"])


df["price"] = 0.0
for name in df["name"].unique():
    url = df.loc[df["name"] == name]["url"].unique()[0]
    currency = df.loc[df["name"] == name]["currency"].unique()[0]
    if "Pension" in name:
        df.loc[df["name"] == name, "price"] = 100.0
    elif "Premium Bonds" in name:
        df.loc[df["name"] == name, "price"] = 100.0
    elif currency == "GBP":
        df.loc[df["name"] == name, "price"] = get_ft_current_price(url)
        time.sleep(1)
    elif currency == "USD":
        df.loc[df["name"] == name, "price"] = get_ft_current_price_usd(url)
        time.sleep(1)
    else:
        pass


def get_value(row):
    return round(((row["units"] * row["price"]) / 100), 2)


df["value"] = df.apply(lambda row: get_value(row), axis=1)
end = time.time()
elasped = end - start
t = divmod(elasped, 60)
mins = int(t[0])
secs = int(t[1])

logger.info(f"Scraping finished in {mins} mins and {secs} secs")

# Alison Summary
alison_summary = (
    df[df["portfolio"].str.contains("Alison", case=False)]
    .groupby(by=["portfolio"])
    .agg({"value": "sum"})
    .sort_values(by=["value"], ascending=[False])
    .reset_index()
)
alison_summary.loc["Totals"] = alison_summary["value"].sum()
alison_summary["value"] = alison_summary["value"].round(decimals=2)
alison_summary.loc["Totals", "portfolio"] = ""
alison_summary['value'] = alison_summary['value'].map("£ {:,.2f}".format)

# Alison detail
alison_detail = (
    df[df["portfolio"].str.contains("Alison", case=False)]
    .groupby(by=["portfolio", "name"])
    .agg({"units": "sum", "value": "sum"})
    .rename(columns={"units": "units"})
    .sort_values(by=["portfolio", "value"], ascending=[True, False])
    .reset_index()
)

alison_summary_html = build_table(
    alison_summary,
    "orange_light",
    text_align="right",
    font_family="Sans-Serif",
    font_size="14px",
    width="300px",
)
alison_detail_html = build_table(
    alison_detail,
    "blue_light",
    text_align="right",
    font_family="Sans-Serif",
    font_size="12px",
    width="300px",
)

email_portfolio(
    ["simon@muddypaws.net", "alison@muddypaws.net"],
    alison_summary_html,
    alison_detail_html,
)

# Simon Summary
simon_summary = (
    df[df["portfolio"].str.contains("Simon", case=False)]
    .groupby(by=["portfolio"])
    .agg({"value": "sum"})
    .sort_values(by=["value"], ascending=[False])
    .reset_index()
)
simon_summary.loc["Totals"] = simon_summary["value"].sum()
simon_summary["value"] = simon_summary["value"].round(decimals=2)
simon_summary.loc[:, "value"] = "£" + simon_summary["value"].map("£ {:,.2f}".format)
simon_summary.loc["Totals", "portfolio"] = ""

# Simon detail
simon_detail = (
    df[df["portfolio"].str.contains("Simon", case=False)]
    .groupby(by=["portfolio", "name"])
    .agg({"units": "sum", "value": "sum"})
    .rename(columns={"units": "units"})
    .sort_values(by=["portfolio", "value"], ascending=[True, False])
    .reset_index()
)

simon_summary_html = build_table(
    simon_summary,
    "orange_light",
    text_align="right",
    font_family="Sans-Serif",
    font_size="14px",
    width="300px",
)
simon_detail_html = build_table(
    simon_detail,
    "blue_light",
    text_align="right",
    font_family="Sans-Serif",
    font_size="12px",
    width="300px",
)

email_portfolio(
    ["simon@muddypaws.net", "alison@muddypaws.net"],
    simon_summary_html,
    simon_detail_html,
)

# Global Summary
df_summary = (
    df.groupby(by=["portfolio"])
    .agg({"value": "sum"})
    .sort_values(by=["value"], ascending=[False])
    .reset_index()
)
df_summary.loc["Totals"] = df_summary["value"].sum()
df_summary["value"] = df_summary["value"].round(decimals=2)
df_summary.loc[:, "value"] = "£" + df_summary["value"].map("£ {:,.2f}".format)
df_summary.loc["Totals", "portfolio"] = ""

# Global detail
global_detail = (
    df.groupby(by=["portfolio", "name"])
    .agg({"units": "sum", "value": "sum"})
    .rename(columns={"units": "units"})
    .sort_values(by=["portfolio", "value"], ascending=[True, False])
    .reset_index()
)

global_summary_html = build_table(
    df_summary,
    "orange_light",
    text_align="right",
    font_family="Sans-Serif",
    font_size="14px",
    width="300px",
)
global_detail_html = build_table(
    global_detail,
    "blue_light",
    text_align="right",
    font_family="Sans-Serif",
    font_size="12px",
    width="300px",
)

email_portfolio(
    ["simon@muddypaws.net", "alison@muddypaws.net"],
    global_summary_html,
    global_detail_html,
)
df.to_csv("/mnt/nfs_client/fund-daily-output/fund_data_export.csv", index=False)
logger.critical(
    "scraper ran and stored output data in /mnt/nfs_client/fund-daily-output/fund_data_export.csv"
)


