import requests
import urllib
import urllib.request
import json


def translate_word(word, lang):
    transcription = ''
    context = [{
        'eng': '',
        'rus': ''
    }]
    russian = ''
    word_forms = {'description': '', 'links': []}
    response = requests.get('https://google-translate-proxy.herokuapp.com/api/translate?query={word}&targetLang=ru&sourceLang={lang}'.format(
        word=word.replace(' ', '%20'),
        lang=lang
    )).json()['extract']
    russian = response['translation'] + '; ' + '; '.join(response['synonyms'])
    result = {'transcription': transcription, 'context': context[0], 'russian': russian, 'word_forms': word_forms}
    if(lang == 'en'):
        words = word.split(' ')
        mp3 = b''
        for w in words:
            response = urllib.request.urlopen('https://wooordhunt.ru/data/sound/word/us/mp3/' + w.lower().strip() + '.mp3')
            if(response.headers['Content-Type'] == 'audio/mpeg'):
                mp3 = mp3 + response.read()
        open('cache/words/' + word.lower().strip().replace(' ', '_') + '.mp3', 'wb').write(mp3)
    return result
