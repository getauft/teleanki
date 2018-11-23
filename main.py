#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from bs4 import BeautifulSoup
import urllib
import urllib.request
import re
import pickle
import os, sys
import string
import genanki
from random import randint
import json
from pymystem3 import Mystem

update_id = None

class WORKER(object):
    def get_source_word_list(self, file_name):
        if os.path.exists(file_name): 
            raw = open(file_name, 'r')
            text = raw.readlines()
        else:
            print('ERROR! FILE NOT FOUND.')
            sys.exit()
        word_list = []
        for line in text:
            _word = line.replace('\n', '', 1).strip()
            if(len(_word)>0 and _word not in word_list):
                word_list.append(_word.strip().lower())
        word_list.sort()
        return word_list
    def translate_word(self, word, user_id):        
        if os.path.exists('cache/' + user_id +'/words/' + word + '.pkl'):
            return self.load(word, user_id)
        
        soup = BeautifulSoup(urllib.request.urlopen('https://wooordhunt.ru/word/' + word).read(), 'html.parser')
        word_translated = None
        
        def _check_exist(soup):
            if(soup.find(id='word_not_found') is None):
                return True
            else:
                return False
        
        def _get_context(soup):
            context = []
            if(soup.find('h3',text='Примеры')):
                if(soup.find('h3',text='Примеры').next_sibling.next_sibling):
                    context_block = soup.find('h3',text='Примеры').next_sibling.next_sibling
                    context_item_english = context_block.findAll(class_='ex_o')
                    context_item_russian = context_block.findAll(class_='ex_t human')   
                    if(
                        len(context_block.findAll(class_='ex_o'))>0 and 
                        len(context_block.findAll(class_='ex_t human'))>0 and
                        len(context_block.findAll(class_='ex_o')) == len(context_block.findAll(class_='ex_t human'))
                    ):
                        for idx in range(0, len(context_item_english)-1):
                            context.append(
                                {
                                    'eng':context_item_english[idx].text.strip(),
                                    'rus':context_item_russian[idx].text.replace('☰','',1).strip()
                                }
                            )
            return (context, [{'eng': '','rus': ''}])[len(context) == 0]
        
        def _get_english(soup, word = None):
            english = None
            if(word is not None and soup.title.text.lower().strip() == word.lower().strip()):
                english = soup.title.text.lower().strip()
            elif(re.match(r'(\S*):.*', soup.title.text)):
                english = re.match(r'(\S*):.*', soup.title.text).group(1).lower().strip()
            elif(soup.find('h1').text.replace(' - перевод на русский','',1).strip()):
                english = soup.find('h1').text.replace(' - перевод на русский','',1).lower().strip()
            return english
        def _get_transcription(soup):
            transcription = ''
            if(soup.find(id='us_tr_sound')):
                if(soup.find(id='us_tr_sound').find(class_='transcription')):
                    transcription = soup.find(id='us_tr_sound').find(class_='transcription').text.replace('|','',2).strip()
            return transcription
        
        def _get_russian(soup, word = None):
            russian = None
            if(soup.find(class_='t_inline_en')):
                if(word is not None):
                    russian = soup.find(class_='t_inline_en').text.replace('\u2002',' ').replace('  ',' ').strip()
                else:
                    russian = soup.find(class_='t_inline_en').text.replace('\u2002',' ').replace('  ',' ').strip()
            elif(soup.find(class_='light_tr')):
                russian = soup.find(class_='light_tr').text.replace('\u2002',' ').replace('  ',' ').strip()
            return russian
        
        def _get_word_forms(soup):
            word_forms = {'description':'','links': []}
            if(soup.find(id='word_forms')):
                word_forms['description'] = soup.find(id='word_forms').text.replace('\u2002',' ').replace('  ',' ').strip(),
                for link in soup.find(id='word_forms').findAll('a', href=True):
                    if(link['href'] not in word_forms['links']):
                        word_forms['links'].append(link['href'])
            return word_forms
        def _get_sound(soup, word):
            sound = {
                'us': '',
                'uk': ''
            }
            def __download(pref, word): 
                mp3 = b''
                if(len(word.split())==1):
                    response = urllib.request.urlopen('https://wooordhunt.ru/data/sound/word/' + pref + '/mp3/' + word + '.mp3')
                    if(response.headers['Content-Type'] == 'audio/mpeg'):
                        mp3 = response.read() 
                else:
                    for item in word.split():
                        response = urllib.request.urlopen('https://wooordhunt.ru/data/sound/word/' + pref + '/mp3/' + item + '.mp3')
                        if(response.headers['Content-Type'] == 'audio/mpeg'):
                            mp3 += response.read() 
                return mp3
            sound['us'] = __download('us', word)
            sound['uk'] = __download('uk', word)  
            return sound    
        
        
        if(_check_exist(soup) and _get_russian(soup) is not None):
            word_translated = {
                'english': _get_english(soup, word),
                'transcription':  _get_transcription(soup),
                'word_forms': _get_word_forms(soup),
                'context': _get_context(soup),
                'russian': _get_russian(soup, word),
                'audio': _get_sound(soup, word),
            }
        self.save(word_translated, user_id)
        return word_translated    
    
    def save(self, translate_word_object,user_id):
        with open('cache/' + user_id + '/words/' + translate_word_object['english'].lower() + '.pkl', 'wb') as output:
            pickle.dump(translate_word_object, output, pickle.HIGHEST_PROTOCOL) 
    
    def load(self, word, user_id):
        with open('cache/' + user_id + '/words/' + word + '.pkl', 'rb') as input:
            return pickle.load(input)   
    
    def extract_audio(self, translate_word_object, us = True, uk = False):
        extracted_us = False
        extracted_uk = False
        if(us and translate_word_object['audio']['us']):
            open(translate_word_object['english'].lower().replace(' ','_') + '_us.mp3','wb').write(translate_word_object['audio']['us'])
            extracted_us = True
        if(uk and translate_word_object['audio']['uk']):
            open(translate_word_object['english'].lower().replace(' ','_') + '_uk.mp3','wb').write(translate_word_object['audio']['uk'])
            extracted_uk = True
        return {'us':extracted_us,'uk':extracted_uk}
    def make_anki_deck(self, translated_words, need_reverse_card, input_deck_name, user_id):
        model_id = 1607392319
        model_name = 'ankinstain_english'
        fields = [
            {'name': 'english'},
            {'name': 'russian'},
            {'name': 'transcription'},
            {'name': 'audio'},
            {'name': 'image'},
            {'name': 'context_rus'},
            {'name': 'context_eng'},
            {'name': 'word_forms'}
        ]
        templates = [
            {
                'name': 'ertai2cw',
                'qfmt': '<table id="main_table"><thead><tr id="english"><th>&nbsp;{{english}}&nbsp;</th></tr></thead><tbody><tr id="transcription"><td>&nbsp;{{transcription}}&nbsp;</td></tr><tr id="word_forms"><td>&nbsp;{{word_forms}}&nbsp;</td></tr><tr id="russian" class="hidden"><td>&nbsp;{{russian}}&nbsp;</td></tr><tr id="context_eng"><td>&nbsp;{{context_eng}}&nbsp;</td></tr><tr id="context_rus" class="hidden"><td>&nbsp;{{context_rus}}&nbsp;</td></tr><tr height=200px id="image" class="hidden"><td>{{image}}</td></tr></tbody><tfoot><tr id="audio"><td>&nbsp;{{audio}}&nbsp;</td></tr></tfoot></table>',
    
                'afmt': '<table id="main_table"><thead><tr id="english"><th>&nbsp;{{english}}&nbsp;</th></tr></thead><tbody><tr id="transcription"><td>&nbsp;{{transcription}}&nbsp;</td></tr><tr id="word_forms"><td>&nbsp;{{word_forms}}&nbsp;</td></tr><tr id="russian"><td>&nbsp;{{russian}}&nbsp;</td></tr><tr id="context_eng"><td>&nbsp;{{context_eng}}&nbsp;</td></tr><tr id="context_rus"><td>&nbsp;{{context_rus}}&nbsp;</td></tr><tr id="image" height=200px><td>{{image}}</td></tr></tbody><tfoot><tr id="audio"><td>&nbsp;{{audio}}&nbsp;</td></tr></tfoot></table>',
            }
        ]
        css = 'b{color:#E86F6F; font-size:110%}#main_table{width:100%;height:100%;min-height:100%;position:absolute;bottom:0;top:0;left:0;right:0;text-align:center}#image img{width:auto;max-width:100%;border-radius:5%}#english{font-size:150%;font-weight:700;text-transform:uppercase;color:#1b98f8}#transcription{color:#999;font-size:120%}#word_forms{color:#1b98f9;opacity:.7}#russian{color:#5aba59}#context_eng,#context_rus{font-style:italic}#context_rus{color:#5aba59}.hidden{visibility:hidden}'
        model = genanki.Model(model_id, model_name, fields, templates, css)
        deck = genanki.Deck(randint(1000000000, 9999999999), input_deck_name + ' (eng)')
        local_media_list = []    
        print('Заполнение колоды #1')
        for translated_word in translated_words:
            extracted = self.extract_audio(translated_word)
            if(extracted['us']):
                local_media_list.append(translated_word['english'].replace(' ','_') + '_us.mp3')
            if(extracted['uk']):
                local_media_list.append(translated_word['english'].replace(' ','_') + '_uk.mp3')                          
            fields = [
                str(translated_word['english']),
                str(translated_word['russian']),
                str(translated_word['transcription']),
                str('[sound:' + translated_word['english'].replace(' ','_') + '_us.mp3' + ']'),
                str(''),
                str(translated_word['context'][0]['rus']),
                str(translated_word['context'][0]['eng']),
                str(translated_word['word_forms']['description'])
            ]
            note = genanki.Note(
                model=model,
                fields=fields
            )
            deck.add_note(note)   
        package = genanki.Package(deck)
        package.media_files = local_media_list
        package.write_to_file('cache/' + user_id +'/decks/' + input_deck_name + ' (eng).apkg')
        
        model_id_reverse = 1607392320
        model_name_reverse = 'ankinstain_russian'
        fields_reverse = [
            {'name': 'english_reverse'},
            {'name': 'russian_reverse'},
            {'name': 'transcription_reverse'},
            {'name': 'audio_reverse'},
            {'name': 'image_reverse'},
            {'name': 'word_forms_reverse'}
        ]
        templates_reverse = [
            {
                'name': 'ertai2cwr',
                'qfmt': '<table id="main_table"><thead><tr id="english" class="hidden"><th>&nbsp;{{english_reverse}}&nbsp;</th></tr></thead><tbody><tr id="transcription" class="hidden"><td>&nbsp;{{transcription_reverse}}&nbsp;</td></tr><tr id="word_forms" class="hidden"><td>&nbsp;{{word_forms_reverse}}&nbsp;</td></tr><tr id="russian"><td>&nbsp;{{russian_reverse}}&nbsp;</td></tr><tr id="image"><td>{{image_reverse}}</td></tr></tbody><tfoot><tr id="audio"><td>&nbsp;</td></tr></tfoot></table>',

                'afmt': '<table id="main_table"><thead><tr id="english"><th>&nbsp;{{english_reverse}}&nbsp;</th></tr></thead><tbody><tr id="transcription"><td>&nbsp;{{transcription_reverse}}&nbsp;</td></tr><tr id="word_forms"><td>&nbsp;{{word_forms_reverse}}&nbsp;</td></tr><tr id="russian"><td>&nbsp;{{russian_reverse}}&nbsp;</td></tr><tr id="image" height=200px><td>{{image_reverse}}</td></tr></tbody><tfoot><tr id="audio"><td>&nbsp;{{audio_reverse}}&nbsp;</td></tr></tfoot></table>',
            }
        ]
        css_reverse = 'b{color:#E86F6F; font-size:110%}#main_table{width:100%;height:100%;min-height:100%;position:absolute;bottom:0;top:0;left:0;right:0;text-align:center}#image img{width:auto;max-width:100%;border-radius:5%}#english{font-size:150%;font-weight:700;text-transform:uppercase;color:#1b98f8}#transcription{color:#999;font-size:120%}#word_forms{color:#1b98f9;opacity:.7}#russian{color:#5aba59}#context_eng,#context_rus{font-style:italic}#context_rus{color:#5aba59}.hidden{visibility:hidden}'
        model_reverse = genanki.Model(model_id_reverse, model_name_reverse, fields_reverse, templates_reverse, css_reverse)
        deck_reverse = genanki.Deck(randint(1000000000, 9999999999), input_deck_name + ' (rus)')         
        print('Заполнение колоды #2')
        for translated_word in translated_words:
            fields_reverse = [
                str(translated_word['english']),
                str(translated_word['russian']),
                str(translated_word['transcription']),
                str('[sound:' + translated_word['english'].replace(' ','_') + '_us.mp3' + ']'),
                str(''),
                str(translated_word['word_forms']['description'])
            ]
            note_reverse = genanki.Note(
                model=model_reverse,
                fields=fields_reverse
            )
            deck_reverse.add_note(note_reverse)        
        package_reverse = genanki.Package(deck_reverse)
        package_reverse.media_files = local_media_list
        package_reverse.write_to_file('cache/' + user_id +'/decks/' + input_deck_name + ' (rus).apkg')        
        print('Удаление временных файлов')
        for file in local_media_list:
            if os.path.exists(file):
                os.remove(file)   
        return ['cache/' + user_id +'/decks/' + input_deck_name + ' (rus).apkg','cache/' + user_id +'/decks/' + input_deck_name + ' (eng).apkg']

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
            
