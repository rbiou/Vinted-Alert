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

from datetime import datetime, timezone

def sendNotification():
    try:
	    #Read datas
        data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRIrg56uMRWI3zLci_4FHbA3chxVjnDtucBFhnMxV5sAWkQ4OPXlYkH6jZUTVl-GEUp61ZEowsWlZhc/pub?gid=0&single=true&output=csv", on_bad_lines="skip")
        log ("{size} searchs to alert.".format(size=data.size))
        log(data)
        #For each alert requested, check event and deals
        for index, row in data.iterrows():
            log("New search to alert : {url}".format(url=row["url"]), domain="Vinted")
            req = Request(url=row["url"], headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req).read()
            soup = BeautifulSoup(response.decode('utf-8'), 'lxml') # lxml is faster but a dependency, "html.parser" is quite fast and installed by default
            script = soup.find_all('script', {"data-js-react-on-rails-store": "MainStore"})[0] # careful with this as it might change at any update
            data = json.loads(script.string) # might check the type="application/json"
            data = data['items']['catalogItems']['byId'].values()
            # log(data, "Vinted") # --> debug
            
            for item in data:
                # Collect data
                title = item.get("title", "N/A")
                price = item.get("price", "ERR") # Format 4,00 €
                brand = item.get("brand_title", "N/A")
                login = item.get("user", {}).get("login", "N/A")
                url = item.get("url", "N/A") # provide not found as default
                item = "{login} - {title} {price} €".format(login=login, title=title, price=price)
     	        # Get more details about the item
                reqDetails = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
                responseDetails = urlopen(reqDetails).read()
                soupDetails = BeautifulSoup(responseDetails.decode('utf-8'), 'lxml')
                scriptDetails = soupDetails.find_all('script', {"data-component-name": "ItemDetails"})[0] # careful with this as it might change at any update
                dataDetails = json.loads(scriptDetails.string) # might check the type="application/json"
                dataDetails = dataDetails["item"]
                images = dataDetails.get("photos", "No Photo")
                feedback_reputation = dataDetails['user']['feedback_reputation']
                created_at = datetime.strptime(dataDetails['created_at_ts'], '%Y-%m-%dT%H:%M:%S%z')
                # Notify if new item from last ten min
                if ((datetime.now(timezone.utc) - created_at).seconds / 60 < 11):
                    log("New item : {item} => {url}".format(item=item, url=url), domain="Vinted")
                    content = NOTIFICATION_CONTENT.format(
                        price = price,
                        title = title,
                        brand = brand,
       	                feedback_reputation = "{:.0%}".format(feedback_reputation) if (feedback_reputation and feedback_reputation > 0) else "Non noté ATM",
                        url = url
                    )
                    # Send notification
                    send_notification(content, images)
    except Exception:
        print_exc()

sendNotification()