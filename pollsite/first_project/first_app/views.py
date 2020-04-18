from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . import models
from nlpia_bot.clibot import CLIBot
import re


bot = CLIBot()

get_request = None


def home_view(request):

    # function return Query.dict from GET
    global get_request
    get_request = request.GET

    return render(request, "question.html", )


def reply(request):

    # k = str(n[20:-4])
    bot_reply = bot.reply(get_request['n'])

    dict_1 = {'insert': bot_reply, 'Question': get_request['n']}

    return render(request, "answer.html", context=dict_1)


class PostListView(ListView):
    context_object_name = 'posts'
    model = models.Post


class PostDetailView(DetailView):
    context_object_name = 'post_detail'
    model = models.Post
    template_name = 'first_app/first_app_detail.html'
