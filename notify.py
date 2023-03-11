"""
Notify.py

Holds the notification logic, using the Telegram API
"""

from telegram import *
from telegram.ext import *
from telegram.error import RetryAfter, TimedOut
from utils import log
from config import TELEGRAM_KEY, CHAT_ID

import time

log("Connecting to the Telegram API", "Telegram")
bot = Bot(TELEGRAM_KEY)

def send_notification(content, images):
    '''Sends a telegram notification'''
    # log(content, "Telegram")
    # print(images)
    # print(notification)      
    log("Notifying user about a new product", "Telegram")
    try:
        bot.send_message(CHAT_ID, content)
        # Send the 3 firsts images
        for image in images[:3]:
            bot.send_photo(CHAT_ID, image["url"])
    except RetryAfter:
        print("ALERT FLOOD : wait 30s")
        time.sleep(30)
        send_notification(content, images)
    except TimedOut:
        print("TIME OUT : try again")
        send_notification(content, images)