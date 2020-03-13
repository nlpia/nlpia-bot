from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('<em>Secound app</em>')


def help(request):
    dic = {'insert': 'help page'}
    return render(request, 'app_two/help.html', context=dic)
