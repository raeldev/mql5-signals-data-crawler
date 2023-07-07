import requests
from bs4 import BeautifulSoup
import pymongo
import numpy
import time

def main():
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

        signalTable = soup.find('div', class_= 'signals-table')
        signalTable.find('div', class_= 'row header').decompose()
        hrefs = signalTable.findAll('a', class_= 'signal-avatar')
        
        links = list(map(lambda a : str(a['href']), hrefs))
        mqlIds = list(map(lambda a : str(a['href']).split('/')[5].split('?')[0], hrefs))
        signalNames = list(map(lambda a : str(a['title']).split(' by ')[0].replace('\'',''), hrefs))
        authors = list(map(lambda a : str(a['title']).split(' by ')[1], hrefs))
        prices = signalTable.findAll('span', class_= 'price-value')
        growths = signalTable.findAll('div', class_='col-growth')
        subscribers = signalTable.findAll('div', class_='col-subscribers')
        funds = signalTable.findAll('div', class_='col-facilities')
        weeks = signalTable.findAll('div', class_='col-weeks')
        experts = signalTable.findAll('div', class_='col-experts')
        trades = signalTable.findAll('div', class_='col-trades')
        winPercent = signalTable.findAll('div', class_='col-plus')
        activities = signalTable.findAll('div', class_='col-activity')
        profitFactors = signalTable.findAll('div', class_='col-pf')
        ep = signalTable.findAll('div', class_='col-ep')
        drawdowns = signalTable.findAll('div', class_='col-drawdown')
        leveragies = signalTable.findAll('div', class_='col-leverage')
        
        while (position < len(prices)):
            #2006 Signals at 24-05
            print('Adding signal {}'.format(signalNames[position]))
            
            signal = { 
                'link': links[position],
                'mqlId': mqlIds[position],
                'name': signalNames[position],
                'author': authors[position],
                'price':float(prices[position].get_text().removesuffix('USD').replace('K','000')),
                'growth':growths[position].get_text(),
                'subscribers':int(subscribers[position].get_text()),
                'funds':float(funds[position].get_text().removesuffix('USD').replace('K','000')),
                'weeks':int(weeks[position].get_text()),	
                'experts':float(experts[position].get_text().removesuffix('%'))/100,	
                'trades':int(trades[position].get_text().replace(' ','')),
                'winPercent':float(winPercent[position].get_text().removesuffix('%'))/100,
                'activities':activities[position].get_text(),
                'profitFactor': float(profitFactors[position].get_text()),
                'ep':ep[position].get_text(),	
                'drawdown':float(drawdowns[position].get_text().removesuffix('%'))/100,
                'leveragies':leveragies[position].get_text(),
            }

            redirectPrefix = '?source=Site+Signals+MT5+Tile#!tab='

            #SignalDetails
            signalDetailRequest = requests.get(links[position])
            signalDetail = BeautifulSoup(signalDetailRequest.content, 'html.parser')
            time.sleep(numpy.random.choice(delayOptions))
            
            # Account Page
            signalDetail = signalDetail.find('div', id = 'returnChart')
            developments = signalDetail.select('div.row > div.cell[id^="returnCell"]')
            developments.pop(0) #removes table header
            signal['growth'] = list(map(lambda development : formatGrowth(development), developments))
            
            # Statistics Page
            signalDetailRequest = requests.get(links[position]+redirectPrefix+'stats')
            signalDetail = BeautifulSoup(signalDetailRequest.content, 'html.parser')
            time.sleep(numpy.random.choice(delayOptions))
            signalDetail = signalDetail.find('div', class_ = 's-data-columns')
            statisticsLabels = signalDetail.findAll('div', class_ = 's-data-columns__label')
            statisticsValues = signalDetail.findAll('div', class_ = 's-data-columns__value')
            signal['statistics'] = mapStastitcs(statisticsLabels, statisticsValues)

            # Review Page
            signalDetailRequest = requests.get(links[position]+redirectPrefix+'reviews')
            signalDetail = BeautifulSoup(signalDetailRequest.content, 'html.parser')
            time.sleep(numpy.random.choice(delayOptions))
            signalDetail = signalDetail.select('div.rating > div')
            rating = signalDetail[0]['class']
            if (len(rating) > 0): 
                rating = rating[0].removeprefix('v')
                rating = float(rating)/10
            else:
                rating = ''
            signal['rating'] = rating

            mycol.replace_one({"link":str(links[position])}, signal, upsert=True)
            position += 1

        # forced stop for testing
        #pageWithContent = False
        pageWithContent = site.status_code != 404
        page += 1
        position = 0

    #print(signals[0])

def formatGrowth(growth):
    growthText = str(growth.get('title'))
    splitedText = growthText.split(' ')

    if (len(splitedText) > 0):
        period = splitedText[len(splitedText) - 2].removesuffix(':')
        result = splitedText[len(splitedText) - 1]
        return { 'period': period, 'result': result }

def mapStastitcs(labels, values):
    stats = {}
    pos = 0
    while (pos < len(labels)):
        label = labels[pos].get_text().strip()
        value = values[pos].get_text().replace('\r','').replace('\n','').strip().removesuffix(':')
        stats[label] = value
        pos += 1

    return stats

main()