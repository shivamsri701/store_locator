from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('homepage', views.homepage, name='homepage'),
    path('pizzahut', views.pizzahut, name='pizzahut'),
    path('sendmailpizzahut', views.sendmailpizzahut, name='sendmailpizzahut'),
    path('tacobell', views.tacobell, name='tacobell'),
    path('sendmailtacobell', views.sendmailtacobell, name='sendmailtacobell'),
    path('starbucks', views.starbucks, name='starbucks'),
    path('sendmailstarbucks', views.sendmailstarbucks, name='sendmailstarbucks'),
    path('verizon', views.verizon, name='verizon'),
    path('sendmailverizon', views.sendmailverizon, name='sendmailverizon'),
    path('burgerking', views.burgerking, name='burgerking'),
    path('sendmailburgerking', views.sendmailburgerking, name='sendmailburgerking'),
    path('save_pizzahutstores_to_db', views.save_pizzahutstores_to_db, name='save_pizzahutstores_to_db')
]
