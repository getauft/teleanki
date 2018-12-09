from peewee import *
import datetime
import uuid

db = SqliteDatabase('teleanki.db')

class User(Model):
    idx = CharField()
    name = CharField()
    login = CharField()

    class Meta:
        database = db

class Words(Model):
    owner = ForeignKeyField(User, backref='users')
    date = DateField(default=datetime.datetime.now)
    english = CharField(unique=False)
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
    english = TextField(unique=False)
    russian = TextField()

    class Meta:
        database = db
