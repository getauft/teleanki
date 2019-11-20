GET https://ankiweb.net/account/login
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'ankiweb=login',
'DNT':1,
'Host':'ankiweb.net',
'Referer':'https://ankiweb.net/',
'TE':'Trailers',
'Upgrade-Insecure-Requests':1,
'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'

POST https://ankiweb.net/account/login (отдает куки)
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'keep-alive',
'Content-Type':'application/x-www-form-urlencoded',
'Cookie':'ankiweb=login',
'DNT':1,
'Host':'ankiweb.net',
'Referer':'https://ankiweb.net/account/login',
'TE':'Trailers',
'Upgrade-Insecure-Requests':1,
'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'

GET https://ankiuser.net/edit/ (нужно передавать куки)(на странице в скрипте scfr2)
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'keep-alive',
'Cookie':'ankiweb=iO4NkM8pK0EVlHjr',
'DNT':1,
'Host':'ankiuser.net',
'Referer':'https://ankiweb.net/',
'TE':'Trailers',
'Upgrade-Insecure-Requests':1,
'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'

POST https://ankiuser.net/edit/save (нужно передавать куки) (нужно передавать параметры)
'Accept':'*/*',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
'Connection':'keep-alive',
'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie':'ankiweb=iO4NkM8pK0EVlHjr',
'DNT':1,
'Host':'ankiuser.net',
'Referer':'https://ankiuser.net/edit/',
'TE':'Trailers',
'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
'X-Requested-With':'XMLHttpRequest'

csrf_token:eyJpYXQiOiAxNTQzMjU2MDA4LCAib3AiOiAiZWRpdCIsICJ1aWQiOiAiM2FiZDgyYWYifQ.plLz1yQ4RM2y8f4HKAmDO81VyWMYqoU95Rjy30P-3kQ
data: [["Front","Back"],"Tags"]
deck: Phrases
mid: 1540747305545

#.