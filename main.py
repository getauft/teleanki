import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from peewee import *
from wooordhunt import translate_word

db = SqliteDatabase('teleanki.db')

class User(Model):
    idx = CharField()
    name = CharField()
    login = CharField()

    class Meta:
        database = db

class Words(Model):
    owner = ForeignKeyField(User, backref='users')
    english = CharField(unique=True)
    transcription = CharField(null=True)
    word_forms = TextField(null=True)
    russian = TextField(null=True)
    context_rus = TextField(null=True)
    context_eng = TextField(null=True)

    class Meta:
        database = db

class Phrases(Model):
    owner = ForeignKeyField(User, backref='users')
    english = TextField(unique=True)
    russian = TextField()

    class Meta:
        database = db


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
            
def set_user_info(message):
    User.create_table()
    idx = message['chat']['id']
    name = message['chat']['first_name'] + ' ' + message['chat']['last_name']
    login = message['chat']['username']
    try:
        User.select().where(User.idx == idx).get()
    except:
        User.create(
            idx=message['chat']['id'],
            name=message['chat']['first_name'] + ' ' + message['chat']['last_name'],
            login=message['chat']['username']
        )
    pass


def save(message):
    user = User.get(User.idx == message['chat']['id'])
    text = message.text
    items = text.split('\n')
    msg = None
    if(len(items) == 2):
        Phrases.create_table()
        try:
            phrase = Phrases.create(
                owner=user,
                english=items[0],
                russian=items[1]
            )
            msg = 'Фраза сохранена:\n\n{eng}\n{rus}\n'.format(eng=items[0], rus=items[1])
        except:
            pass
    elif(len(items) == 1):
        Words.create_table()
        try:
            translate = translate_word(items[0])
            print(translate)
            word = Words.create(
                owner = user,
                english = items[0],
                transcription = translate['transcription'],
                word_forms = translate['word_forms']['description'],
                russian = translate['russian'],
                context_rus = translate['context']['rus'],
                context_eng = translate['context']['eng']
            )
            msg = 'Слово <b>{english}</b> сохранено\n\n<b>Транскрипция:</b> {transcription}\n<b>Формы слова:<b> {word_forms}\n<b>Перевод:</b> {russian}\n<b>Контекст:</b>\n<i>{context_eng}</i>\n<i>{context_rus}</i>'.format(
                english=word.english.upper(), 
                transcription=word.transcription,
                word_forms=word.word_forms,
                russian=word.russian,
                context_eng=word.context_eng,
                context_rus=word.context_rus)
            print(msg)
        except:
            pass
    return msg

def echo(bot):
    global update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        if update.message:

            if (update.message.text):
                if(update.message.text == 'get_base_file'):
                    bot.send_document(chat_id=update.message['chat']['id'], document=open('teleanki.db', 'rb'))
                else:
                    set_user_info(update.message)
                    msg = save(update.message)
                    bot.send_message(
                        chat_id=update.message['chat']['id'], 
                        text=msg, 
                        parse_mode=telegram.ParseMode.HTML
                    )
                pass
            elif(update.message.document):
                if(update.message.document.file_name == 'teleanki.db'):
                    file_id = update.message.document.file_id
                    newFile = bot.get_file(file_id)
                    newFile.download('teleanki.db')


if __name__ == '__main__':
    main()
