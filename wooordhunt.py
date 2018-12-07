import requests
import urllib
import json

def translate_word(word):
    transcription = ''
    context = [{
        'eng': '',
        'rus': ''
    }]
    russian = ''
    word_forms = {'description': '', 'links': []}
    response = requests.get('https://google-translate-proxy.herokuapp.com/api/translate?query={word}&targetLang=ru&sourceLang=en'.format(
        word = word.replace(' ', '%20')
    )).json()['extract']
    russian = response['translation'] + '; ' + '; '.join(response['synonyms'])
    result = {'transcription' : transcription, 'context' : context[0], 'russian' : russian, 'word_forms' : word_forms}
    response = urllib.request.urlopen('https://wooordhunt.ru/data/sound/word/us/mp3/' + word.replace(' ', '%20').lower() + '.mp3')
    if(response.headers['Content-Type'] == 'audio/mpeg'):
        mp3 = response.read()
        open('cache/words/'+word.lower() + '.mp3', 'wb').write(mp3)    
    return result
