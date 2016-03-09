from bs4 import BeautifulSoup
from random import choice
import urllib.request


class getpls:
    def __init__(self, show):
        self.programas = {'wdm': {'radio': 'Los40', 'feed': 'http://urotrosfiles.media.streamtheworld.com/otrosfiles/podcasts/483.xml'}, 'nano': {'radio': 'LaMáxima', 'feed': 'http://www.radioasturias.com/rss_audios.asp?emisora=Maxima+FM+Asturias&programa=Bien+Bailao'}, 'carl': {'radio': 'LaMáxima', 'feed': 'http://www.radioasturias.com/rss_audios.asp?emisora=Maxima+FM+Asturias&programa=Global+Carl+Cox'}, 'armin': {'radio': 'LaMáxima', 'feed': 'http://www.radioasturias.com/rss_audios.asp?emisora=Maxima+FM+Asturias&programa=F%C3%B3rmula+M%C3%A1xima'}, 'insessions': {'radio': 'LaMáxima', 'feed': 'http://www.radioasturias.com/rss_audios.asp?emisora=Maxima+FM+Asturias&programa=In+Sessions'}, 'insomnia': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/236303/podcast.xml'}, 'climax': {'radio': 'LaMáxima', 'feed': 'http://www.radioasturias.com/rss_audios.asp?emisora=Maxima+FM+Asturias&programa=Cl%C3%ADmax+Chill+Out'}, 'chillout': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/236321/podcast.xml'}, 'europa': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/236312/podcast.xml'}, 'brian': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/256645/podcast.xml'}, 'atodojazz': {'radio': 'RNE', 'feed': 'http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq={}&orderCriteria=DESC&modl=TOC&locale=es&pageSize=15&ctx=1875'.format(choice(range(1, 45)))}, 'jazzporquesi': {'radio': 'RNE', 'feed': 'http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq={}&orderCriteria=DESC&modl=TOC&locale=es&pageSize=15&ctx=1999'.format(choice(range(1, 58)))}}
        self.allpro = list(self.programas.keys()) + ['random', 'randomdance', 'randomjazz']
        if show == 'random':
            self.show = choice(list(self.programas.keys()))
        elif show == 'randomjazz':
            self.show = choice(['jazzporquesi', 'atodojazz'])
        elif show == 'randomdance':
            x = [k for k in list(self.programas.keys()) if k != 'jazzporquesi' and k != 'atodojazz']
            self.show = choice(x)
        elif show in self.programas.keys():
            self.show = show
        else:
            return None
        if self.programas[self.show]['radio'] == 'RNE':
            self.get_last_rne()
        else:
            self.get_last()

    def get_last(self):
        url = self.programas[self.show]['feed']
        radio = self.programas[self.show]['radio']
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode(), "html.parser")
        audios = soup.find_all('guid')

        if self.show == 'insessions':
            ultis = list(range(-7, 0))
            uno = choice(ultis)
            ultis.remove(uno)
            dos = choice(ultis)
            aa = sorted([audios[uno].get_text(), audios[dos].get_text()])
            audio = [aa[0], aa[1]]
        elif self.show == 'armin':
            ttaa = [(d.find_previous_siblings('title')[0].get_text().replace('Fórmula Máxima', 'A State of Trance'), d.find_next_siblings('guid')[0].get_text()) for d in soup.find_all('description') if 'domingo' in d.get_text() and '22:00' in d.get_text() or 'domingo' in d.get_text() and '23:00' in d.get_text()]
            audio = [ttaa[-2][1], ttaa[-1][1]]
        elif self.show == 'wdm':
            audio = [audios[1].get_text(), audios[0].get_text()]
        elif radio == 'LaMáxima':
            audio = [audios[-2].get_text(), audios[-1].get_text()]
        else:
            audio = [audios[0].get_text()]
        self.joinedpls = '[playlist]\n{}\nTitle1={}\nNumberOfEntries={}'.format('\n'.join(['file{}={}'.format(i + 1, audio[i]) for i in range(len(audio))]), self.show, len(audio))

    def get_last_rne(self):
        url = self.programas[self.show]['feed']
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode(), "html.parser")
        audios = [a.get('href').replace('.lvlt.', '1.akcdn.') for a in soup.find_all(class_='download')]
        r = choice(range(len(audios)))
        self.joinedpls = '[playlist]\nFile1={}\nTitle1={}\nNumberOfEntries=1\nVersion=2'.format(audios[r], self.show)
