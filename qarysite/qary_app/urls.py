# from django.contrib import admin
# from django.urls import path
from django.conf.urls import url  # , include

from qary_app import views


app_name = 'qary_app'


urlpatterns = [
    # path('', home_view),
    url(r'^$', views.PostListView.as_view(), name='list'),
    url(r'^(?P<pk>[-\w]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'answer/', views.reply, name='answer'),
    url(r'question/', views.home_view, name='question'),

]
