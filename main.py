#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from dbcontent import DBCONTENT

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
                update.message.reply_text(str(update.message))
                print(update.message)
                pass

if __name__ == '__main__':
    db = DBCONTENT('123')
    db.add('word', 'transcription', 'translate', 'sound', 'context_front', 'context_back')
    print(db.find('word'))
    print(db.get_all())
    db.update('word', 'word222', 'transcription333', 'translate444', 'sound555', 'context_front666', 'context_back777')
    db.delete('word222')
    main()