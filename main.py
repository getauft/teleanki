#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
from peewee import *
from models import *
from gendeck import make_anki_deck
import zipfile
from wooordhunt import translate_word
import datetime
import zipfile
from dbox import *
import threading
import time
import hashlib

logging.basicConfig(format='<p>%(asctime)s — %(levelname)s: %(message)s</p>',
                    level=logging.INFO,
                    filename='log.html',
                    filemode='w')
logger = logging.getLogger(__name__)


def help(bot, update):
    msg = [
        '/start — init user in project',
        '/help — show this message',
        '/anki — get ANKI decks',
        '/base — get data base',
        '/logs — get logs file',
        '/list — get list words and phrases',
        '/clean — delete all your cards',
        '\n\n',
        'message format from word:\n«word»',
        '\n',
        'message format from phrase:\n«phrase»\n«translate»'
    ]
    update.message.reply_text('\n'.join(msg))


def start(bot, update):
    idx = update.message['chat']['id']
    name = update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name']
    login = update.message['chat']['username']

    User.get_or_create(
        idx=update.message['chat']['id'],
        name=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'],
        login=update.message['chat']['username']
    )
    logger.info('{user} — init user'.format(
        user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))
    help(bot, update)


def anki(bot, update):
    user = User.get(User.idx == update.message['chat']['id'])
    words = Words.select().where(Words.owner == user)
    phrases = Phrases.select().where(Phrases.owner == user)
    make_anki_deck(words, phrases)
    if os.path.exists('words.apkg'):

        words_apkg = zipfile.ZipFile('words.apkg', 'r')
        files = words_apkg.filelist
        for file in files:
            print(file.filename)
        words_apkg.extractall()
        if os.path.exists('media'):
            media = open('media', 'r').read()
            media = media.replace('cache/words/', '')
            open('media', 'w').write(media)
        with zipfile.ZipFile('words.apkg', 'w') as myzip:
            for file in files:
                myzip.write(file.filename)
        bot.send_document(chat_id=update.message['chat']['id'], document=open('words.apkg', 'rb'))
        os.remove('words.apkg')
        logger.info('{user} — requested words.apkg file'.format(
            user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
        ))
    if os.path.exists('phrases.apkg'):
        bot.send_document(chat_id=update.message['chat']['id'], document=open('phrases.apkg', 'rb'))
        os.remove('phrases.apkg')
        logger.info('{user} — requested phrases.apkg file'.format(
            user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
        ))
    if(len(words) == 0 and len(phrases) == 0):
        update.message.reply_text('Your decks is clear.')


def base(bot, update):
    logger.info('{user} — requested data base file'.format(
        user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))
    if os.path.exists('teleanki.db'):
        bot.send_document(chat_id=update.message['chat']['id'], document=open('teleanki.db', 'rb'))


def logs(bot, update):
    logger.info('{user} — requested logs file'.format(
        user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))
    if os.path.exists('log.html'):
        bot.send_document(chat_id=update.message['chat']['id'], document=open('log.html', 'rb'))

def ilist(bot, update):
    logger.info('{user} — requested list words and phrases'.format(
        user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))
    user = User.get(User.idx == update.message['chat']['id'])
    words = Words.select().where(Words.owner == user)
    phrases = Phrases.select().where(Phrases.owner == user)
    html = '<html><head><meta charset="UTF-8"></head><body>'
    if os.path.exists('list.html'):
        os.remove('list.html')
    if(len(words) > 0):
        html = html + '<h2>Words ({count})</h2>'.format(count = len(words))
        for idw, word in enumerate(words):
            html = html + '<div>{idw} (ID #{base_id}). <b>{english}</b> — {russian}</div>'.format(
                english = word.english, 
                russian = word.russian,
                idw = idw,
                base_id = word.id
            )
    if(len(phrases) > 0):
        html = html + '<h2>Phrases ({count})</h2>'.format(count = len(phrases))
        for phrase in phrases:
            html = html + '<div>{idw} (ID #{base_id}). <b>{english}</b> — {russian}</div>'.format(
                english = phrase.english, 
                russian = phrase.russian,
                idw = idw,
                base_id = word.id
            )
    html = html + '</body></html>'
    open('list.html','w').write(html)
    if os.path.exists('list.html'):
        bot.send_document(chat_id=update.message['chat']['id'], document=open('list.html', 'rb'))
    else:
        update.message.reply_text('Your decks is clear.')

def clean(bot, update):
    user = User.get(User.idx == update.message['chat']['id'])
    words = Words.select().where(Words.owner == user)
    phrases = Phrases.select().where(Phrases.owner == user)
    if(words):
        for word in words:
            word.delete_instance()
    if(phrases):
        for phrase in phrases:
            phrase.delete_instance()
    update.message.reply_text('All your cards remove.')
    logger.info('{user} — remove all his cards'.format(
        user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))


def wordz(bot, update):
    user = User.get(User.idx == update.message['chat']['id'])
    text = update.message.text
    items = text.split('\n')
    if(len(items) == 2):
        try:
            phrase = Phrases.get_or_create(
                owner=user,
                english=items[0],
                russian=items[1]
            )
            logger.info('{user} — add phrase «{l1} — {l2}»'.format(
                user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')',
                l1=items[0],
                l2=items[1]
            ))
        except:
            pass
    elif(len(items) == 1):
            items[0] = items[0].lower().strip()
            if(user.idx == '165430615'):
                lang = 'fr'
            else:
                lang = 'en'
            translate = translate_word(items[0], lang)
            word = Words.get_or_create(
                owner=user,
                english=items[0],
                transcription=translate['transcription'],
                word_forms=translate['word_forms']['description'],
                russian=translate['russian'],
                context_rus=translate['context']['rus'],
                context_eng=translate['context']['eng']
            )
            update.message.reply_text(items[0] + ' — ' + translate['russian'])
            logger.info('{user} — add word «{word}»'.format(
                user=update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')',
                word=items[0].lower()
            ))
    pass


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater('700887235:AAEMUZmPSfF4gCzNs9O_nyU8-jCkDY2GgDY')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("anki", anki))
    dp.add_handler(CommandHandler("base", base))
    dp.add_handler(CommandHandler("logs", logs))
    dp.add_handler(CommandHandler("list", ilist))
    dp.add_handler(CommandHandler("clean", clean))
    dp.add_handler(MessageHandler(Filters.text, wordz))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

def sync_sound():
    dbox_files = []
    for file in files_list():
        dbox_files.append(file.name)
    local_files = os.listdir('cache/words')
    local_send = list(set(dbox_files) - set(local_files))
    for file in local_send:
        download('cache/words/' + file, '/sounds/' + file)
        pass
    dbox_get = list(set(local_files) - set(dbox_files))
    for file in dbox_get:
        upload('cache/words/' + file, '/sounds/' + file)
        pass    
    pass

def sync_database():
    def md5sum():
        hash_md5 = hashlib.md5()
        with open('teleanki.db', "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    while True:
        md5 = md5sum()
        time.sleep(60)
        if(md5 != md5sum()):
            upload('teleanki.db', '/teleanki.db')
            sync_sound()


if __name__ == '__main__':
    logger.info('Start app')
    download('teleanki.db', '/teleanki.db')
    User.create_table()
    Phrases.create_table()
    Words.create_table()
    if not os.path.exists('cache'):
        os.makedirs('cache')
    if not os.path.exists('cache/words/'):
        os.makedirs('cache/words/')
        
    target_main = threading.Thread(target=main)
    target_main.start()  
    target_sync_database = threading.Thread(target=sync_database)
    target_sync_database.start()