def create_user_dir(user_id):
    if not os.path.exists('cache'):
        os.makedirs('cache')
    if not os.path.exists('cache/' + user_id + '/'):
        os.makedirs('cache/' + user_id + '/') 
    if not os.path.exists('cache/' + user_id + '/words/'):
        os.makedirs('cache/' + user_id + '/words/')   
    if not os.path.exists('cache/' + user_id + '/decks/'):
        os.makedirs('cache/' + user_id + '/decks/')

def make_deck(message):
    deck_name = message.text.replace('/make','').strip()
    user_id = message.chat.id
    if not os.path.exists('cache/'+ str(user_id) + '/' + str(deck_name)):
        open('cache/'+ str(user_id) + '/' + str(deck_name), 'w')
        return 'Создана колода «' + deck_name + '»'
    else:
        return 'Колода «' + deck_name + '» уже существует'

def set_deck(message):
    message_lines = message.text.split('\n')
    deck_file = 'cache/' + str(message.chat.id) + '/' + message_lines[0].replace('/set','').replace('\n','').strip() 
    word_list = []
    if os.path.exists(deck_file):
        df = open(deck_file, 'r')
        raw = df.readlines()
        for line in raw:
            _word = line.replace('\n', '', 1).strip()
            if(len(_word)>0 and _word not in word_list):
                word_list.append(_word.strip().lower())
        df.close() 
    else:
        deck_name = message_lines[0].replace('/set','').replace('\n','').strip()
        user_id = message.chat.id
        df = open(deck_file, 'w')
        df.close()
    for idx, line in enumerate(message.text.split('\n')):
            if(not idx == 0):        
                if(len(line)>0 and line not in word_list):
                    word_list.append(line.strip().lower())                
                    print(idx, line)
    word_list.sort() 
    df = open(deck_file,'w')
    df.write('\n'.join(word_list))
    df.close()
    return 'Колода «' + message_lines[0].replace('/set','').replace('\n','').strip() + '» пополнена, теперь в ней содержатся следующие слова: ' + ', '.join(word_list)
    
