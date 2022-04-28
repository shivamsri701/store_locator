from celery import shared_task
from time import sleep
from django.core.mail import send_mail, EmailMessage
from . models import Store
import csv
import os

@shared_task
def send_mail_task(name, email):
    subject = 'Store list of all {0} stores'.format(name)
    body = 'Below is the file attached of {0} stores in USA'.format(name)
    to = email
    print(to)
    email = EmailMessage(subject, body, 'shivamsri7011@gmail.com',['shivamsri701@gmail.com'])
    email.content_subtype = 'html'

    stores = None
    if name == 'PizzaHut':
      stores = Store.objects.filter(name='Pizza Hut').values_list()
    elif name == 'Tacobell':
      stores = Store.objects.filter(name='Taco Bell').values_list()
    elif name == 'Starbucks':
      stores = Store.objects.filter(name='Starbucks').values_list()
    elif name == 'Verizon':
      stores = Store.objects.filter(name__icontains='Verizon').values_list()
    elif name == 'Burgerking':
      stores = Store.objects.filter(name='Burgerking').values_list()[:2000]
    print('Stores mila', len(stores))
    if stores is not None:
      with open('accounts/{0}.csv'.format(name), 'w') as file:
          writer = csv.writer(file)
          writer.writerows(stores)

      file = open('accounts/{0}.csv'.format(name), 'r')
      email.attach('{0}.csv'.format(name), file.read(), 'text/plain')
      email.send()
      os.remove('accounts/{0}.csv'.format(name))
      return None
