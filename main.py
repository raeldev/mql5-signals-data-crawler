import requests
from bs4 import BeautifulSoup
import pymongo
import numpy
import time

print('\n \n ')
print('Scrapping ...')

# Crawler
url = 'https://www.mql5.com/en/signals/mt5/list/page'
headers = { 'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15" }

myclient = pymongo.MongoClient("mongodb://root:guest@localhost:27017/")
mydb = myclient["crawler"]
mycol = mydb["mql5signal"]
page = 1
position = 0
pageWithContent = True
delayOptions = [2,3,4]

while (pageWithContent):
    print('Adding page {}'.format(page))
    site = requests.get(url+str(page), headers=headers)
    soup = BeautifulSoup(site.content, 'html.parser')
    time.sleep(numpy.random.choice(delayOptions))

    signalTable = soup.find('div', {'class': 'signals-table'})
    signalTable.find('div', {'class': 'row header'}).decompose()
    hrefs = signalTable.findAll('a', {'class': 'signal-avatar'})
    
    links = list(map(lambda href : href.get('href'), hrefs))
    mqlIds = list(map(lambda href : str(href.get('href')).split('/')[5].split('?')[0], hrefs))
    signalNames = list(map(lambda href : str(href.get('title')).split(' by ')[0].replace('\'',''), hrefs))
    authors = list(map(lambda href : str(href.get('title')).split(' by ')[1], hrefs))
    prices = signalTable.findAll('span', {'class': 'price-value'})
    growties = signalTable.findAll('div', {'class':'col-growth blue'})
    subscribers = signalTable.findAll('div', {'class':'col-subscribers'})
    funds = signalTable.findAll('div', {'class':'col-facilities'})
    weeks = signalTable.findAll('div', {'class':'col-weeks'})
    experts = signalTable.findAll('div', {'class':'col-experts'})
    trades = signalTable.findAll('div', {'class':'col-trades'})
    winPercent = signalTable.findAll('div', {'class':'col-plus'})
    activiies = signalTable.findAll('div', {'class':'col-activiy'})
    profitFactors = signalTable.findAll('div', {'class':'col-pf'})
    #ep = signalTable.findAll('div', {'class':'col-ep'})
    drawdowns = signalTable.findAll('div', {'class':'col-drawdown'})
    #leveragies = signalTable.findAll('div', {'class':'col-leverage'})
    
    while (position < len(prices)):
        #2006 Signals at 24-05
        print('Adding signal {}'.format(signalNames[position]))
        
        signal = { 
            'link': links[position],
            'mqlId': mqlIds[position],
            'name': signalNames[position],
            'author': authors[position],
            'price':prices[position].get_text(),
            'growth':growties[position].get_text(),
            'subscribers':subscribers[position].get_text(),
            'funds':funds[position].get_text(),
            'weeks':weeks[position].get_text(),	
            'trades':trades[position].get_text(),	
            'winPercent':winPercent[position].get_text(),
            'profitFactor':profitFactors[position].get_text(),	
            'drawdown':drawdowns[position].get_text()
        }

        mycol.insert_one(signal)

        # SignalDetails
        #existentSignal = mycol.find({"link":str(links[position])})
        #if existentSignal:
        #     signalDetailRequest = requests.get(links[position])
        #     signalDetail = BeautifulSoup(signalDetailRequest.content, 'html.parser')
        #     time.sleep(numpy.random.choice(delayOptions))

        # if existentSignal:
        #     mycol.find_one_and_replace()
        # else:
        #     mycol.insert_one()
            
        position += 1

    pageWithContent = site.status_code != 404
    #pageWithContent = False
    page += 1
    position = 0

#print(signals[0])