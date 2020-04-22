from django.shortcuts import render
from django.views.generic import ListView, DetailView
from qary_app import models
from qary.clibot import CLIBot
# import re  # noqa


bot = CLIBot(bots=('glossary',))

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
    template_name = 'qary_app/first_app_detail.html'
