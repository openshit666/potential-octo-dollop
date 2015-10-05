from json import loads, dumps
from bs4 import BeautifulSoup
from time import sleep
import urllib.request
import logging
import os


def getsongs(radio):
    try:
        url = 'http://np.tritondigital.com/public/nowplaying?mountName={}&numberToFetch=50&eventType=track'.format(radio)
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode())
        canciones = [c.contents[3].string.replace(',', ', ') + ' - ' + c.contents[1].string.replace(',', ', ') for c in soup.find_all(attrs={'mountname': '{}'.format(radio)}) if len(c.contents) == 6]
        return canciones
    except:
        pass
    return False


def checkdb(canciones, dbcanciones):
    global count
    count = 0
    todb = False
    for c in canciones:
        if c not in dbcanciones['canciones']:
            dbcanciones['canciones'].append(c)
            todb = True
            count+=1
    return todb


pathlog = os.environ['OPENSHIFT_LOG_DIR']
pathrepo = os.environ['OPENSHIFT_REPO_DIR']
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: {} :: %(levelname)s :: %(message)s'.format(radio),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=pathlog+'scripts.log')

radios = ['MAXIMAFM', 'M80RADIO']
for radio in radios:
    with open(pathrepo + 'xml/{}.json'.format(radio), 'r') as r:
        dbcanciones = r.read()
        dbcanciones = loads(dbcanciones)
    canciones = getsongs(radio)
    if canciones is not False:
        todb = checkdb(canciones, dbcanciones)
        if todb is True:
            with open(pathrepo + 'xml/{}.json'.format(radio), 'w') as w:
                w.write(dumps(dbcanciones, separators=(',', ':'), ensure_ascii=False))
            logging.info('DB update +{} ... [OK]'.format(count))
        else:
            logging.info('No hace falta actualizar!')
    else:
        logging.error('404 Not found. ¡You shall not pass! Algo ha petao premoh')
