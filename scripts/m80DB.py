from json import loads, dumps
from bs4 import BeautifulSoup
from time import sleep
import urllib.request
import logging
import os


def getsongs():
    try:
        url = 'http://np.tritondigital.com/public/nowplaying?mountName=M80RADIO&numberToFetch=50&eventType=track'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        req.add_header('Referer', 'http://www.m80radio.com/')
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode())
        artistas = soup.find_all(attrs={"name": "track_artist_name"})
        titulos = soup.find_all(attrs={"name": "cue_title"})
#        titulos = [t for t in titulos if t.string != '¿Te gusta @maximafm_radio? Compártelo con tus amigos, síguenos!!!']
        canciones = [artistas[i].string.replace(',', ', ') + ' - ' + titulos[i].string.replace(',', ', ') for i in range(len(artistas))]
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
                    format='%(asctime)s :: DBM80 :: %(levelname)s :: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=pathlog+'scripts.log')

with open(pathrepo + 'xml/m80DB.json', 'r') as r:
    dbcanciones = r.read()
    dbcanciones = loads(dbcanciones)
canciones = getsongs()
if canciones is not False:
    todb = checkdb(canciones, dbcanciones)
    if todb is True:
        with open(pathrepo + 'xml/m80DB.json', 'w') as w:
            w.write(dumps(dbcanciones, separators=(',', ':'), ensure_ascii=False))
        logging.info('DB update +{} ... [OK]'.format(count))
    else:
        logging.info('No hace falta actualizar!')
else:
    logging.error('404 Not found. ¡You shall not pass! Algo ha petao premoh')
