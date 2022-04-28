import requests
import json
import csv
from celery import shared_task
from django.core.mail import send_mail
from .models import Store


url = "https://use1-prod-bk.rbictg.com/graphql"

def get_all_zip_codes():
    with open('dataFiles/USZipCodes.csv', 'r') as file:
        reader = csv.reader(file)
        data = []
        header = next(reader)
        for row in reader:
            # print(row)
            data.append(row)
        return data



def get_stores_data(session, latitude, longitude):

    payload = [
        {
            "operationName": "GetRestaurants",
            "variables": {"input": {
                    "filter": "NEARBY",
                    "coordinates": {
                        "userLat": latitude,
                        "userLng": longitude,
                        "searchRadius": 32000
                    },
                    "first": 30,
                    "status": "OPEN"
                }},
            "query": """query GetRestaurants($input: RestaurantsInput) {
    restaurants(input: $input) {
        pageInfo {
        hasNextPage
        endCursor
        __typename
        }
        totalCount
        nodes {
        ...RestaurantNodeFragment
        __typename
        }
        __typename
    }
    }

    fragment RestaurantNodeFragment on RestaurantNode {
    _id
    storeId
    isAvailable
    posVendor
    chaseMerchantId
    curbsideHours {
        ...OperatingHoursFragment
        __typename
    }
    deliveryHours {
        ...OperatingHoursFragment
        __typename
    }
    diningRoomHours {
        ...OperatingHoursFragment
        __typename
    }
    distanceInMiles
    drinkStationType
    driveThruHours {
        ...OperatingHoursFragment
        __typename
    }
    driveThruLaneType
    email
    environment
    franchiseGroupId
    franchiseGroupName
    frontCounterClosed
    hasBreakfast
    hasBurgersForBreakfast
    hasCatering
    hasCurbside
    hasDelivery
    hasDineIn
    hasDriveThru
    hasMobileOrdering
    hasLateNightMenu
    hasParking
    hasPlayground
    hasTakeOut
    hasWifi
    hasLoyalty
    id
    isDarkKitchen
    isFavorite
    isHalal
    isRecent
    latitude
    longitude
    mobileOrderingStatus
    name
    number
    parkingType
    phoneNumber
    physicalAddress {
        address1
        address2
        city
        country
        postalCode
        stateProvince
        stateProvinceShort
        __typename
    }
    playgroundType
    pos {
        vendor
        __typename
    }
    posRestaurantId
    restaurantImage {
        asset {
        _id
        metadata {
            lqip
            palette {
            dominant {
                background
                foreground
                __typename
            }
            __typename
            }
            __typename
        }
        __typename
        }
        crop {
        top
        bottom
        left
        right
        __typename
        }
        hotspot {
        height
        width
        x
        y
        __typename
        }
        __typename
    }
    restaurantPosData {
        _id
        __typename
    }
    status
    vatNumber
    __typename
    }

    fragment OperatingHoursFragment on OperatingHours {
    friClose
    friOpen
    monClose
    monOpen
    satClose
    satOpen
    sunClose
    sunOpen
    thrClose
    thrOpen
    tueClose
    tueOpen
    wedClose
    wedOpen
    __typename
    }
    """
        }
    ]
    headers = {"Content-Type": "application/json"}

    response = session.request("POST", url, json=payload, headers=headers)

    print(response.text)

    pageData = json.loads(response.text)
    stores = pageData[0]['data']['restaurants']['nodes']
    print('Length of stores array: ',len(stores))
    if len(stores) != 0:
        data = []
        for store in stores:
            print('Name: ', 'Burgerking')
            print('Phone: ',store['phoneNumber'])
            print('Latitude: ', store['latitude'])
            print('Longitude: ', store['longitude'])
            print('Address', store['name'])
            print('City: ',store['physicalAddress']['city'])
            # print('',store['physicalAddress']['country'])
            print('Zipcode: ',store['physicalAddress']['postalCode'])
            print('State', store['physicalAddress']['stateProvince'])
            print('--------------------------------------')
            name = 'Burgerking'
            address = store['name']
            phoneNumber = store['phoneNumber']
            latitude = store['latitude']
            longitude = store['longitude']
            zip = store['physicalAddress']['postalCode']
            city = store['physicalAddress']['city']
            state = store['physicalAddress']['stateProvince']
            d = [name, address, city, state, zip, phoneNumber, latitude, longitude]
            data.append(d)
        return data
    else:
        return None

def store_to_file(data):
    print('Saving data to file')
    with open('burgerking.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print('Saved data to file')


@shared_task
def burgerkingScraper(to):
    print('Getting all zip codes, latitude, longitude')
    ziplist = get_all_zip_codes()
    session = requests.Session()
    storesList = []
    for zip in ziplist:
        try:
            print('Zip: ', zip[0])
            stores = get_stores_data(session, float(zip[1]), float(zip[2]))
            if stores is not None:
                storesList.extend(stores)
        except Exception as e:
            print('Error: ', e)

    print('Store List: ', storesList)
    # store_to_file(storesList)
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

    print('Saved data')
    send_mail('Scraping for Burgerking stores has completed',
     'This mail is to comfirm that the scraper has completed scraping the data and updating the database',
     'shivamsri7011@gmail.com',
     [to]
     )
    return storesList


# stores = burgerkingScraper()