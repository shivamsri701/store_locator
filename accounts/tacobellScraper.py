import csv
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from .models import Store
from django.core.mail import send_mail

# import mysql.connector

# from pizzahut import store_to_file


def get_page(url, session=None):
    print('Retrieving URL: ', url)
    page = session.get(url, headers = {"Content-Type": "application/json; charset=utf-8"})
    # print(page.text)
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup)
    return soup


def get_states(soup):
    print('Geting all states from the page')
    states = []
    subpage = soup.find('div', class_='Directory-content')
    
    states = subpage.findAll('li', class_='Directory-listItem')
    print('Total number of states: ', len(states))

    data = []
    for state in states:
        name = state.find('span', class_='Directory-listLinkText').text
        link = state.find('a', class_='Directory-listLink')['href']
        d = (name, link)
        data.append(d)
    # print(data)
    return data




def get_cities(soup, name):
    print('Getting all cities for state: ', name)
    citiesData = []
    cities = soup.findAll('li', class_='Directory-listItem')
    for city in cities:
        name = city.find('span', class_='Directory-listLinkText').text
        link = city.find('a', class_='Directory-listLink')['href']
        dataCount = city.find('a', class_='Directory-listLink')['data-count']
        d = (name, link, dataCount)
        citiesData.append(d)

    # print(citiesData)
    return citiesData

def get_stores(soup, sname, cname):
    print('Geting all store for state: ', sname, ' and city: ', cname)
    allStores = []
    storesList = soup.findAll('li', class_='Directory-listTeaser')
    for storeitem in storesList:
        # name = storeitem.find('span', class_='LocationName--directory-geo').text
        name = 'Taco Bell'
        address = storeitem.find('span', class_='c-address-street-1').text
        city = cname
        state = sname
        zipcode = storeitem.find('span', class_='c-address-postal-code').text
        phone = storeitem.find('div', class_='Phone-display Phone-display--withLink')
        if phone is not None:
            phone = phone.text
        # print(zipcode)

        s = (name, address, city, state, zipcode, phone)
        print(s)
        allStores.append(s)

    return allStores

def get_store(soup, sname, cname):
    name = 'Taco Bell'
    address = soup.find('span', class_='c-address-street-1')
    if address is not None:
        address = address.text
    city = cname
    state = sname
    zipcode = soup.find('span', class_='c-address-postal-code').text
    phone = soup.find('div', class_='Phone-display Phone-display--withLink')
    if phone is not None:
        phone = phone.text
    s = (name, address, city, state, zipcode, phone)
    return s
    

def store_to_file(data):
    print('Saving data to file')
    with open('tacobell.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print('Saved data to file')



@shared_task
def tacobellScraper(to):
    print('Scraper for Tacobell stores has started')
    url = 'https://locations.tacobell.com/'
    finalData = []
    session = requests.Session()
    soup = get_page(url, session) 
    statesData = get_states(soup)
    # counter = 0
    for name, link in statesData:
        soup = get_page(url + '/' + link, session)
        cities = get_cities(soup, name)

        for cname, clink, dataCount in cities:
            soup = get_page(url + '/' + clink, session)
            # counter += 1
            if dataCount == '(1)':
                store = get_store(soup, name, cname)
                finalData.append(store)
            else:
                stores = get_stores(soup, name, cname)
                finalData.extend(stores)

            # if counter == 20:
            #     break


    # print(finalData)
    # store_to_file(finalData)
    rows = finalData
    print('Collected all stores data')
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
    print('Data saved to database')

    send_mail('Scraping for Starbucks stores has completed',
     'This mail is to comfirm that the scraper has completed scraping the data and updating the databses',
     'shivamsri7011@gmail.com',
     [to]
     )








# tacobellScraper()