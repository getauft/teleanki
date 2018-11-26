import requests
from bs4 import BeautifulSoup
import re


class ANKIWEB(object):

    def __init__(self):
        self.cookie = None
        self.scrf = None
        self.scrf2 = None
        self.username = 'getauft@gmail.com'
        self.password = '35227401'
        self.url = {
            'login': 'https://ankiweb.net/account/login',
            'edit': 'https://ankiuser.net/edit/',
            'save': 'https://ankiuser.net/edit/save'
        }
        self.headers_ankiweb_get = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'ankiweb=login',
            'DNT': '1',
            'Host': 'ankiweb.net',
            'Referer': 'https://ankiweb.net/',
            'TE': 'Trailers',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        }
        self.headers_ankiweb_post = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'ankiweb=login',
            'DNT': '1',
            'Host': 'ankiweb.net',
            'Referer': 'https://ankiweb.net/account/login',
            'TE': 'Trailers',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        }
        self.headers_ankiuser_get = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Cookie': 'ankiweb={cookie}',
            'DNT': '1',
            'Host': 'ankiuser.net',
            'Referer': 'https://ankiweb.net/',
            'TE': 'Trailers',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        }
        self.headers_ankiuser_post = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ankiweb={cookie}',
            'DNT': '1',
            'Host': 'ankiuser.net',
            'Referer': 'https://ankiuser.net/edit/',
            'TE': 'Trailers',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session = requests.Session()

    def send(self, front='', back='', tags=''):
        params = {
            'data': [[front, back], tags],
            'csrf_token': self.scrf2,
            'mid': 1540747305545,
            'deck': 'Phrases'
        }
        cookies = {
            'ankiweb': self.cookie
        }
        self.headers_ankiuser_post['Cookie'] = self.headers_ankiuser_post['Cookie'].format(cookie=self.cookie)
        send_post = self.session.post(url=self.url['save'], cookies=cookies, data=params, headers=self.headers_ankiuser_post)
        print(send_post.text)
        pass

    def get_scrf2(self):
        self.headers_ankiuser_get['Cookie'] = self.headers_ankiuser_get['Cookie'].format(cookie=self.cookie)
        edit_get = self.session.get(url=self.url['edit'], cookies={'ankiweb': self.cookie}, headers=self.headers_ankiuser_get)
        pattern = re.compile("editor.csrf_token2 = '.+';")
        result = pattern.search(edit_get.text)
        self.scrf2 = result.group(0).replace("editor.csrf_token2 = '", '').replace("';", '')
        pass

    def login(self):
        login_get = self.session.get(url=self.url['login'], headers=self.headers_ankiweb_get)
        login_get_soup = BeautifulSoup(login_get.content, 'html.parser')
        self.scrf = login_get_soup.find('input', {"name": "csrf_token"})['value']
        params = {
            'csrf_token': self.scrf,
            'password': self.password,
            'submitted': '1',
            'username': self.username
        }
        self.session.post(url=self.url['login'], data=params, headers=self.headers_ankiweb_post)
        self.cookie = self.session.cookies['ankiweb']
        pass

    def get_session_params(self):
        return {'cookie': self.cookie, 'scrf': self.scrf, 'scrf2':self.scrf2}

ankiweb = ANKIWEB()
ankiweb.login()
print(ankiweb.get_session_params())
ankiweb.get_scrf2()
print(ankiweb.get_session_params())
ankiweb.send(front='qwerty', back='ytrewq')