"""bot URL patterns (endpoints or routes) """
from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.webchat, name='webchat'),
]
