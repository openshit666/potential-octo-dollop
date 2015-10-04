from bs4 import BeautifulSoup
from time import localtime, strftime
import re
import os


pathlog = os.environ['OPENSHIFT_LOG_DIR']
pathrepo = os.environ['OPENSHIFT_REPO_DIR']

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: LosToros :: %(levelname)s :: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=pathlog+'scripts.log')

soup = BeautifulSoup(open(pathrepo+'xml/lostoros.xml'))
links = soup.find_all('link')[1:]
regexplast = re.search('\d{4}/\d{1,2}/\d{1,2}', links[0].get_text()).group()
hoy = strftime('%Y/%-m/%-d', localtime())

if regexplast != hoy:
    for l in links:
        text = re.sub('\d{4}/\d{1,2}/\d{1,2}', hoy, l.get_text())
        text = re.sub('s_\d{8}', 's_' + strftime('%Y%m%d', localtime()), text)
        l.string = text
    for t in soup.find_all('title')[1:]:
        text = re.sub('\d{2}/\d{2}/\d{4}', strftime('%d/%m/%Y', localtime()), t.get_text())
        t.string = text
    soup.lastbuilddate.string = strftime('%a, %d %h %Y %H:%m:%S GMT', localtime())
    with open('py/lostoros.xml', "wb") as f:
        f.write(soup.renderContents())
        logging.info('RSS update ... [OK]')
else:
    logging.info('No hace falta actualizar!')
