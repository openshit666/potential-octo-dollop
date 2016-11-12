from bs4 import BeautifulSoup
from random import choice
import urllib.request
import urllib.error


class getpls:
    def __init__(self, show):
        self.programas = {'wdm': {'radio': 'Los40', 'feed': 'http://urotrosfiles.media.streamtheworld.com/otrosfiles/podcasts/483.xml'}, 'nano': {'radio': 'LaMáxima', 'feed': 'http://urotrosfiles.media.streamtheworld.com/otrosfiles/podcasts/767.xml'}, 'armin': {'radio': 'LaMáxima', 'feed': 'https://miroppb.com/rss'}, 'insomnia': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/236303/podcast.xml'}, 'climax': {'radio': 'LaMáxima', 'feed': 'http://urotrosfiles.media.streamtheworld.com/otrosfiles/podcasts/707.xml'}, 'funk': {'radio': 'LaMáxima', 'feed': 'http://fapi-top.prisasd.com/podcast/maximafm/funk_and_show.xml'}, 'chillout': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/236321/podcast.xml'}, 'europa': {'radio': 'EuropaFM', 'feed': 'http://www.europafm.com/rss/podcast/236312/podcast.xml'}, 'atodojazz': {'radio': 'RNE', 'feed': 'http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq={}&orderCriteria=DESC&modl=TOC&locale=es&pageSize=15&ctx=1875'.format(choice(range(1, 45)))}, 'jazzporquesi': {'radio': 'RNE', 'feed': 'http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq={}&orderCriteria=DESC&modl=TOC&locale=es&pageSize=15&ctx=1999'.format(choice(range(1, 58)))}, 'tatw': {'radio': 'LaMáxima', 'feed': 'https://cdn.trancearoundtheworld.co.uk/podcasts/tatw/feed.xml'}, 'gtr': {'radio': 'LaMáxima', 'feed': 'http://static.aboveandbeyond.nu/grouptherapy/podcast.xml'}, 'tks': {'radio': 'LaMáxima', 'feed': 'http://www.djvytl.com/karandashow/'}}
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
        z = 0
        while z < 11:
            z+=1
            try:
                f = urllib.request.urlopen(req)
                break
            except urllib.error.URLError as e:
                if str(e.reason) != '[Errno 104] Connection reset by peer':
                    return None

        soup = BeautifulSoup(f.read().decode(), "html.parser")
        audios = soup.find_all('guid')
        Naudios = soup.find_all('enclosure')

        if self.show == 'armin' or self.show == 'gtr':
            audio = [Naudios[0].get('url')]
        elif self.show == 'climax':
            audio = [audios[2].get_text(), audios[1].get_text(), audios[0].get_text()]
        elif self.show == 'wdm' or self.show == 'nano':
            audio = [audios[1].get_text(), audios[0].get_text()]
        elif self.show == 'tatw':
            i = choice(range(len(Naudios)))
            audio = [Naudios[i - 1].get('url')]
        elif self.show == 'tks':
            Ntitles = soup.find_all('a')[5:103]
            i = choice(range(len(Ntitles)))
            audio = ['{}{}'.format(url, Ntitles[i].get('href'))]
        else:
            audio = [audios[0].get_text()]
        self.joinedpls = '[playlist]\n{}\nTitle{}={}\nNumberOfEntries={}\nVersion=2'.format('\n'.join(['File{}={}'.format(i + 1, audio[i]) for i in range(len(audio))]), len(audio), self.show, len(audio))

    def get_last_rne(self):
        url = self.programas[self.show]['feed']
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode(), "html.parser")
        audios = [a.get('href').replace('.lvlt.', '1.akcdn.') for a in soup.find_all(class_='download')]
        r = choice(range(len(audios)))
        self.joinedpls = '[playlist]\nFile1={}\nTitle1={}\nNumberOfEntries=1\nVersion=2'.format(audios[r], self.show)
