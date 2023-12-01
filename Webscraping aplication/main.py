from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import whois #python-whois
import datetime
import re
from threading import Thread, Lock
from queue import Queue

# de parameters die wij gaan toevoegen aan het neural network zijn
# 1: Database voor scam triggerwoorden https://mailmeteor.com/blog/spam-words
def check_keywords(text_lowered, file):
    f = open(file, "r")
    count = 0
    for word in f.readlines():
        count += text_lowered.count((word.replace("\n", "")).lower())
    return count

# 2: https of https
# 3: lengte van de url
def urlcheck(url):
    if url[:5] == "https":
        return ["https", len(urlparse(url).netloc)]
    return ["http", len(urlparse(url).netloc)]

# 4: dit soort characters: “//*” “<!” “ =” “//..//”.
def check_special(page):
    special = ["//*", "<!", " =", "//..//", "<!-- ", " -->"]
    count = 0
    for character in special:
        count += page.count(character) * len(character)
    return count / len(page) * 100

# 5: hoe oud de website is
def get_oldness_days(url):
    try:
        domain = urlparse(url).netloc
        loaded_domain = whois.whois(domain) # get the whois data
        date = loaded_domain.get("creation_date")
        if isinstance(date, list): #if there are multiple dates
            return (datetime.datetime.now() - date[0]).total_seconds() / 86400 # return the date difference in days
        else:
            return (datetime.datetime.now() - date).total_seconds() / 86400 # return the date difference in days
    except:
        return 0


# 6: als de method post wordt gebruikt
# 7: bij image preloading
# 8: Of het whatsapp bevat
# 9: Het aantal srcs
# 10: Het aantal hrefs
# 11 t/m 13: correlatie volgens https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/anti-spam-policies-asf-settings-about?view=o365-worldwide



# Hier worden de scripts uitgewerk met de gemaakte functies
def get_stuff(q, lock, goodorbad):
    while True:
        # Wij gaan het opslaan in deze volgorde url, goede website, slechte website,(kenmerken) 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
        # de goodorbad moet [1, 0] zijn voor good en [0, 1] zijn voor bad
        url = q.get()
        q.task_done()
        characteristics = [url]
        characteristics.extend(goodorbad)

        # Dit zijn alle benodigdheden, een try statement voor als de website niet meer bestaat.
        try:
            page = requests.get(url, headers={'User-Agent': 'AdsBot-Google'})
            soup = BeautifulSoup(page.text, 'html.parser')
            text = soup.body.get_text(' ', strip=True)
        except:
            continue

        if not len(text) != 0:
            continue

        #1
        characteristics.append(check_keywords(text.lower(), "triggerwords.txt") / len(text.strip()) * 100)

        # 2 en 3
        characteristics.extend(urlcheck(url))

        # 4
        characteristics.append(check_special(page.text))

        # 5
        characteristics.append(get_oldness_days(url))

        #Een lijstje van allemaal dingen die wij willen checken
        HTMLelements = ["post", "preload", "whatsapp", "src=", "href=", "<form", "<iframe", "<img"]
        for element in HTMLelements:
            characteristics.append(page.text.lower().count(element) * len(element) / len(page.text) * 100)

        with lock:
            print(f"{characteristics},")

if __name__ == '__main__':
    print("doing bad websites \n[")
    bad = open("Badwebsites.txt", "r")
    bad_queue = Queue()
    lock = Lock()

    for i in range(10):
        thread = Thread(target=get_stuff, args=(bad_queue, lock, [0, 1]))
        thread.daemon = True
        thread.start()

    for word in bad.readlines():
        bad_queue.put(word.replace("\n", ""))
    bad_queue.join()

    print("]\ndoing good websites \n[")
    good = open("Goodwebsites.txt", "r")
    good_queue = Queue()
    lock = Lock()

    for i in range(10):
        thread = Thread(target=get_stuff, args=(good_queue, lock, [1, 0]))
        thread.daemon = True
        thread.start()

    for word in good.readlines():
        good_queue.put(word.replace("\n", ""))
    good_queue.join()
    print("]\ndone")





