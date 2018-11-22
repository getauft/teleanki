import requests
import datetime
from time import sleep

url = "https://api.telegram.org/bot700887235:AAEMUZmPSfF4gCzNs9O_nyU8-jCkDY2GgDY/"


def get_updates_json(request):  
    response = requests.get(request + 'getUpdates')
    return response.json()


def last_update(data):  
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]

def get_chat_id(update):  
    chat_id = update['message']['chat']['id']
    return chat_id

def send_mess(chat, text):  
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response

 
update_id = last_update(get_updates_json(url))['update_id']
while True:
    if update_id == last_update(get_updates_json(url))['update_id']:
        print('This is update ID ' + str(update_id))
        send_mess(get_chat_id(last_update(get_updates_json(url))), 'This is update ID ' + str(update_id))
        update_id += 1
    sleep(1)       
