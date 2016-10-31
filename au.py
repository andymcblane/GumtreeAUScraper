from BeautifulSoup import BeautifulSoup
import urllib2
import re
import requests
import sqlite3 as lite
import time

con = lite.connect('db.sqlite')

cur = con.cursor()
def doesNotExist(cur, number):
    try:
        cur.execute("SELECT * FROM Phone where number LIKE '" + number + "'")
    except:
        return True
    if len(cur.fetchall()) == 0:
        return True
    return False



def request(address):
    return urllib2.urlopen(address).read()


html = request("http://www.gumtree.com.au/s-iphone/iphone/k0c18597")

def notPromo(features):
    return features not in ['AD_GP_TOP_AD', 'AD_URGENT', 'PREMIUM_AD', ':seachTopAd']

soup = BeautifulSoup(html)

links = soup.findAll('a', attrs={'class': 'ad-listing__title-link'})
#get the id's of all search results
ids = re.match("/s-ad/.*/([0-9][0-9]*)\"", html)

for link in links:
    try:
        dataref = link['data-ref']
    except:
        pass
    ids = re.match("/s-ad/.*/([0-9][0-9]*)", link['href'])
    s = ids.groups()[0]
    headers = {
        'Host': 'ecg-api.gumtree.com.au',
        'Proxy-Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Firefox 21.2 (iPhone; iPhone OS 9.3.6; en_AU)',
        'Accept-Language': 'en-AU',
        #stolen from the iPhone app. This means we can make requests without a captcha.
        'Authorization': 'Basic YXVfaXBob25lX2FwcDplY2dhcGkhZ2xvYmFs',
    }
    if notPromo(dataref):
        r = requests.get("https://ecg-api.gumtree.com.au/api/ads/" + s, headers=headers)
        page = BeautifulSoup(r.text)
        features = ""
        try:
            features = page.find('feat:feature-active')['name']
        except:
            pass
        if notPromo(features):
            number = page.find('ad:phone').string
            title = page.find('ad:title').string
            price = page.find('ad:highest-price').string
            id = page.find('ad:user-id').string
            description = page.find('ad:description').string
            if doesNotExist(cur,str(number)) and number is not None and price is not None:

                print("Phone Number: \n   " + str(number))
                print("Title: \n   " + title)
                print("Price: \n   $" + price)
                print("Description: \n   " + description)
                k = title + ' on Gumtree http://www.gumtree.com.au/s-ad/' + s
                time.sleep(5)
                cur.execute("INSERT into Phone VALUES ('" + number + "')")
                con.commit()

