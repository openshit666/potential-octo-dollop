from datetime import datetime, timedelta
from time import strftime, strptime
from bs4 import BeautifulSoup
from json import loads
import urllib.request
import locale
import os
import re


class mcal:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, '')
        now = datetime.now() + timedelta(hours=6)
        pathrepo = os.environ['OPENSHIFT_REPO_DIR']
        with open('{}xml/motocal.json'.format(pathrepo), 'r') as r:
            motocal = loads(r.read())

        fin_motogp = (now - timedelta(hours=1)).strftime('%Y%m%d%H%M%S')
        fin_f1 = (now - timedelta(hours=2)).strftime('%Y%m%d%H%M%S')
        nextmotogp = [f for f in sorted(list(motocal['motogp'].keys())) if int(fin_motogp) < int(datetime.strftime(datetime.strptime('{}{}:00'.format(f, motocal['motogp'][f]['carrera']['MotoGP']), '%Y%m%d%H:%M:%S'), '%Y%m%d%H%M%S'))][0]
        nextf1gp = [f for f in sorted(list(motocal['f1'].keys())) if int(fin_f1) < int(datetime.strftime(datetime.strptime('{}{}:00'.format(f, motocal['f1'][f]['carrera']['F1']), '%Y%m%d%H:%M:%S'), '%Y%m%d%H%M%S'))][0]
        try:
            nextnextmotogp = sorted(list(motocal['motogp'].keys()))[sorted(list(motocal['motogp'].keys())).index(nextf1gp) + 1]
        except:
            nextnextmotogp = 666
            pass
        try:
            nextnextf1gp = sorted(list(motocal['f1'].keys()))[sorted(list(motocal['f1'].keys())).index(nextf1gp) + 1]
        except:
            nextnextf1gp = 666
            pass
        if int(datetime.strftime(datetime.strptime('{}{}:00'.format(nextf1gp, motocal['f1'][nextf1gp]['carrera']['F1']), '%Y%m%d%H:%M:%S'), '%Y%m%d%H%M%S')) < int(datetime.strftime(datetime.strptime('{}{}:00'.format(nextmotogp, motocal['motogp'][nextmotogp]['carrera']['MotoGP']), '%Y%m%d%H:%M:%S'), '%Y%m%d%H%M%S')):
            self.nextgptext = '{} #F1\nGP {}, {}\nClasificación: {}\nCarrera: {}\n{}'.format(strftime('%A %-d %B', strptime(nextf1gp, '%Y%m%d')).title(), motocal['f1'][nextf1gp]['gp'], motocal['f1'][nextf1gp]['location'], motocal['f1'][nextf1gp]['clasificacion']['F1'], motocal['f1'][nextf1gp]['carrera']['F1'], goodTime(datetime.strptime('{}{}:00'.format(nextf1gp, motocal['f1'][nextf1gp]['carrera']['F1']), '%Y%m%d%H:%M:%S') - now, 'FORMULA 1'))
            if 666 < int(nextnextf1gp) <= int(nextmotogp):
                self.nextgptext +='\n\n{} {}, {} #F1'.format(strftime('%A %-d %B', strptime(nextnextf1gp, '%Y%m%d')).title(), motocal['f1'][nextnextf1gp]['carrera']['F1'], motocal['f1'][nextnextf1gp]['gp'])
            self.nextgptext += '\n\n{} #MotoGP\nGP {}, {}\nClasificación/Carrera:\nMoto3   {}/{}\nMoto2   {}/{}\nMotoGP  {}/{}\n{}'.format(strftime('%A %-d %B', strptime(nextmotogp, '%Y%m%d')).title(), motocal['motogp'][nextmotogp]['gp'], motocal['motogp'][nextmotogp]['location'], motocal['motogp'][nextmotogp]['clasificacion']['Moto3'], motocal['motogp'][nextmotogp]['carrera']['Moto3'], motocal['motogp'][nextmotogp]['clasificacion']['Moto2'], motocal['motogp'][nextmotogp]['carrera']['Moto2'], motocal['motogp'][nextmotogp]['clasificacion']['MotoGP'], motocal['motogp'][nextmotogp]['carrera']['MotoGP'], goodTime(datetime.strptime('{}{}:00'.format(nextmotogp, motocal['motogp'][nextmotogp]['carrera']['MotoGP']), '%Y%m%d%H:%M:%S') - now, 'MOTOGP'))
        else:
            self.nextgptext = '{} #MotoGP\nGP {}, {}\nClasificación/Carrera:\nMoto3   {}/{}\nMoto2   {}/{}\nMotoGP  {}/{}\n{}'.format(strftime('%A %-d %B', strptime(nextmotogp, '%Y%m%d')).title(), motocal['motogp'][nextmotogp]['gp'], motocal['motogp'][nextmotogp]['location'], motocal['motogp'][nextmotogp]['clasificacion']['Moto3'], motocal['motogp'][nextmotogp]['carrera']['Moto3'], motocal['motogp'][nextmotogp]['clasificacion']['Moto2'], motocal['motogp'][nextmotogp]['carrera']['Moto2'], motocal['motogp'][nextmotogp]['clasificacion']['MotoGP'], motocal['motogp'][nextmotogp]['carrera']['MotoGP'], goodTime(datetime.strptime('{}{}:00'.format(nextmotogp, motocal['motogp'][nextmotogp]['carrera']['MotoGP']), '%Y%m%d%H:%M:%S') - now, 'MOTOGP'))
            if 666 < int(nextnextmotogp) <= int(nextf1gp):
                self.nextgptext +='\n\n{} {}, {} #MotoGP\n'.format(strftime('%A %-d %B', strptime(nextnextmotogp, '%Y%m%d')).title(), motocal['motogp'][nextnextmotogp]['carrera']['MotoGP'], motocal['motogp'][nextnextmotogp]['gp'])
            self.nextgptext += '\n\n{} #F1\nGP {}, {}\nClasificación: {}\nCarrera: {}\n{}'.format(strftime('%A %-d %B', strptime(nextf1gp, '%Y%m%d')).title(), motocal['f1'][nextf1gp]['gp'], motocal['f1'][nextf1gp]['location'], motocal['f1'][nextf1gp]['clasificacion']['F1'], motocal['f1'][nextf1gp]['carrera']['F1'], goodTime(datetime.strptime('{}{}:00'.format(nextf1gp, motocal['f1'][nextf1gp]['carrera']['F1']), '%Y%m%d%H:%M:%S') - now, 'FORMULA 1'))


