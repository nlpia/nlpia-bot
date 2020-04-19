from django.conf.urls import url
from swot import views
from django.urls import path

app_name = 'swot'

urlpatterns = [

    url(r'^$', views.PurposeListView.as_view(), name='list'),

    url(r'^(?P<pk>\d+)/$',
        views.PurposeDetailView.as_view(), name='detail'),

    url(r'^create/$', views.PurposeCreateView.as_view(), name='create'),

    url(r'^update/(?P<pk>\d+)/$',
        views.PurposeUpdateView.as_view(), name='update'),

]