def get_deck(message):
    worker = WORKER()
    deck_file = 'cache/' + str(message.chat.id) + '/' + message.text.replace('/get','').replace('\n','').strip()
    source_word_list = worker.get_source_word_list(deck_file)
    translated_word_list = []
    print('Перевод',len(source_word_list), 'слов:',', '.join(source_word_list))
    for _word in source_word_list:
        tw = worker.translate_word(_word, str(message.chat.id))
        translated_word_list.append(tw)
    return worker.make_anki_deck(translated_word_list, False, message.text.replace('/get','').replace('\n','').strip(), str(message.chat.id))

def list_deck(message):
    user_dir = 'cache/' + str(message.chat.id) + '/'
    items = os.listdir(user_dir)
    items.remove('words')
    items.remove('decks')   
    if(len(items) > 0):
        return 'Список ваших колод:\n' + '\n'.join(items)
    else:
        return 'У вас не создано ни одной колоды'
    
def delete_deck(message):
    deck_name = message.text.replace('/delete','').strip()
    user_id = message.chat.id
    if os.path.exists('cache/'+ str(user_id) + '/' + str(deck_name)):  
        os.remove('cache/'+ str(user_id) + '/' + str(deck_name))
        return 'Колода «' + deck_name + '» удалена'
    else:
        return 'Колоды «' + deck_name + '» не существует'
    
