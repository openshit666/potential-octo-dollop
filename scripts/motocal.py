from datetime import datetime, timedelta
from time import strftime, strptime
from bs4 import BeautifulSoup
from pytz import timezone
from json import loads
import urllib.request
import locale
import os
import re


class mcal:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, '')
        tzutc = timezone("UTC")
        tzmadrid = timezone("Europe/Madrid")
        now = tzutc.localize(datetime.utcnow()).astimezone(tzmadrid).replace(tzinfo=None)
        pathrepo = os.environ['OPENSHIFT_REPO_DIR']
        with open('{}xml/.motocal.json'.format(pathrepo), 'r') as r:
            cal = loads(r.read())
            motocal = cal['motor']
            ciclical = cal['ciclismo']

        fin = (now - timedelta(hours=1.5)).strftime('%Y%m%d%H%M%S')
        gps = [k for k in sorted(motocal.keys()) if int(fin) < int(k)]
        gpscicli = [k for k in sorted(ciclical.keys()) if int(fin) < int(k)]

        self.nextgptext = ''
        for i in range(len(gps[:4])):
            nextgp = gps[i]
            tipo = motocal[nextgp]['tipo']
            if i > 1:
                self.nextgptext += '{} {}, {} #{}\n'.format(strftime('%A %-d %B', strptime(nextgp[:-6], '%Y%m%d')).title(), motocal[nextgp]['carrera'][tipo], motocal[nextgp]['gp'], tipo)
            else:
                if 'MotoGP' == tipo:
                    text = ''
                    kk = sorted(motocal[nextgp]['clasificacion'].keys())
                    kk.remove('Moto3')
                    kk.insert(0, 'Moto3')
                    for k in kk:
                        if k == kk[-1]:
                            text += '{}\t{}/{}\n'.format(k.replace('Moto2', 'Moto3'), motocal[nextgp]['clasificacion'][k], motocal[nextgp]['carrera'][k])
                        else:
                            text += '{}\t{}/{}\n'.format(k, motocal[nextgp]['clasificacion'][k], motocal[nextgp]['carrera'][k])
                    self.nextgptext += '{} #{}\nGP {}, {}\nClasificación/Carrera:\n{}{}\n\n'.format(strftime('%A %-d %B', strptime(nextgp[:-6], '%Y%m%d')).title(), tipo, motocal[nextgp]['gp'], motocal[nextgp]['location'], text, goodTime(datetime.strptime('{}{}:00'.format(nextgp[:-6], motocal[nextgp]['carrera'][tipo]), '%Y%m%d%H:%M:%S') - now, 'MOTOGP'))
                else:
                    self.nextgptext += '{} #{}\nGP {}, {}\nClasificación:\t{}\nCarrera:\t{}\n{}\n\n'.format(strftime('%A %-d %B', strptime(nextgp[:-6], '%Y%m%d')).title(), tipo, motocal[nextgp]['gp'], motocal[nextgp]['location'], motocal[nextgp]['clasificacion'][tipo], motocal[nextgp]['carrera'][tipo], goodTime(datetime.strptime('{}{}:00'.format(nextgp[:-6], motocal[nextgp]['carrera'][tipo]), '%Y%m%d%H:%M:%S') - now, 'FORMULA 1'))
        if len(gpscicli) > 1:
            self.nextgptext += '{}, {}@, {} #Ciclismo'.format(strftime('%A %-d %B', strptime(gpscicli[0][:-6], '%Y%m%d')).title(), goodTime(datetime.strptime(gpscicli[0][:-2], '%Y%m%d%H%M') - datetime.now(), None).split(',')[0], ciclical[gpscicli[0]]['name'])


