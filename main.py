"""
Main.py

The main script

Goal : Creating a Vinted bot that will send a notification as soon as a new article is available.
We can pass some arguments like the price, the size, the type of article, etc...
"""
from datetime import datetime, timezone, timedelta
from traceback import print_exc

from pandas import pandas as pd

from constants import NOTIFICATION_CONTENT
from notify import send_notification
from utils import log

from urllib import parse

from vinted_scraper import VintedScraper


def search_and_notify():
    try:
        # Read datas
        data = pd.read_csv(
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vRIrg56uMRWI3zLci_4FHbA3chxVjnDtucBFhnMxV5sAWkQ4OPXlYkH6jZUTVl-GEUp61ZEowsWlZhc/pub?gid=0&single=true&output=csv",
            on_bad_lines="skip")
        log("{size} searchs to alert.".format(size=data.size))
        scraper = VintedScraper("https://www.vinted.fr")
        # For each alert requested, check event and deals
        for index, row in data.iterrows():
            log("New search to alert : {url}".format(url=row["url"]), domain="Vinted")
            data = search(scraper, row["url"])
            for item in data:
                item = scraper.item(item.id)
                created_at = datetime.fromtimestamp(
                    datetime.strptime(item.created_at_ts, '%Y-%m-%dT%H:%M:%S%z').timestamp(),
                    timezone.utc)
                # Notify if new item from last ten min
                if (datetime.now(timezone.utc) - timedelta(minutes=110)) <= created_at:
                    # Collect data
                    title = item.title
                    price = item.price  # Format 4,00 €
                    brand = item.brand
                    size = item.size_title
                    login = item.user_id
                    url = item.url
                    images = [photo.url for photo in item.photos]
                    feedback_reputation = item.user.feedback_reputation
                    item = "{login} - {title} {price} €".format(login=login, title=title, price=price)
                    log("New item : {item} => {url}".format(item=item, url=url), domain="Vinted")
                    content = NOTIFICATION_CONTENT.format(
                        price=price,
                        title=title,
                        brand=brand,
                        size=size,
                        feedback_reputation="{:.0%}".format(feedback_reputation) if (
                                    feedback_reputation and feedback_reputation > 0) else "Non noté ATM",
                        url=url
                    )
                    # Send notification
                    send_notification(content, images)
                else:
                    log("No new articles to alert")
                    break
    except Exception:
        print_exc()


def search(scraper, url):
    # Parse the query string
    query_string = parse.urlparse(url).query

    # Convert the query string to a dictionary
    query_params = parse.parse_qs(query_string)

    # init the scraper with the baseurl
    params = {k: v[0] for k, v in query_params.items()}
    items = scraper.search(params)
    return items


search_and_notify()
