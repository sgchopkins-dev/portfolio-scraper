import re
import time

import requests
from bs4 import BeautifulSoup


def get_ft_current_price(url, verify=False):
    """
    returns a price as a float object when passed a correct FT url in GBP pence
    :param url: string
    :param verify: bool
    :return: float
    """
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            value_raw = soup.find("span", {"class": "mod-ui-data-list__value"})
            value_net = value_raw.text
            value_net = value_net.replace(",", "")
            value_net = value_net.replace("£", "")
            label_raw = soup.find("span", {"class": "mod-ui-data-list__label"})
            result = re.findall(r"\d+\.\d+", value_net)[0]
            if label_raw.text == "Price (GBP)":
                return float(result) * 100
            elif label_raw.text == "Price (GBX)":
                return float(result)
            else:
                return 0.0
        except:
            if attempt == 4:
                return 0.0
            time.sleep(5)
            continue