def get_avs(cual, modo):
    qavs = {}
    ravs = {}
    allavs = {}
    response = ''
    url = 'https://www.arenavision.ru/guide'
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Cookie', 'beget=begetok')
    f = urllib.request.urlopen(req)
    soup = BeautifulSoup(f.read().decode('utf-8'), "html.parser")
    width = soup.select_one('tr > td:nth-of-type(3)').get('style')
    cualgp = soup.find('td', text=re.compile(cual), style=width).find_next_sibling('td').get_text()
    qualy = list(filter(None, ' '.join([x.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').get_text() for x in soup.find_all('td', text=re.compile(cual), style=width) if cual.replace('FORMULA 1', 'QUALIFYING').replace('MOTOGP', 'QP') in x.find_next_sibling('td').find_next_sibling('td').get_text() and cualgp in x.find_next_sibling('td').get_text()]).split(']')))
    for q in qualy:
        try:
            qavs[q[-3:]] += sorted([int(av) for av in re.findall('(?<!S)\d+', q)])
        except KeyError:
            qavs[q[-3:]] = sorted([int(av) for av in re.findall('(?<!S)\d+', q)])
    race = list(filter(None, ' '.join([x.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').get_text() for x in soup.find_all('td', text=re.compile(cual), style=width) if 'RACE' in x.find_next_sibling('td').find_next_sibling('td').get_text() and cualgp in x.find_next_sibling('td').get_text()]).split(']')))
    for r in race:
        try:
            ravs[r[-3:]] += sorted([int(av) for av in re.findall('(?<!S)\d+', r)])
        except KeyError:
            ravs[r[-3:]] = sorted([int(av) for av in re.findall('(?<!S)\d+', r)])
    for q in qavs:
        qavs[q] = sorted(set(qavs[q]))
    for r in ravs:
        ravs[r] = sorted(set(ravs[r]))
    if modo == 'qualy':
        lavs = [val for subl in sorted(list(qavs.values())) for val in subl]
        for key, val in sorted(qavs.items(), key=lambda k: k[1][1]):
            response += '{}: {} {} -'.format(modo.title(), key, val)
    else:
        lavs = [val for subl in sorted(list(ravs.values())) for val in subl]
        for key, val in sorted(ravs.items(), key=lambda k: k[1][1]):
            response += '{}: {} {} -'.format(modo.title(), key, val)
    response = response[::-1].replace('- ', '\n', 1)[::-1]
    for av in lavs:
        url = 'https://www.arenavision.ru/av{}'.format(av)
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        req.add_header('Cookie', 'beget=begetok')
        req.add_header('Referer', 'https://www.arenavision.ru/guide')
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode('utf-8'), "html.parser")
        allavs[av] = soup.find(href=re.compile('acestream://')).get('href').replace('acestream://', '')
    for av in sorted(list(allavs.keys())):
        response += 'av{}: {}\n'.format(av, allavs[av])
    return response[::-1].replace('\n', '', 1)[::-1]


def goodTime(timeleft, cual):
    countdown = [timeleft.days, int(timeleft.seconds / 3600), int((timeleft.seconds / 3600 - int(timeleft.seconds / 3600)) * 60)]
    text = ['día', 'hora', 'minuto']
    msg = '@Faltan '
    for i in range(3):
        if countdown[i] != 0:
            if countdown[i] > 1:
                msg += '{} {}s'.format(countdown[i], text[i])
                if i != 2:
                    msg += ', '
            else:
                msg += '{} {}'.format(countdown[i], text[i])
                if i != 2:
                    msg += ', '

    if timeleft.days == -1:
        if cual is None:
            return '@¡¡Live!!@'
        avs = get_avs(cual, 'race')
        return '@¡¡Live!!@\n{}'.format(avs)
    elif timeleft.days == 0 and timeleft.seconds <= 75600:
        if cual is None:
            return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
        avs = get_avs(cual, 'race')
        return '{}@\n{}'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1], avs)
    elif timeleft.days <= 2:
        if cual is None:
            return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
        avs = get_avs(cual, 'qualy')
        return '{}@\n{}'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1], avs)
    if cual is None:
        return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
    return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
