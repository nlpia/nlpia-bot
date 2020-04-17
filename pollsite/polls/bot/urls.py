from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from bot import views


app_name = 'bot'


urlpatterns = [
    path('', home_view),
]
