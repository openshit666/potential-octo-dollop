from bs4 import BeautifulSoup


soupALL = BeautifulSoup(open("/home/rc-manjaro/py/rtve-_-docs.xml"), "html.parser")
linksALL = soupALL.find_all('link')[1:]

soupPi = BeautifulSoup(open("/home/rc-manjaro/py/pi-ton/xml/rtve-_-docs.xml"), "html.parser")
linksPi = soupPi.find_all('link')[1:]

nope = []
for l in linksPi:
    if l not in linksALL:
        nope.append(l.string)

with open('/home/rc-manjaro/Desktop/nope.txt', 'w') as outfile:
    outfile.write(str(nope))

with open('/home/rc-manjaro/Desktop/first_30.txt', 'w') as outfile:
    outfile.write(str(linksPi[:30]))
