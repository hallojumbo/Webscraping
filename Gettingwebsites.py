import os
import json
import requests
from bs4 import BeautifulSoup


def Active(domain, txt):
    hostname = domain
    response = os.system("ping -n 1 " + hostname)
    print("\none website done")
    if response == 0:
        txt.write(f"{hostname}\n")  # writing the file if active
        return True
    else:
        return False

def getGoodWebsites():
    counter = 0 #we only want 500 websites

    with open("Goodwebsites.txt", mode="wt") as Goodwebsites:
        f = open("ranked_domains.json", "r") #handy json file
        data = json.loads(f.read())
        for i in data:
            position = i.get("position")
            if position > 350: #getting the position of the less popular websites
                hostname = i.get("domain")
                if Active(hostname, Goodwebsites): #writing if active
                    counter += 1
                    print(f"\nSuccesfully written url, count is {counter}")
            if(counter == 500):
                Goodwebsites.close()
                return
        Goodwebsites.close()

def getBadWebsites():
    counter = 0 #we only want 500 websites

    with open("Badwebsites.txt", mode="wt") as Badwebsites:
        for i in range(1, 1001, 20):  # List goes from 1 to 20
            page = requests.get(f"https://db.aa419.org/fakebankslist.php?start={i}")  # Getting the url
            soup = BeautifulSoup(page.text, 'html.parser')
            for link in soup.find_all(class_='tddomain'):
                a = link.find('a').text
                if a != "\nUrl ":  # This is the header
                    if Active(a.replace("http://www.","").replace("https://www.",""), Badwebsites): #writing if active and removing the HTTP
                        counter += 1
                        print(f"\nSuccesfully written url, count is {counter}")
                if counter == 500:
                    Badwebsites.close()
                    return
        Badwebsites.close()

if __name__ == '__main__':
    print("\nStarting good websites \n")
    getGoodWebsites()
    print("\nDone with good websites \n")
    print("Starting bad websites \n")
    getBadWebsites()
    print("\nDone with bad websites \n")