def get_avs(cual, modo):
    qavs = {}
    ravs = {}
    allavs = {}
    response = ''
    url = 'http://www.arenavision.in/agenda'
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    f = urllib.request.urlopen(req)
    soup = BeautifulSoup(f.read().decode('utf-8'), "html.parser")
    qualy = list(filter(None, ' '.join([x.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').get_text() for x in soup.find_all('td', text=re.compile(cual), style="width: 188px") if cual.replace('FORMULA 1', 'QUALIFYING').replace('MOTOGP', 'QP') in x.find_next_sibling('td').find_next_sibling('td').get_text()]).split(']')))
    for q in qualy:
        try:
            qavs[q[-3:]] += sorted([int(av) for av in re.findall('(?<!S)\d+', q)])
        except KeyError:
            qavs[q[-3:]] = sorted([int(av) for av in re.findall('(?<!S)\d+', q)])
    race = list(filter(None, ' '.join([x.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').get_text() for x in soup.find_all('td', text=re.compile(cual), style="width: 188px") if 'RACE' in x.find_next_sibling('td').find_next_sibling('td').get_text()]).split(']')))
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
        url = 'http://www.arenavision.in/av{}'.format(av)
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
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
    elif (timeleft.days <= 1 and timeleft.seconds <= 10800) or (timeleft.days == 0 and timeleft.seconds >= 75600):
        if cual is None:
            return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
        avs = get_avs(cual, 'qualy')
        return '{}@\n{}'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1], avs)
    elif timeleft.days == 0 and timeleft.seconds <= 75600:
        if cual is None:
            return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
        avs = get_avs(cual, 'race')
        return '{}@\n{}'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1], avs)
    if cual is None:
        return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
    return '{}@'.format(msg[::-1].replace(' ,', ' y ', 1)[::-1])
