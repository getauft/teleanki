from bs4 import BeautifulSoup
import urllib
import urllib.request
import re
import os, sys
import string
import json
from pymystem3 import Mystem


def translate_word(word):
    soup = BeautifulSoup(urllib.request.urlopen('https://wooordhunt.ru/word/' + word).read(), 'html.parser')
    context = []
    if(soup.find('h3', text='Примеры')):
        if(soup.find('h3', text='Примеры').next_sibling.next_sibling):
            context_block = soup.find('h3', text='Примеры').next_sibling.next_sibling
            context_item_english = context_block.findAll(class_='ex_o')
            context_item_russian = context_block.findAll(class_='ex_t human')
            if(
                len(context_block.findAll(class_='ex_o')) > 0 and
                len(context_block.findAll(class_='ex_t human')) > 0 and
                len(context_block.findAll(class_='ex_o')) == len(context_block.findAll(class_='ex_t human'))
            ):
                for idx in range(0, len(context_item_english) - 1):
                    context.append(
                        {
                            'eng': context_item_english[idx].text.strip(),
                            'rus': context_item_russian[idx].text.replace('☰', '', 1).strip()
                        }
                    )
    if(soup.find(id='us_tr_sound')):
                if(soup.find(id='us_tr_sound').find(class_='transcription')):
                    transcription = soup.find(id='us_tr_sound').find(class_='transcription').text.replace('|', '', 2).strip()

    if(soup.find(class_='t_inline_en')):
        if(word is not None):
            yandex_url = "https://translate.yandex.net/api/v1.5/tr.json/translate?lang=en-ru&format=plain&key=trnsl.1.1.20181026T095610Z.0f9e5b3c50d78498.83dff75a74e7d95e0712640c87b207295ef8842a&text=" + word.replace(' ', '%20')
            yandex_url_to = "https://translate.yandex.net/api/v1.5/tr.json/translate?lang=en-ru&format=plain&key=trnsl.1.1.20181026T095610Z.0f9e5b3c50d78498.83dff75a74e7d95e0712640c87b207295ef8842a&text=" + 'to%20' + word.replace(' ', '%20')
            yandex_translate = urllib.request.urlopen(yandex_url).read()
            yandex_translate_to = urllib.request.urlopen(yandex_url_to).read()
            yd = json.loads(yandex_translate.decode("utf-8"))['text'][0].replace('чтобы', '', 1).strip().replace('себе', '', 1).strip()
            yd_to = json.loads(yandex_translate_to.decode("utf-8"))['text'][0]
            russian = soup.find(class_='t_inline_en').text.replace('\u2002', ' ').replace('  ', ' ').strip()
            mystem = Mystem()
            lemmas = mystem.lemmatize(yd)
            ws = russian.split(',')
            b = False
            for idx in range(1, 3):
                for w in ws:
                    if((not w.find(yd[:-idx]) == -1 or not w.find(lemmas[0][:-idx]) == -1) and b == False):
                        russian = russian.replace(w, w.upper(), 1)
                        b = True
        else:
            russian = soup.find(class_='t_inline_en').text.replace('\u2002', ' ').replace('  ', ' ').strip()
    elif(soup.find(class_='light_tr')):
        russian = soup.find(class_='light_tr').text.replace('\u2002', ' ').replace('  ', ' ').strip()

    word_forms = {'description': '', 'links': []}
    if(soup.find(id='word_forms')):
        word_forms['description'] = soup.find(id='word_forms').text.replace('\u2002', ' ').replace('  ', ' ').strip(),
        for link in soup.find(id='word_forms').findAll('a', href=True):
            if(link['href'] not in word_forms['links']):
                word_forms['links'].append(link['href'])

    return {'transcription' : transcription, 'context' : context[0], 'russian' : russian, 'word_forms' : word_forms}
