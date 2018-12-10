import genanki
import sys
from random import randint
import random
from shutil import move
import os


def make_anki_deck(words, phrases):
    parts = [{'items': words, 'name': 'words'}, {'items': phrases, 'name': 'phrases'}]
    model_id = 1540747305545
    model_name = 'Basic (and reversed card)'
    fields = [{'name': 'Front'}, {'name': 'Back'}]
    templates = [{
        'name': 'Card',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id=answer>{{Back}}'
    }]
    css = '.main{text-align:center} .english{text-transform:uppercase}'
    model = genanki.Model(model_id, model_name, fields, templates, css)
    local_media_list = []
    for part in parts:
        if(len(part['items']) > 0):
            deck_ = []
            deck = genanki.Deck(randint(1000000000, 9999999999), part['name'])
            for item in part['items']:
                if(part['name'] == 'words'):
                    ###
                    if os.path.exists('cache/words/' + item.english.lower().replace(' ', '_') + '.mp3'):
                        local_media_list.append('cache/words/' + item.english.lower().replace(' ', '_') + '.mp3')
                    ###
                    front = '<div class="main"><h1 class="english">{english}</h1><p>[sound:{sound}.mp3]</p><p class="transcription">{transcription}</p><p class="forms">{forms}</p><p class="context eng">{context_eng}</p></div>'.format(
                        english=item.english.lower(),
                        sound=item.english.lower().replace(' ', '_'),
                        transcription=item.transcription,
                        forms=item.word_forms,
                        context_eng=item.context_eng
                    )
                    back = '<div class="main"><p class="russian">{russian}</p><p class="context rus">{context_rus}</p></div>'.format(
                        russian=item.russian,
                        context_rus=item.context_rus
                    )
                else:
                    local_media_list = []
                    front = '<div class="main"><p class="context eng">{english}</p></div>'.format(english=item.english)
                    back = '<div class="main"><p class="context eng">{russian}</p></div>'.format(russian=item.russian)
                for fields in [[front, back], [back, front]]:
                    note = genanki.Note(model=model, fields=fields)
                    deck_.append(note)
            random.shuffle(deck_)
            for w in deck_:
                deck.add_note(w)
            package = genanki.Package(deck)
            package.media_files = local_media_list
            package.write_to_file(part['name'] + '.apkg')
    return
