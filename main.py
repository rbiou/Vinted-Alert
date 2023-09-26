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
                reqDetailsAPI = Request(url="https://www.vinted.fr/api/v2/items/" + itemId + "?localize=false", headers={'User-Agent': 'Mozilla/5.0', 'cookie': '_vinted_fr_session=aWpyWTFDeDFFSUF6R1Rua29CSlFGLyt5KzJkWDBneU84RVJ4SzYrc3pJSSt1eE9nV0xIc25jMlJaMzJ0N3g3Z2tKV1pWSmczejJNNWlsaVZWWTc0UURSZG0zdk1vb21ISTNyajlHNkJORnEwWURaQzRLaUwyM2NVKzRBenhCRlp2dlY5OGRBYjdzaWVtekpMMzVOT3ZoZ0VSUTlFdUF4QzlGV3FTbVZydmxJY3oyQ21yVm1YWWJLMitFRndWbFZDaVY2Sk5ERmxwWnhyRjFlQkRMcjVUdVBUMDBzU0hHZVlRUkRVeFB0aWZLREZvdDB5VzJPbENYY1BYRGtMR1g0L0lWSnR4NlNWb0JGMkd0Q29wbW8ybkxLQWFsV2JqZUlzdk9UZHRneUZLN09IOWFHOWRzcHgxOVVUL0RveE1iK3VtbnE4WEhuVzJsYzBXM2NJUDIwRVVUQVdaaEdMUTRBR05JR3FwWUlxUU54T1RNd2ltQjNiYWNMSURMeHJVS3lMdm1SOVNsWEhpakpPaWw3bzE3aS9DUHR1cW0xU1JydTNDa3RUS1M5aWxqUUJpVkt6YUx2OSt6RXpFUWkyTWNublRWRCtwdG9sTmo4TUw3ZjhDQUhNM0ZhTVkwek5yb3hxd2dXYUwxTmQrTzlVeWN4VnR2S0J1bGNrUENTZ09seERrWWtNTkxKRDdNeEM5RVFhVVZ3QVhSNWFiT0RBN0JYNXJzUmFVaFIzeDhta1ViaVNDY1pkUVkyMVA2M2hsMkl4dDJXUjNrRVVDMWo4cjN5em1nL0YyeW5NM3J1VjZObGNmdVpqN1dXUlVBNGh2a0VPYkRETkhRWEJQeUtsc1hsQk1IUXVCd25vY21vVys3ZVdtYWpTRG5OR204bGFpRWJ5U3UvME1wTFU0cGhuYk05N0NrL2JyRm9UZStkcDlpZk5VT3MyM3NhT0lDNEhwUHM3eGwweEFCV3pkS00wdjV2QWszR1M2VlhFWDZaSmlWOWhkWFVzVG00c2Z2NjlwRndiWk8xQlIrc1VvOHZ0MllpNis0ZVQ2RDVtZ3lQaTFJbzZjSFRmQTdoL1psQTdreFdHUHJ4UzB6L2lLSnY0OWQ5aUFpRXZuakhKcFdRU2JhOUdDaEVUUVd4Vkc5L3hzVlVyYUpBaFZjcllSaTlyRVdESjJJM2VQUHpKempEV3VZUFNKZysxNzNKS0ptSUxZZm1WVzVtQmJ2ZlR0UU5BeVBuU252YlpNVFRPTW9tQXR4R0ZTM1lOS1hWMXd1ZmZ0OVZMYWZCeFY4R1lHcEdvQ2RDYjdveDBmL2toN1AzZ0YzZkRyeFdzYVNBWXB0ZXNxUStveXE3QllKMXVqOCt2S3NkOTlmREx0dEdSWWN1L1FoOEd5L2F2T3FqdWhIY05ONlVScGlHRFAyV2Vja0U1QXBWUm5waGlRN1hWUEhpcktZNzBZYUdSMVB3ZlBSL2pNUXcreXE0UU9WRkYzeEp6bVZuMmloL2pKVC9MdFIzOFUrdDZoSXROYytlOXorRkREOGZjL1dQT3JKMSswMkZjaEJzL2ZrWFRtWkMwZTNjV05UWCtIbisvVXY2UHNXbDVUWC9mUkQydktYaTRwTWo3OFNsWDBBbkVDK2tqczFPdi9heUpCczFaaUthNm1DT3h5VVZxeERQZTd3T044UkxaVTYzWElNRUxTK1k1amNYb2lramJoY2lIQ1BNTW9oYlhsVFppc2NpM29ocVBhcUN0THM4dCtRR1NPSmpqZlVJZjc1MzRWcXJwRFhUNS9GTDFacjlwZlA4eU5NdDdidDRoYnpoZUx5NTY1b1hkazVKczhWUWRTRExMMmMvbmVKYXlOVC9Ddm1KemppT3IrMUpCNWdScSsvK1VQb1ByZi9TdkYyS2dIdXNjeEcyRi9xaDZrbnBGVCtsZ05ORzJkMVV1U2cxWE1HdHhzZGt1Z1F0blcwVGhLK3dUTnVuSitiNlhaZ3NVdDN2SXVZL0lKc3EzbG5aQUpwKzRSKysrRnREbUQ0NTBOZDdBMi9uaFJMeXQ5NlUyc1g2eStzcEhVZzRiT04yeFpFYkhZaEo2NHc3dlAzdkdZMStYZ2U0L3BRS1hNQUtqVTlwSTRyVXBjTW9hRmVXOUltZGE1eUE5VzVwdE5lL3laSXpqNXlwa3VOc2M1R0xJdHArKzV1aXVHaVowcHBFNVVRR28waGJ2NXY2ZUZ5SEsxUzRFNEdtdThQUGdRQitDMzI2Q1dLYTJFdlV0QUZlYTlleEVzUkU2Vm1qUXA1N0pldy9BK0p0Wi9MejdSMXB5VU5WU05LQnhBOG5JY2VWdERDajNGc0xNTllLOVFpTnZXMEhNNXVxUnFmU1lhOTJUTFZPMEVSeGI4ZUQ3Sjg0Nnh6SURQZGdnTG5JdVVnUlBzbUY1Z0E9PS0tamVwQmNPbFUwU2NGbVRFY2JtcUJBQT09--9af1824fbd14900e14a0434fb4cf65895ae2edc3'})
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