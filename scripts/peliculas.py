from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import PyRSS2Gen
import datetime
import logging
import os


def get_torrent(url):
    req = urllib.request.Request('http://www.moviesdvdr.com/{}'.format(url))
    req.add_header('User-Agent', 'Mozilla/5.0')
    r = urllib.request.urlopen(req)
    soup = BeautifulSoup(r.read().decode('iso-8859-1'), "html.parser")
    return 'http://www.moviesdvdr.com/{}'.format(soup.find(string='Descargar TORRENT').parent.get('href'))


pathlog = os.environ['OPENSHIFT_LOG_DIR']
pathrepo = os.environ['OPENSHIFT_REPO_DIR']
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: DVDR :: %(levelname)s :: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=pathlog + 'report.log')

soup = BeautifulSoup(open(pathrepo + 'xml/dvdr-_-movies.xml'), "html.parser")
L_titulos = soup.find_all('title')
L_titulos = [L_titulos[i].string for i in range(1, len(L_titulos))]
L_enlaces = soup.find_all('link')
L_enlaces = [L_enlaces[i].string for i in range(1, len(L_enlaces))]
url = 'http://www.moviesdvdr.com/'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')
r = urllib.request.urlopen(req)
soup = BeautifulSoup(r.read().decode('iso-8859-1'), "html.parser")
W_titulos = [t.get('alt') for t in soup.find_all('img', alt=True, width=True)]
W_enlaces = [get_torrent(t.parent.get('href')) for t in soup.find_all('img', alt=True, width=True)]

if W_titulos[0] != L_titulos[0]:
    e = W_titulos.index(L_titulos[0])
    del W_titulos[e:]
    del W_enlaces[e:]
    for t in W_titulos:
        logging.debug('%s ... [OK]', t)
    W_titulos.extend(L_titulos)
    W_enlaces.extend(L_enlaces)
    titulos = W_titulos
    enlaces = W_enlaces

    rss_items = []
    for i in range(len(enlaces)):
        # fix titulo vacío
        item = PyRSS2Gen.RSSItem(title=titulos[i],
                                 link=enlaces[i])
        rss_items.append(item)

    rss = PyRSS2Gen.RSS2(
        title='MoviesDVDR',
        link='http://pi-ton.rhcloud.com/xml/dvdr-_-movies.xml',
        description='TodoTorrents RSS Feed for DVDR-Movies',

        lastBuildDate=datetime.datetime.now(),

        items=rss_items)
    try:
        with open(pathrepo + 'xml/dvdr-_-movies.xml', 'w') as outfile:
            rss.write_xml(outfile)
            logging.info('RSS update ... [OK]')

    except:
        logging.error('404 Not found. ¡You shall not pass! Algo ha petao premoh')

elif W_titulos[0] == L_titulos[0]:
    logging.info('No hace falta actualizar!')
