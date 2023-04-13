from bs4 import BeautifulSoup
import urllib3
import certifi
import pandas as pd
import re
import random
import time
from time import sleep
import boto3
from db.update_table import create_lot, delete_lot, upload_file

url = 'https://www.gcsurplus.ca/mn-eng.cfm?snc=wfsav&sc=ach-shop&jstp=sly&hpsr=&hpcs=2300&vndsld=0'
gcsurplus = 'https://www.gcsurplus.ca/'

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

lot_urls = set()
urls_failed = 0


df = pd.DataFrame(columns = ['lot', 'closing_date', 'year', 'make', 'model', 'mileage', 'url'])

# random generator for sleep between pages
sleepNmbr = random.randrange(5, 10)


def make_soup(url):
    global urls_failed
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    try:
        r = http.request("GET", url, timeout=20.0, retries=False)
        return BeautifulSoup(r.data, 'html.parser')

    except urllib3.exceptions.HTTPError:
        urls_failed += 1
        print('Connection failed for ' + url)
        return 0

    except Exception as err:
        urls_failed += 1
        exception_type = type(err).__name__
        print('Other failure type for' + url + '\nfollowing error occurred: ' + exception_type)
        return 0


def soup_process1(url):
    global lot_urls
    soup = make_soup(url)
    results = soup.find('tbody')
    
    for tr in results.find_all('tr'):
        link = tr.find('div', {'class': 'novisit'}).find('a')['href']
        lot_urls.add(gcsurplus + link)
 
    sleep(5)    
    return soup


def soup_process2(url):
    global df
    soup = make_soup(url)

    if soup != 0:
        try:
            lot_info_details1 = soup.find('div', {'id':'bidPanelId'})
            table1_1 = lot_info_details1.find('dl', {'class': 'table-display fontSize90'})
            lot = table1_1.find("dt",text='\r\n\t\t\t\tSale / Lot :\r\n\t\t\t').findNext("dd").string.strip().replace(' ', '')
            closing_date = table1_1.find('span', {'id':'closingDateId'}).text.strip().split('\xa0@')[0]

            lot_info_details2 = soup.find('div', {'id':'lot-info','class': 'lot-info'})
            table2_1 = lot_info_details2.find('dl', {'class': 'table-display'})
            table2_2 = table2_1.find('dl', {'class': 'table-display'})

            year = table2_2.find("dt",text="Year:").findNext("dd").text
            make = table2_2.find("dt",text="Make:").findNext("dd").text
            model = table2_2.find("dt",text="Model:").findNext("dd").text
            odometer = table2_2.find("dt",text="Odometer:").findNext("dd").string
            odometer = re.sub("\D", "", odometer)

            # Upload image
            imgurl = soup.find('span', {'id':'img1'}).find('img')['src']

            if 'gcsurplus' not in imgurl:
                imgurl = gcsurplus + imgurl

            upload_file(lot, imgurl)

            df = df.append({'lot': lot, 'closing_date': pd.to_datetime(closing_date), 'year': year,
                            'make': make, 'model': model, 'mileage': odometer, 'url': url}, ignore_index=True)

            time.sleep(sleepNmbr)

        except Exception as err:
            exception_type = type(err).__name__
            print('\nfailed to parse: ' + url + '\nfollowing error occurred: ' + exception_type)
            soup = 0
            return soup


def main(url):
    print('Scraping lot urls')
    soup = soup_process1(url)

    while url:
        soup = soup_process1(url)
        nextlink = soup.find('li', {'class': 'next'}).find('a')['href']

        url = False
        if (nextlink):
            url = (gcsurplus+nextlink)



if __name__ == '__main__':
    # Parse lot listings to extract all links
    main(url)
    print('{} lot urls extracted\n'.format(len(lot_urls)))

    # Parse individual car lots to extract lot information
    print('Scraping individual lot listings')
    for url in lot_urls:
        soup_process2(url)
    print('{} individual lots parsed\n{} urls failed\n'
          .format(df.shape[0], urls_failed))

    # Update gcsurplus table in DynamoDB with new lots
    print('Updating DynamoDB')
    try:
        for i, row in df.iterrows():
            create_lot(dynamodb, row[0], row[1].isoformat(), row[2], row[3], row[4], row[5], row[6])
            sleep(5)
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
    print('DynamoDB updated\n')

    # Remove old lots with date older than today
    print('Removing old lots')
    lots_removed = delete_lot(dynamodb)
    print('{} lots removed'.format(lots_removed))


