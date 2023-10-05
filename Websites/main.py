import requests
from bs4 import BeautifulSoup


def Active(domain, txt):
    hostname = domain
    try:
        response = requests.get(hostname, headers={'User-Agent': 'AdsBot-Google'}, timeout=2)
        print(f"\n{hostname}")
        print("One website done")
        print(f"Status code was: {response.status_code}")
        if response.status_code == 200:
            txt.write(f"{hostname}\n")  # writing the file if active
            return True
        else:
            print("\n")
            return False
    except:
        return False

def getGoodWebsites():
    counter = 0 #we only want 500 websites

    with open("Goodwebsites.txt", mode="wt") as Goodwebsites:
        f = open("Uncheckedgoodwebsites.txt", "r") # Popular websites and websites from registered companies.
        for i in f.readlines():
            if Active(i.replace("\n", ""), Goodwebsites): #writing if active
                counter += 1
                print(f"Succesfully written url, count is {counter}\n")
            if(counter == 500):
                Goodwebsites.close()
                return
        Goodwebsites.close()

def getBadWebsites():
    counter = 0 #we only want 500 websites

    with open("Badwebsites.txt", mode="wt") as Badwebsites:
        for i in range(1, 1001, 20):  # List goes from 1 to 20
            page = requests.get(f"https://db.aa419.org/fakebankslist.php?start={i}")  # The url of all the bad websites from aa419
            soup = BeautifulSoup(page.text, 'html.parser')
            for link in soup.find_all(class_='tddomain'):
                a = link.find('a').text
                if a != "\nUrl ":  # This is the header
                    if Active(a, Badwebsites): #writing if active and removing the HTTP
                        counter += 1
                        print(f"Succesfully written url, count is {counter}\n")
                if counter == 500:
                    Badwebsites.close()
                    return
        Badwebsites.close()

if __name__ == '__main__':
    print("\nStarting good websites")
    getGoodWebsites()
    print("\nDone with good websites \n")
    print("Starting bad websites")
    getBadWebsites()
    print("\nDone with bad websites \n")

