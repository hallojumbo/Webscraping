import tensorflow as tf
from urllib.parse import urlparse
from bs4 import BeautifulSoup  # beautifulsoup4
import requests
import whois  # python-whois
import datetime
import sys


# de parameters die wij gaan toevoegen aan het neural network zijn
# 1: Database voor scam triggerwoorden https://help.salesforce.com/s/articleView?id=sf.mc_es_trigger_words.htm&type=5
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
        return [1, len(urlparse(url).netloc)]
    return [0, len(urlparse(url).netloc)]


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
        loaded_domain = whois.whois(domain)  # get the whois data
        date = loaded_domain.get("creation_date")
        if isinstance(date, list):  # if there are multiple dates
            return (datetime.datetime.now() - date[0]).total_seconds() / 86400  # return the date difference in days
        else:
            return (datetime.datetime.now() - date).total_seconds() / 86400  # return the date difference in days
    except:
        return 0


# 6: als de method post wordt gebruikt
# 7: bij image preloading
# 8: Of het whatsapp bevat
# 9: Het aantal srcs
# 10: Het aantal hrefs
# 11 t/m 13: correlatie volgens https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/anti-spam-policies-asf-settings-about?view=o365-worldwide

def get_stuff(url):
    characteristics = []
    # Dit zijn alle benodigdheden, een try statement voor als de website niet meer bestaat.
    try:
        page = requests.get(url, headers={'User-Agent': 'AdsBot-Google'})
        soup = BeautifulSoup(page.text, 'html.parser')
        text = soup.body.get_text(' ', strip=True)
    except:
        return 0

    if (len(text) == 0):
        return 0

    # 1
    characteristics.append(check_keywords(text.lower(), "triggerwords.txt") / len(text.strip()) * 100)

    # 2 en 3
    characteristics.extend(urlcheck(url))

    # 4
    characteristics.append(check_special(page.text))

    # 5
    characteristics.append(get_oldness_days(url))

    # Een lijstje van allemaal dingen die wij willen checkenYuBlam
    HTMLelements = ["post", "preload", "whatsapp", "src=", "href=", "<form", "<iframe", "<img"]
    for element in HTMLelements:
        characteristics.append(page.text.lower().count(element) * len(element) / len(page.text) * 100)

    return characteristics


if __name__ == "__main__":
    print("De AI laden...")
    average = [0.61104044, 0.95825427, 20.49525617, 0.42170777, 4369.14721496, 0.08884886, 0.01439478, 0.01341572,
               0.20849571, 0.59853586, 0.00965875, 0.00579614, 0.1085275]
    deviation = [0.42115669, 0.20000756, 6.68280216, 0.64935835, 4603.15875707, 0.12776998, 0.03932445, 0.11351909,
                 0.19531467, 0.47577819, 0.02506296, 0.03746394, 0.13103639]
    model = tf.keras.models.load_model('scamDetector.keras')
    print("klaar\n")

    while True:
        url = input("Welke url wilt u checken? ")
        data = [get_stuff(url)]
        if data[0] != 0:
            print(data)
            print("Als veel van de data gelijk is aan 0, is de voorspelling niet accuraat")
            for index in range(13):
                data[0][index] -= average[index]
                if deviation[index] != 0:
                    data[0][index] /= deviation[index]
            print(data)
            print(f'Hoeveelheid betrouwbare eigenschappen van 0-1: {(model.predict(data))[0]}\nHoeveelheid frauduleuze van 0-1: {(model.predict(data))[1]}')
        else:
            print("Kan de website niet vinden")

        if input("Ben je klaar? ") == "ja":
            sys.exit()
