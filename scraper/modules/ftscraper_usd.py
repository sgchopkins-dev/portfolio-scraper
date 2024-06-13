import re
import time

import requests
from bs4 import BeautifulSoup

from .get_ft_usd_rate import get_ft_usd_rate


def get_ft_current_price_usd(url, verify=False):
    """
    returns a price as a float object when passed a correct FT url converted to GBP pence
    :param url: string
    :param verify: bool
    :return: float
    """
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            value_raw = soup.find("span", {"class": "mod-ui-data-list__value"})
            value_net = value_raw.text
            value_net = value_net.replace(",", "")
            value_net = value_net.replace("$", "")
            label_raw = soup.find("span", {"class": "mod-ui-data-list__label"})
            result = re.findall("\d+\.\d+", value_net)[0]
            if label_raw.text == "Price (USD)":
                return (float(result) * 100) * get_ft_usd_rate()
            else:
                return 0.0
        except:
            if attempt == 4:
                return 0.0
            time.sleep(5)
            continue
