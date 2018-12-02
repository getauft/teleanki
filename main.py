import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from peewee import *
from wooordhunt import translate_word
import datetime


db = SqliteDatabase('teleanki.db')


class User(Model):
    idx = CharField()
    name = CharField()
    login = CharField()

    class Meta:
        database = db


class Reports(Model):
    user = ForeignKeyField(User, backref='users')
    date = DateField(default=datetime.datetime.now)

    class Meta:
        database = db


class Words(Model):
    owner = ForeignKeyField(User, backref='users')
    date = DateField(default=datetime.datetime.now)
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
    date = DateField(default=datetime.datetime.now)
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
        try:
            translate = translate_word(items[0])
            word = Words.create(
                owner=user,
                english=items[0],
                transcription=translate['transcription'],
                word_forms=translate['word_forms']['description'],
                russian=translate['russian'],
                context_rus=translate['context']['rus'],
                context_eng=translate['context']['eng']
            )
            msg = 'Слово {english} сохранено:\n\nТранскрипция: {transcription}\nФормы слова: {word_forms}\nПеревод: {russian}\nКонтекст:\n{context_eng}\n{context_rus}'.format(
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
    if(datetime.datetime.now().hour == 21):
        dnow = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        for user in User.select():
            report = Reports.select().where((Reports.date == dnow) | (Reports.user == user))
            if(len(report) == 0):
                words = Words.select().where((Words.date == dnow) | (Words.owner == user))
                phrases = Phrases.select().where((Phrases.date == dnow) | (Phrases.owner == user))
                wa = []
                pa = []
                if(words):
                    for word in words:
                        wa.append(word.english)
                if(phrases):
                    for phrase in phrases:
                        pa.append(phrase.english)
                if(len(words) > 0 or len(phrases) > 0):
                    msg = 'День подошел к концу. Вы добавили:\nслова ({len_words}): {word_list}\nфразы ({len_phrases}):\n{phrase_list}'.format(
                        len_words=str(len(words)),
                        len_phrases=str(len(phrases)),
                        word_list=', '.join(wa),
                        phrase_list='\n'.join(pa)
                    )
                else:
                    msg = 'Что-то случилось сегодня? Вы про меня совсем забыли?'
                bot.send_message(chat_id=user.idx, text=msg)
                Reports.create(
                    user=user
                )

    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        if update.message:
            if (update.message.text):
                if(update.message.text == 'get_base_file'):
                    bot.send_document(chat_id=update.message['chat']['id'], document=open('teleanki.db', 'rb'))
                elif(update.message.text == '/start'):
                    set_user_info(update.message)
                    update.message.reply_text('Привет, {name}!\nЯ - бот который будет ждать от тебя новые для тебя слова. В конце дня я специально для тебя сделаю отчет по добавленным словам и пришлю колоду которую ты сможешь добавить в ANKI. Пришли мне /help и я расскажу тебе как правильно добавлять слова и фразы.'.format(name=update.message['chat']['first_name']))
                elif(update.message.text == '/help'):
                    update.message.reply_text('TeleAnki бот на связи! Я умею сохранять два типа данных: слова и фразы. Чтобы сохранить слово, просто пришли его мне. К примеру, чтобы сохранить слово «bear», просто пришли его мне, а я его переведу и сохраню. Фразы сохранять чуть сложнее, но для тебя это не составит труда... Сообщение должно состоять из двух строк:\n1-я строка — фраза на иностранном языке,\n2-я — перевод фразы.\nПример:\n\nI can\'t bear him.\nЯ его не выношу.\n\nВот так все просто!')
                elif(update.message.text == '/report'):
                    dnow = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
                    user = User.get(User.idx == update.message['chat']['id'])
                    report = Reports.select().where((Reports.date == dnow) | (Reports.user == user))
                    words = Words.select().where((Words.date == dnow) | (Words.owner == user))
                    phrases = Phrases.select().where((Phrases.date == dnow) | (Phrases.owner == user))
                    wa = []
                    pa = []
                    if(words):
                        for word in words:
                            wa.append(word.english)
                    if(phrases):
                        for phrase in phrases:
                            pa.append(phrase.english)
                    if(len(words) > 0 or len(phrases) > 0):
                        msg = 'День подошел к концу. Вы добавили:\nслова ({len_words}): {word_list}\nфразы ({len_phrases}):\n{phrase_list}'.format(
                            len_words=str(len(words)),
                            len_phrases=str(len(phrases)),
                            word_list=', '.join(wa),
                            phrase_list='\n'.join(pa)
                        )
                    else:
                        msg = 'Что-то случилось сегодня? Вы про меня совсем забыли?'
                    bot.send_message(chat_id=user.idx, text=msg)
                else:
                    msg = save(update.message)
                    update.message.reply_text(msg)
                pass
            elif(update.message.document):
                if(update.message.document.file_name == 'teleanki.db'):
                    file_id = update.message.document.file_id
                    newFile = bot.get_file(file_id)
                    newFile.download('teleanki.db')


if __name__ == '__main__':
    User.create_table()
    Phrases.create_table()
    Words.create_table()
    Reports.create_table()
    main()
