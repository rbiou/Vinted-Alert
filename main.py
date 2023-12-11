"""
Main.py

The main script

Goal : Creating a Vinted bot that will send a notification as soon as a new article is available.
We can pass some arguments like the price, the size, the type of article, etc...
"""
import json
from time import sleep
from traceback import print_exc
from random import randint, random

from requests import get
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from pandas import pandas as pd

import config
from utils import log
from notify import send_notification
from constants import NOTIFICATION_CONTENT

from datetime import datetime, timezone, timedelta

from api import search

def sendNotification():
    try:
	    #Read datas
        data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRIrg56uMRWI3zLci_4FHbA3chxVjnDtucBFhnMxV5sAWkQ4OPXlYkH6jZUTVl-GEUp61ZEowsWlZhc/pub?gid=0&single=true&output=csv", on_bad_lines="skip")
        log ("{size} searchs to alert.".format(size=data.size))
        #For each alert requested, check event and deals
        for index, row in data.iterrows():
            log("New search to alert : {url}".format(url=row["url"]), domain="Vinted")
            data = searchViaApi(row["url"])
            for item in data:
                created_at = datetime.fromtimestamp(item['photo']['high_resolution']['timestamp'], timezone.utc)
                # Notify if new item from last ten min
                if ((datetime.now(timezone.utc) - timedelta(minutes=11)) < created_at):
                    # Collect data
                    title = item.get("title", "N/A")
                    price = item.get("price", "ERR") # Format 4,00 €
                    brand = item.get("brand_title", "N/A")
                    size = item.get("size_title", "N/A")
                    login = item.get("user", {}).get("login", "N/A")
                    url = item.get("url", "N/A") # provide not found as default
                    images = [item["photo"]["full_size_url"]]
                    feedback_reputation = None
                    item = "{login} - {title} {price} €".format(login=login, title=title, price=price)
                    log("New item : {item} => {url}".format(item=item, url=url), domain="Vinted")
                    content = NOTIFICATION_CONTENT.format(
                        price = price,
                        title = title,
                        brand = brand,
                        size = size,
       	                feedback_reputation = "{:.0%}".format(feedback_reputation) if (feedback_reputation and feedback_reputation > 0) else "Non noté ATM",
                        url = url
                    )
                    # Send notification
                    send_notification(content, images)
                else:
                    log("No new articles to alert")
                    break
    except Exception:
        print_exc()

def searchViaApi(url):
    return search(url, {})
sendNotification()