def echo(bot):
    global update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        if update.message:      
            print(update.message.text)
            create_user_dir(str(update.message.chat.id))
            if(not update.message.text.find('/make') == -1):
                update.message.reply_text(make_deck(update.message))
            if(not update.message.text.find('/delete') == -1):
                update.message.reply_text(delete_deck(update.message))                
            if(not update.message.text.find('/set') == -1):
                update.message.reply_text(set_deck(update.message))
            if(not update.message.text.find('/list') == -1):
                update.message.reply_text(list_deck(update.message))
            if(not update.message.text.find('/get') == -1):
                update.message.reply_text('Идет процесс создания колоды... ожидайте...')
                deck_files = get_deck(update.message)
                for deck_file in deck_files:
                    bot.send_document(chat_id=update.message.chat.id, document=open(deck_file, 'rb'))
                    if os.path.exists(deck_file):  
                        os.remove(deck_file)                    
            if(not update.message.text.find('/help') == -1):
                update.message.reply_text(
                    'Список доступных комманд:\n' +
                    '/make <название колоды> — создание новой колоды.\n' +
                    '/set <название колоды>\n<word>\n...\n<word> — наполнение колоды словами\n' +
                    '/list — получение списка существующих колод\n' +
                    '/get <название колоды> — получение колоды в формате apkg'
                )

if __name__ == '__main__':
    main()
