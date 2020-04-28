from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from . import models
from . models import Post, Chat
# from qary.clibot import CLIBot
from qary_app import models
# Import all skills
from qary.skills import (parul_bots, basebots, glossary_bots,
                         pattern_bots, search_fuzzy_bots, eliza_bots)


parul_bot = parul_bots.Bot()
basebot = basebots.HiBot()
glossary_bot = glossary_bots.Bot()
pattern_bot = pattern_bots.Bot()
search_fuzzy_bot = search_fuzzy_bots.Bot()
eliza_bot = eliza_bots.Bot()


def team(request):
    return render(request, "team.html")


def nlpia(request):
    return render(request, "nlpia.html")


def home_view(request):

    obj = Chat.objects.all().order_by('-create_date')

    dict_1 = {'c': obj}

    return render(request, "bot.html", context=dict_1)


def reply(request):

    my_question = request.POST.get('question_req')
    # radio button condition
    if request.POST.get('parul_bot'):
        bot_reply = parul_bot.reply(request.POST.get('question_req'))

    elif request.POST.get('basebot'):
        bot_reply = basebot.reply(request.POST.get('question_req'))

    elif request.POST.get('glossary_bot'):
        bot_reply = glossary_bot.reply(request.POST.get('question_req'))

    elif request.POST.get('pattern_bot'):
        bot_reply = pattern_bot.reply(request.POST.get('question_req'))

    elif request.POST.get('search_fuzzy_bot'):
        bot_reply = search_fuzzy_bot.reply(request.POST.get('question_req'))

    elif request.POST.get('eliza_bot'):
        bot_reply = eliza_bot.reply(request.POST.get('question_req'))

    else:
        bot_reply = parul_bot.reply(request.POST.get('question_req'))

    obj = Chat.objects.all().order_by('-create_date')
    print(bot_reply)

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
    template_name = 'qary_app/qary_app_detail.html'
