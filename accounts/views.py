from email import message
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth import get_user_model

from django.contrib import messages
from .models import Store
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
import os
import csv
from . mailing import send_mail_task
from .starbucksScraper import starbucksscraper
from .pizzahutScraper import pizzahutScraper
from .tacobellScraper import tacobellScraper


User = get_user_model()

# Create your views here.

def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method != 'POST':
        redirect(request, '/')

    username = request.POST['username']
    firstname = request.POST['fname']
    email = request.POST['email']
    lastname = request.POST['lname']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    if password1 == password2:
        if User.objects.filter(username=username).exists():
            print('Username already exists')
            messages.info(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            print('Email already exists')
            messages.info(request, 'Email already exists')
        else:

            try:
                user = User.objects.create(username=username, email=email, first_name=firstname, last_name=lastname)
                user.set_password(password1)
                user.save()
                print('User created successfully')
                messages.info(request, 'User created successfully')
            except Exception as e:
                print('Error occured: ', e)
                messages.info(request, 'Error occured: {}'.format(e))
    else:
        print('Password did not match')
        messages.info(request, 'Password did not match')

    return redirect('/')


def login(request):
    if request.method != 'POST':
        return redirect('/')

    email = request.POST['email']
    password = request.POST['password']

    user = auth.authenticate(email=email, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect('homepage')
    else:
        messages.info(request, 'Wrong credentials')
        return redirect('/')



def logout(request):
    auth.logout(request)
    return redirect('/')

def homepage(request):
    if request.user.is_authenticated:
        return render(request, 'homepage.html')
    else:
        return redirect('/')


def pizzahut(request):
    if request.user.is_staff:
        pizzahutScraper.delay(request.user.email)
        messages.info(request, "Scraper for Pizzahut stores has started. Confirmation mail will be sent once it's done")
        return redirect('homepage')
    else:
        storesList = Store.objects.filter(name='Pizza Hut')
        return render(request, 'pizzahut.html', {"storesList" : storesList})

def tacobell(request):
    if request.user.is_staff:
        tacobellScraper.delay(request.user.email)
        messages.info(request, "Scraper for Tacobell stores has started. Confirmation mail will be sent once it's done")
        return redirect('homepage')
    else:
        storesList = Store.objects.filter(name='Taco Bell')
        return render(request, 'tacobell.html', {"storesList" : storesList})


def starbucks(request):
    if request.user.is_staff:
        starbucksscraper.delay(request.user.email)
        messages.info(request, "Scraper for Starbucks stores has started. Confirmation mail will be sent once it's done")
        return redirect('homepage')
    else:
        storesList = Store.objects.filter(name='Starbucks')
        return render(request, 'starbucks.html', {"storesList" : storesList})


# def save_pizzahutstores_to_db(request):
#     file = open("accounts/tacobellData.csv")
#     csvreader = csv.reader(file)
#     header = next(csvreader)
#     # print(header)
#     rows = []
#     for row in csvreader:
#         rows.append(row)

#     for i in range(0, len(rows)):
#         name = rows[i][0]
#         address = rows[i][1]
#         city=rows[i][2]
#         state=rows[i][3]
#         zipcode=rows[i][4]
#         try:
#             phone=rows[i][5]
#         except IndexError:
#             phone = ''
#         try:
#             latitude=rows[i][6]
#         except IndexError:
#             latitude = ''
#         try:
#             longitude=rows[i][7]
#         except IndexError:
#             longitude = ''
#         store = Store(name=name, address=address,city=city, state=state, zipcode=zipcode, phone=phone, latitude=latitude, longitude=longitude)
#         store.save()


def sendmailpizzahut(request):
    if request.user.is_authenticated:
        send_mail_task.delay('PizzaHut', request.user.email)
        messages.info(request, 'Email sent to your registered email address')
        return redirect('pizzahut')

    else:
        return redirect('/')

def sendmailtacobell(request):
    if request.user.is_authenticated:
        send_mail_task.delay('Tacobell', request.user.email)
        messages.info(request, 'Email sent to your registered email address')
        return redirect('tacobell')
    else:
        return redirect('/')

def sendmailstarbucks(request):
    if request.user.is_authenticated:
        send_mail_task.delay('Starbucks', request.user.email)
        messages.info(request, 'Email sent to your registered email address')
        return redirect('starbucks')
    else:
        return redirect('/')

