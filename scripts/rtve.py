from bs4 import BeautifulSoup
import logging
import urllib.request
import datetime
import PyRSS2Gen
import re
import os

pathlog = os.environ['OPENSHIFT_LOG_DIR']
pathrepo = os.environ['OPENSHIFT_REPO_DIR']

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: RTVE :: %(levelname)s :: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=pathlog+'scripts.log')

error = False

soup = BeautifulSoup(open(pathrepo+'xml/rtve-_-docs.xml'))

L_titulos = soup.find_all('title')
L_titulos = [L_titulos[i].string for i in range(1, len(L_titulos))]
L_enlaces = soup.find_all('link')
L_enlaces = [L_enlaces[i].string for i in range(1, len(L_enlaces))]
L_descarga = soup.find_all('description')
L_descarga = [L_descarga[i].string for i in range(1, len(L_descarga))]

url = 'http://www.rtve.es/drmn/iso/catalog/?&col=3&extended=S&de=N&ll=N&playerid=&n2=%26Uacute%3Bltimos&c2=TEM&i2=70090&t2=VID&f2=N&o2=FP&e2&q2=&csel=2'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')
r = urllib.request.urlopen(req)
soup = BeautifulSoup(r.read().decode('iso-8859-1'))
nfo = soup.find_all('a', 'linkExtendedTrue')

W_titulos = [v.string for v in nfo]
W_enlaces = [v.get('href') for v in nfo]
W_descarga = []

if W_titulos[0] != L_titulos[0]:
    try:
        e = W_titulos.index(L_titulos[0])
        del W_titulos[e:]
        del W_enlaces[e:]
    except ValueError:
        pass

    for i in range(len(W_enlaces)):
        urlapi = 'http://www.descargavideos.tv/?web='+W_enlaces[i]
        reque = urllib.request.Request(urlapi)
        reque.add_header('User-Agent', 'Mozilla/5.0')
        f = urllib.request.urlopen(reque)
        data = f.read().decode('utf-8', 'ignore')
        datasoup = BeautifulSoup(data)
        try:
            link = re.findall('linkHtml\(\n\t\t\'(.*)\',', data)[0]
            if not link.endswith('.mp4') and not link.endswith('.flv'):
                raise Exception
            else:
                url_video = link
                W_descarga.append(url_video)
                logging.debug('%s ... [OK]', W_titulos[i])
        except:
            error = True
            error_res = datasoup.find('div', 'error_res').string
            W_descarga.append('... [Error!]')
            logging.error('%s, %s ... [Error!]', W_titulos[i], error_res)
            pass

    W_titulos.extend(L_titulos)
    W_enlaces.extend(L_enlaces)
    W_descarga.extend(L_descarga)
    titulos = W_titulos
    enlaces = W_enlaces
    descarga = W_descarga

    rss_items = []
    for i in range(len(W_enlaces)):
        item = PyRSS2Gen.RSSItem(title=titulos[i],
                                 link=enlaces[i],
                                 description=descarga[i])
        rss_items.append(item)

    rss = PyRSS2Gen.RSS2(
        title='RTVE Docs',
        link='http://pi-ton.rhcloud.com/xml/rtve-_-docs.xml',
        description='RTVE RSS Feed for documentaries',

        lastBuildDate=datetime.datetime.now(),

        items=rss_items)
    try:
        with open(pathrepo+'xml/rtve-_-docs.xml', 'w') as outfile:
            rss.write_xml(outfile)
        logging.info('RSS update ... [OK]')

    except:
        logging.error('404 Not found. ¡You shall not pass! Algo ha petao premoh')

elif W_titulos[0] == L_titulos[0]:
    logging.info('No hace falta actualizar!')
