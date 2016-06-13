from time import localtime, strftime
from bs4 import BeautifulSoup
import logging
import re
import os


pathlog = os.environ['OPENSHIFT_LOG_DIR']
pathrepo = os.environ['OPENSHIFT_REPO_DIR']

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: LosToros :: %(levelname)s :: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=pathlog + 'report.log')

soup = BeautifulSoup(open(pathrepo + 'xml/lostoros.xml'))
guids = soup.find_all('guid')
regexplast = re.search('\d{4}/\d{1,2}/\d{1,2}', guids[0].get_text()).group()
hoy = strftime('%Y/%-m/%-d', localtime())

if regexplast != hoy:
    for g in guids:
        text = re.sub('\d{4}/\d{1,2}/\d{1,2}', hoy, g.get_text())
        text = re.sub('s_\d{8}', 's_' + strftime('%Y%m%d', localtime()), text)
        g.string = text
    for t in soup.find_all('title')[1:]:
        text = re.sub('\d{2}/\d{2}/\d{4}', strftime('%d/%m/%Y', localtime()), t.get_text())
        t.string = text
    for c in soup.find_all('enclosure'):
        text = re.sub('\d{4}/\d{1,2}/\d{1,2}', hoy, c.get('url'))
        text = re.sub('s_\d{8}', 's_' + strftime('%Y%m%d', localtime()), text)
        c['url'] = text
    for p in soup.find_all('pubdate'):
        p.string = strftime('%a, %d %h %Y %H:%m:%S +0200', localtime())
    with open(pathrepo + 'xml/lostoros.xml', "wb") as f:
        f.write(soup.renderContents())
    with open(pathrepo + 'xml/lostoros.txt', "r+") as w:
        d = int(w.read())
        w.seek(0)
        w.write(str(d + 10))
        w.truncate()
#    logging.info('RSS update ... [OK]')
#else:
#    logging.info('No hace falta actualizar!')
