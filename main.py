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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def help(bot, update):
    msg = [
        '/start — init user in project',
        '/help — show this message',
        '/anki — get your ANKI decks',
        '/base — get data base project',
        '/delete — delete all your cards',
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
    try:
        User.select().where(User.idx == idx).get()
    except:
        User.create(
            idx = update.message['chat']['id'],
            name = update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'],
            login = update.message['chat']['username']
        )    
        logger.info('New user — {user}'.format(
            user= update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
        ))        
    help(bot, update)

def anki(bot, update):
    user = User.get(User.idx == update.message['chat']['id'])
    words = Words.select().where(Words.owner == user)
    phrases = Phrases.select().where(Phrases.owner == user)
    make_anki_deck(words, phrases)
    if os.path.exists('words.apkg'):
        with zipfile.ZipFile('words.apkg', 'a') as outzip:
            outzip.writestr('media', outzip.read('media').decode("utf-8").replace('cache/words/',''))
      
        bot.send_document(chat_id=update.message['chat']['id'], document=open('words.apkg', 'rb'))
        os.remove('words.apkg')                         
    if os.path.exists('phrases.apkg'):
        bot.send_document(chat_id=update.message['chat']['id'], document=open('phrases.apkg', 'rb'))
        os.remove('phrases.apkg')
    
def base(bot, update):
    logger.info('{user} requested data base file'.format(
        user= update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))
    if os.path.exists('teleanki.db'):
        update.message.reply_text('Actual data base file:')
        bot.send_document(chat_id=update.message['chat']['id'], document=open('teleanki.db', 'rb'))
    
def delete(bot, update):
    user = User.get(User.idx == update.message['chat']['id'])
    words = Words.select().where(Words.owner == user)
    phrases = Phrases.select().where(Phrases.owner == user)
    if(words):
        for word in words:
            word.delete_instance()
    if(phrases):
        for phrase in phrases:
            phrase.delete_instance() 
    logger.info('{user} remove all his cards'.format(
        user= update.message['chat']['first_name'] + ' ' + update.message['chat']['last_name'] + ' (' + str(update.message['chat']['id']) + ')'
    ))            
    update.message.reply_text('Your decks is clear.')

def wordz(bot, update):
    user = User.get(User.idx == update.message['chat']['id'])
    text = update.message.text
    items = text.split('\n')
    if(len(items) == 2):
        try:
            phrase = Phrases.create(
                owner=user,
                english=items[0],
                russian=items[1]
            )
        except:
            pass
    elif(len(items) == 1):
            items[0] = items[0].lower()
            translate = translate_word(items[0])
            word = Words.create(
                owner = user,
                english = items[0],
                transcription = translate['transcription'],
                word_forms = translate['word_forms']['description'],
                russian = translate['russian'],
                context_rus = translate['context']['rus'],
                context_eng = translate['context']['eng']
            )

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
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(MessageHandler(Filters.text, wordz))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    User.create_table()
    Phrases.create_table()
    Words.create_table()
    if not os.path.exists('cache'):
        os.makedirs('cache')
    if not os.path.exists('cache/words/'):
        os.makedirs('cache/words/')     
    main()