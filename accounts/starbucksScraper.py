import requests
from bs4 import BeautifulSoup
import csv
import json
from celery import shared_task
from .models import Store
from django.core.mail import send_mail

def get_page(url, session=None):
    print('Retrieving URL: ', url)
    page = session.get(url, headers = {"Content-Type": "application/json; charset=utf-8", 'X-Requested-With':'XMLHttpRequest'})
    try:
        data = json.loads(page.text)
    except Exception as e:
        pass
    try:
        return data['stores']
    except Exception as e:
        return None

def get_starbucks_data(stores, zip):

    try:
        data = []
        for store in stores:
            phone = store['phoneNumber']
            if phone is None:
                phone = ''
            latitude = store['coordinates']['latitude']
            longitude = store['coordinates']['longitude']
            name = store['brandName']
            city = store['address']['city']
            zip = zip
            state = store['address']['countrySubdivisionCode']
            address = ''
            for s in store['addressLines']:
                address += s
            d = [name, address, city, state, zip, phone, latitude, longitude ]
            print(d)
            data.append(d)
        return data
    except Exception as e:
        return None


def get_all_zip_codes():
    with open('dataFiles/USZipCodes.csv', 'r') as file:
        reader = csv.reader(file)
        data = []
        header = next(reader)
        for row in reader:
            # print(row)
            data.append(row[0])
        return data

def get_all_zip_store_data(ziplist):
    finalData = []
    session = requests.Session()
    for zip in ziplist:
        print('Percent done: {0}'.format(int(zip)/int(ziplist[-1]) * 100))
        url = 'https://www.starbucks.com/bff/locations?place='
        # zip = '60010'
        stores = get_page(url+zip, session)
        if stores is None:
            continue
        data = get_starbucks_data(stores, zip)
        if data is not None:
            finalData.extend(data)

    return finalData

def store_to_file(data):
    print('Saving data to file')
    with open('starbucks.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print('Saved data to file')



@shared_task
def starbucksscraper(to):
    print('Scraper for Starbucks stores has started')
    ziplist = get_all_zip_codes()
    storesList = get_all_zip_store_data(ziplist)
    print('Collected all stores data')
    rows = storesList
    for i in range(0, len(rows)):
        name = rows[i][0]
        address = rows[i][1]
        city=rows[i][2]
        state=rows[i][3]
        zipcode=rows[i][4]
        try:
            phone=rows[i][5]
        except IndexError:
            phone = ''
        try:
            latitude=rows[i][6]
        except IndexError:
            latitude = ''
        try:
            longitude=rows[i][7]
        except IndexError:
            longitude = ''
        store = Store(name=name, address=address,city=city, state=state, zipcode=zipcode, phone=phone, latitude=latitude, longitude=longitude)
        store.save()

    print('Data saved to database')

    send_mail('Scraping for Starbucks stores has completed',
     'This mail is to comfirm that the scraper has completed scraping the data and updating the databses',
     'shivamsri7011@gmail.com',
     [to],
     fail_silently=True
     )

    






    # store_to_file(storesList)


# scraper()



