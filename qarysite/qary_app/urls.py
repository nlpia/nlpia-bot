# from django.contrib import admin
# from django.urls import path
from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


from qary_app import views


app_name = 'qary_app'


urlpatterns = [
    # path('', home_view),

    url(r'^$', views.PostListView.as_view(), name='list'),
    url(r'^(?P<pk>[-\w]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'answer/', views.reply, name='answer'),
    url(r'^(?P<pk>[-\w]+)/$', views.home_view, name='question'),

    # Rest_framework
    url('basic/', views.API_objects.as_view()),
    url('basic/<int:pk>/', views.API_objects_details.as_view()),




]
urlpatterns = format_suffix_patterns(urlpatterns)
