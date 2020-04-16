from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from first_app import views


app_name = 'bot'


urlpatterns = [
    path('', home_view),
]
