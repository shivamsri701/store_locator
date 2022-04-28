# from audioop import add
from celery import shared_task
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from django.core.mail import send_mail
from .models import Store


PATH = '/usr/local/bin/chromedriver'

def get_cities_list(driver, state):
    url = 'https://www.verizon.com/stores/state/' + state + '/'
    driver.get(url)
    cities = driver.find_elements(By.CLASS_NAME, 'cityList')
    citiesList = []
    print('\n\n\n\nCities list: ')
    for city in cities:
        cityname = city.find_element(By.TAG_NAME, 'a')
        citiesList.append(cityname.text)
    return citiesList


def get_stores_list(driver, state, city):
    url = 'https://www.verizon.com/stores/city/' + state + '/' + city + '/'
    driver.get(url)
    stores = driver.find_elements(By.CLASS_NAME, 'store-details')
    finalData = []
    for store in stores:
        try:
            name = store.find_element(By.CLASS_NAME, 'store-search-title')
            name = name.find_element(By.TAG_NAME, 'a').text + ' Verizon'
            address = store.find_element(By.XPATH, '//*[@id="content"]/main/div[3]/div[2]/div[1]/div/div/div/div/div/div[3]/div[1]').text
            address = address.replace('\n', ' ')
            phone = store.find_element(By.XPATH, '//*[@id="content"]/main/div[3]/div[2]/div[1]/div/div/div/div/div/div[4]/p[1]/a').text
            statename = link_to_name(state)
            cityname = link_to_name(city)
            zip = address[-5:]

            data = [name, address, phone, cityname, statename, zip]

            finalData.append(data)
            print('Final Data:', finalData)
        except Exception as e:
            continue

    return finalData


def add_zip(storesList, ziplist):
    finalData = []
    for store in storesList:
        zip = store[5]
        for z in ziplist:
            if int(zip) == int(z[0]):
                store.append(z[1])
                store.append(z[2])
                break
        finalData.append(store)

    print('Final data: ', finalData)
    return finalData

                
def get_all_zip_codes():
    with open('dataFiles/USZipCodes.csv', 'r') as file:
        reader = csv.reader(file)
        data = []
        header = next(reader)
        for row in reader:
            data.append(row)
        return data


def get_states_list(driver):
    states = driver.find_elements(By.CLASS_NAME, 'stateLink')
    statesList = []
    for state in states:
        stateLink = state.find_element(By.TAG_NAME, 'a')
        statesList.append(stateLink.text)

    return statesList


def name_to_link(dataList):
    final_list = []
    for name in dataList:
        link = '-'.join(name.split()).lower()
        final_list.append(link)

    return final_list

# def store_to_file(data):
#     print('Saving data to file')
#     with open('verizon.csv', 'w') as file:
#         writer = csv.writer(file)
#         writer.writerows(data)
#     print('Saved data to file')

def link_to_name(link):
    return ' '.join(link.split('-')).capitalize()


@shared_task
def verizonScraper(to):
    driver = webdriver.Chrome('chromedriver')
    driver.maximize_window()
    url =  'https://www.verizon.com/stores/state/state/'

    driver.get(url)
    driver.implicitly_wait(20)
    driver.set_page_load_timeout(30)
    down_arrow = driver.find_element(By.CLASS_NAME, 'dropDownContainer')
    down_arrow.click()
    try:
        single_state = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="stateListDropDown"]/li[1]/a'))
        )
        statesList = get_states_list(driver)
        print(statesList)

        statesLink = name_to_link(statesList)

        print(statesLink)
        finalData = []
        counter = 0
        for state in statesLink:
            cities = get_cities_list(driver, state)
            counter += 1
            # if counter == 9:
            #     break
            print(cities)
            citiesLink = name_to_link(cities)
            for city in citiesLink:
                stores = get_stores_list(driver, state, city)
                print('Stores collected')
                print(stores)
                finalData.extend(stores)

        
        print(finalData)
        ziplist = get_all_zip_codes()
        finalData = add_zip(finalData, ziplist)


        # store_to_file(finalData)
        rows = finalData
        for i in range(0, len(rows)):
            name = rows[i][0]
            address = rows[i][1]
            city=rows[i][3]
            state=rows[i][4]
            zipcode=rows[i][5]
            try:
                phone=rows[i][2]
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

        print('Saved data')
        send_mail('Scraping for Verizon stores has completed',
     'This mail is to comfirm that the scraper has completed scraping the data and updating the database',
     'shivamsri7011@gmail.com',
     [to]
     )

    except Exception as e:
        print(e)
        driver.quit()

    finally:
        driver.quit()