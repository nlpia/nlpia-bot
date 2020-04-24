from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from . import models
from . models import Post, Chat
from nlpia_bot.clibot import CLIBot
from django.utils import timezone


bot = CLIBot()


def home_view(request):

    obj = Chat.objects.all().order_by('-create_date')

    dict_1 = {'c': obj}

    return render(request, "bot.html", context=dict_1)


def reply(request):
    my_question = request.POST.get('question_req')
    bot_reply = bot.reply(request.POST.get('question_req'))
    obj = Chat.objects.all().order_by('-create_date')

    dict_1 = {'insert': bot_reply, 'Question': my_question,
              'c': obj}

    if my_question and bot_reply:
        Chat.objects.create(question=my_question,
                            answer=bot_reply)

    return render(request, "bot.html", context=dict_1)


class PostListView(ListView):
    context_object_name = 'posts'
    model = models.Post


class PostDetailView(DetailView):
    context_object_name = 'post_detail'
    model = models.Post
    template_name = 'first_app/first_app_detail.html'
