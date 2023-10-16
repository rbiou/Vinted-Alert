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

def sendNotification():
    try:
	    #Read datas
        data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRIrg56uMRWI3zLci_4FHbA3chxVjnDtucBFhnMxV5sAWkQ4OPXlYkH6jZUTVl-GEUp61ZEowsWlZhc/pub?gid=0&single=true&output=csv", on_bad_lines="skip")
        log ("{size} searchs to alert.".format(size=data.size))
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
                size = item.get("size_title", "N/A")
                login = item.get("user", {}).get("login", "N/A")
                url = item.get("url", "N/A") # provide not found as default
                item = "{login} - {title} {price} €".format(login=login, title=title, price=price['amount'])
     	        # Get more details about the item
                reqDetails = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
                responseDetails = urlopen(reqDetails).read()
                soupDetails = BeautifulSoup(responseDetails.decode('utf-8'), 'lxml')
                itemId = soupDetails.find_all('meta', {"property": "og:product_id"})[0]["content"] # careful with this as it might change at any update
                reqDetailsAPI = Request(url="https://www.vinted.fr/api/v2/items/" + itemId + "?localize=false", headers={'User-Agent': 'Mozilla/5.0', 'cookie': '_vinted_fr_session=MDI4WTB1bG9WWER1eFU0RHZxRTFiTDFOTFptcitucHM5Qzk3Q3lYSVdjdTlCeVdDYkJFTURoRFMxdC9RZmNDWlJyd2NGRzltdGpydlRpOGJQNnUyQXU0Y2hGQjlGWjV4ZWxkckViLzJvclI1ei9sbzVhOG91RUh4UlJZRmExb09MdDZPTndHSS9pWExSVmpvY1Y0dW53RnR5d2JQU3JlcEZDWUIzY1F5L09LaU40am8vUFV2SnhITEtCZWlqU1JrMEtXVDFKYWQ5M2VoVFNLVFVTclB3K1MwUXh4di81djY5bnEwZGhmT0FVWGJCL1lOdi8vUHN3LzUvU0daNVBaWFNZTXZCVTFCa3lBYjJwTW9kUys4RWhjcTlwbHpaTVNJU0Z3S3FTYWNScGVZTXI0aFNkZktscW5pTHhVa3k2bzFBKytCQTkzOHQ1QWlVVXc0L3BlS0RsdkZES001ZUR0cTBmcCtGNVZsUmlEWC9HUGY4cUVjN254Q3lQSkY4aDF1c1lmb2ZSWW5XLzBGdm9pNUFwTGo2ZXZMU0FuYkI0cUI5eTNHQXphRFVvVnY1c29YalgzTFJ2WUZPb01sb3RkbjJxZmdXSjMzZlhCWlNYSmh0R1JENk5IQ25VM0x6NTd4eWpCLzZ3SitJdjMxRVJQc216OUo2NnEzODBpM3p5azlrejdzMEFibkMzUzlDSFVROGMvWmtqalZpMkVjQ0k2OFdvSERnempXNGhaRzRDT1NJSlppbU5obk96d2lPVEM2NzJYRm1Nb0pmN3U1ckxvS2orTVNHMjNEZFJoeHhnby84TzVwVHVxTk9ZUjVtbG1JRXRhRHlub1JHenA0dGxqMTNVWTJuRWJkRjh5VlU2eExQNitZVjZVN0xKYlA3K2x2WkVQbTFLdVlqY1hKQjRJTGV1V1Z4NlNzSDJRK2pEMHlCa0Q2SEZrTUtJWS9Bd2lvUGhncTF0RlR0Wk5kb04vdStsOUlyTzhkUm0rT3ZNclFwNC9ZRmF6TTZkMnFZcEgzWks0WHBOSWV6NUNaU1B6b3Q0NG5yOXVDcmlyUk9BWjdGaWJpa21OaEFOQWptM3U1K3A4QnFqNkFDY3U5VXppc0l2ZGNmVmdEMjZaeFQ4UE5PMGdxWnFkdWZXOTJrZmVDWTRuOWo4NWp5QzJZV2N1c0VSc1NpRS9YZkkyeW01dXdCSi9hcU4xZmtjQjhncElId1JxV21pUk9GYTNWK0xCK3BUOERuamQ1dUdPQXdlbzJjRUMxbGoxMWtCRG04V3paSDRzaCtQTDl1N3JVZmZkRzN6YnVUdnA1dE9rdjBTSEdBVFk4Skg2UzBpT3hPVkNKcExvOWx5REtmVVowYUw2azUzdUtZNXdxVzdhZ1RYa1kzWWUwU1htU1pleWZkdmxOeVF4Z3NyVVZib3FJVnF3em5udVQxOGhqejg1VlY5dTRJcGJ1Ykw1VVJMNzg5b0ZneXR0eFhQcVVua2JZY3hlSDVtM05EclJTYnI3WjBuVWp5bnhpTy9MQ3JBNFliUXhrZHZ0d1pDeXhETktjM2wzcCtDckk3MkdGcWlkWmp4RHFxMjJ0K3VDbFRKRGlVVkR3Qnc4RTdUSHh1OW9zamc1QmZ6d1dGdGlPVVM0MmpCbHY5ZWJsME9UR2NOV1FTVUJacU5oSVBJeXZTMy9DZWIraEJYTERKVWlxaHpyK25wUTVRalhOVCs2K0huUUxhSmczTmkwYnl6UW1hR1pVbW9aMGptaVFJU3NhMm5TN2x4ODRIOUFOV0JkMWlRY1RmY0hZaHNXSzl6d3lqVXpYeU1zVFF2b3M0RkdDK0lXWGxSV2RzcEp1SW0yekJxUW9vU2hCajJwK3l4VWcwK2hMNnlKOEhyUmNHeWMxQXdrZFVaU1R0ZFd3UFZLNm5qenJoRVhxeTMreVdaQkpUS2s2cjJJeGJNUHFEa2J6dDJ6K0Vnd1JtNHdlTStyQk5YUEtLTXV3dVRSc3Erd1FQVUxoRlZSeTVyamwzbm9BeENDRHRFRFNCN2xUTnBkeWVTT0NUN3dvM2RUdkk1RWZzRC9DZUNVMGpraS8rcm5OMkFqQWMxUC81R2o4Ym1tTEZodjZFUkpPNlA5Mk02TEtNZFdsN3JXSHMzVE5OOXJ3bllHb2RmdHovZlAvaENSdkZSZmxGVXFPL1dJTURvcXBsTWdEK0lRZlMwRXFUU1lMbHhBR0dacEwycWlzRXg5UFZxMnE4ZG15ckFaSjRJOFFVS3RMWktJMWJDVUVLVkxURFNqUXArOGVxblMyK2VNbXNYeDM4bkd2ejgyL052WWEybkVDMTYvWDAzdDRBNnBqdGZONzNMOHhDcktqemYxVXc2cWhPdGpNZU9Da0JzY2JIc0huRWRiWU1DcW44TTc1Vmdibi9jUVNRSmFYMmJ2TG9tYWIyaUtrK1djOG9CUjVEdmN6SXM0d0xvRzR1ZzQySnE2TlRNdmJmczZJYWUvaXVtL0RiRjcxSjh6eWZJeEJpQmRsMzZudTMxYjNwWUNCUExXcmhoeEVaWHhaRHpXSGsvdVZ2KzJmTEdxMHZxa3Z3ZGdnNTZmMDdlNnlUUHFLV1BUSE1qc0M2alN3ZzRybmg0YlFSc0xaV3hmVUMyNXc3djA2OW9Pci0tMUY1bGZtS2ZLOWVyYVcvT3F1ZDNHdz09--28d08a12fd9581a3a3339c1547aca0fcec615b88'})
                responseDetailsAPI = urlopen(reqDetailsAPI).read()
                soupDetailsAPI = BeautifulSoup(responseDetailsAPI,'html.parser')
                dataDetailsAPI = json.loads(soupDetailsAPI.text) # might check the type="application/json"
                dataDetails = dataDetailsAPI["item"]
                images = dataDetails.get("photos", "No Photo")
                feedback_reputation = dataDetails['user']['feedback_reputation']
                created_at = datetime.strptime(dataDetails['created_at_ts'], '%Y-%m-%dT%H:%M:%S%z')
                # Notify if new item from last ten min
                if ((datetime.now(timezone.utc) - timedelta(minutes=11)) < created_at):
                    log("New item : {item} => {url}".format(item=item, url=url), domain="Vinted")
                    content = NOTIFICATION_CONTENT.format(
                        price = price['amount'],
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

sendNotification()
