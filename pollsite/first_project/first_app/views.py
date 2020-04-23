from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from . import models
from . models import Post, Chat
from nlpia_bot.clibot import CLIBot


bot = CLIBot()

get_request = None


def home_view(request):

    # function return Query.dict from GET
    global get_request
    get_request = request.GET

    return render(request, "bot.html", )


def reply(request):
    my_question = request.POST.get('question_req')
    bot_reply = bot.reply(request.POST.get('question_req'))

    dict_1 = {'insert': bot_reply, 'Question': my_question}

    if my_question and bot_reply:
        Chat.objects.create(question=my_question, answer=bot_reply)

    return render(request, "bot.html", context=dict_1)


class PostListView(ListView):
    context_object_name = 'posts'
    model = models.Post


class PostDetailView(DetailView):
    context_object_name = 'post_detail'
    model = models.Post
    template_name = 'first_app/first_app_detail.html'


class ChatHistory(ListView):

    context_object_name = 'chat'
    model = models.Chat
    template_name = 'chat.html'
