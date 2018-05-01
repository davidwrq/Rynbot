#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from utils import get_secret

SECRET_KEY = get_secret('TOKEN')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def next_ufc_fight(bot, update):
    ufc_info = {}
    page = requests.get("http://www.ufcespanol.com/")
    soup = BeautifulSoup(page.content, 'html.parser')
    info = soup.find(id="fightcardtab0")
    info_tittle = info.find_all('a', href=True)
    ufc_info['tittle'] = "{} - {} - {} ".format(
        info_tittle[0].text, info_tittle[1].text.strip(), info_tittle[2].text)
    ufc_info['main_event'] = "{}".format(
        info.find_all(class_="main-event")[0].text.replace('\n', " ").strip())
    cards = {}
    div_card = info.find(
        class_="card-fights card-layout-2 LayoutA").find_all("div", "card")
    for card_fight in div_card:
        card_title = card_fight.find(class_="fight-card-title").text.strip()
        fights = card_fight.find_all(class_="fight")
        fights_list = []
        for fight in fights:
            fights_list.append('{} - vs - {}'.format(
                fight.find(class_="fighter-name1").text, fight.find(
                    class_="fighter-name2").text))
        cards[card_title] = fights_list
    ufc_info['fights'] = cards

    update.message.reply_text(ufc_info)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(SECRET_KEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("next_ufc_fight", next_ufc_fight))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
