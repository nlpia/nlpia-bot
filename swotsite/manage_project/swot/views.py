from django.shortcuts import render
from . import models
from django.urls import reverse
from django.views.generic import (View,
                                  TemplateView, ListView,
                                  DetailView, UpdateView,
                                  CreateView, DeleteView)


# Create your views here.


class IndexView(TemplateView):
  template_name = 'index.html'


class PurposeListView(ListView):
  context_object_name = 'purposes'
  model = models.Purpose


class PurposeDetailView(DetailView):
  context_object_name = 'purpose_detail'
  model = models.Purpose
  template_name = 'swot/purpose_detail.html'


class PurposeCreateView(CreateView):
  fields = ('purpose',)
  model = models.Purpose


class PurposeUpdateView(CreateView):
  fields = ('purpose',)
  model = models.Purpose
