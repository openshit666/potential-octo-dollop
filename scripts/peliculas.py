from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import re
import datetime
import PyRSS2Gen
import time

soup = BeautifulSoup(open("scripts/dvdr-_-movies.xml"))
L_titulos = soup.find_all('title')
L_titulos = [L_titulos[i].string for i in range(1, len(L_titulos))]
L_enlaces = soup.find_all('link')
L_enlaces = [L_enlaces[i].string for i in range(1, len(L_enlaces))]

url = 'http://todotorrents.com'
data = urllib.parse.urlencode({'Submit2': 'Buscar', 'buscar': '[MoviesDVDR]', 'cate': '3', 'estado': '1'})
data = data.encode('iso-8859-1')
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')
req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=iso-8859-1')
r = urllib.request.urlopen(req, data)
soup = BeautifulSoup(r.read().decode('iso-8859-1'))
a_hrefs = soup.find_all(href=re.compile('/download'))
a_titles = soup.find_all(href=re.compile('/descargar/'))

W_enlaces = ['http://todotorrents.com'+v.get('href') for v in a_hrefs]
W_titulos = [v.get('title').split('DVDR')[0].strip() for v in a_titles]


if W_titulos[0] != L_titulos[0]:
    e = W_titulos.index(L_titulos[0])
    del W_titulos[e:]
    del W_enlaces[e:]
    for t in W_titulos:
        print(t)
    W_titulos.extend(L_titulos)
    W_enlaces.extend(L_enlaces)
    titulos = W_titulos
    enlaces = W_enlaces

    rss_items = []
    for i in range(len(enlaces)):
        item = PyRSS2Gen.RSSItem(title=titulos[i],
                                 link=enlaces[i])
        rss_items.append(item)

    rss = PyRSS2Gen.RSS2(
        title='MoviesDVDR',
        link='http://pi-ton.rhcloud.com/dvdr-_-movies.xml',
        description='TodoTorrents RSS Feed for DVDR-Movies',

        lastBuildDate=datetime.datetime.now(),

        items=rss_items)
    try:
        with open('scripts/dvdr-_-movies.xml', 'w') as outfile:
            rss.write_xml(outfile)
        print('RSS update ... [OK]')

    except:
        print('404 Not found. ¡You shall not pass! Algo ha petao premoh')

elif W_titulos[0] == L_titulos[0]:
    print('No hace falta actualizar!')

x = 6
for i in range(x):
    print('.', end="", flush=True)
    time.sleep(0.5)
    if i == x-1:
        print(' bye!')
        time.sleep(0.5)
