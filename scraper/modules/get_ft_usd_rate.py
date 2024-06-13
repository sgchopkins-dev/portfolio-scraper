import logging
import time
import requests
from bs4 import BeautifulSoup
from rfc5424logging import Rfc5424SysLogHandler
import os
NAS = os.getenv('NAS')

logger = logging.getLogger("usd_exch_rate")
logger.setLevel(logging.INFO)

handler = Rfc5424SysLogHandler(address=(NAS, 514))
logger.addHandler(handler)


def get_ft_usd_rate(verify=False):
    """
    returns a float object for USD-GBP rate
    :param verify: bool
    :return: float
    """
    url = "https://markets.ft.com/data/currencies/tearsheet/summary?s=usdgbp"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            value_raw = soup.find("span", {"class": "mod-ui-data-list__value"})
            value_net = value_raw.text
            logger.info(f"usd rate obtained at try number: {attempt + 1}")
            return float(value_net[0:-1])
        except:
            if attempt == 4:
                logger.critical("usd exchange rate scraping timed out")
                return 0.0
            time.sleep(5)
            continue