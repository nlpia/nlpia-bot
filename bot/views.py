# from django.shortcuts import render
from django.http import HttpResponse


def webchat(request, username='human'):
    return HttpResponse(f"Hi {username}! What's on your mind?")
