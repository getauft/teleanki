#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep

update_id = None

def main():
    global update_id
    bot = telegram.Bot('700887235:AAEMUZmPSfF4gCzNs9O_nyU8-jCkDY2GgDY')
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None
    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            update_id += 1

def echo(bot):
    global update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        if update.message:
            if (update.message.text):
                eng, rus = update.message.text.split('\n')
                update.message.reply_text({'eng': eng, 'rus': rus})

if __name__ == '__main__':
    main()