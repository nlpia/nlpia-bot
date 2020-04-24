from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from . import models
from . models import Post, Chat
from qary.clibot import CLIBot
from qary_app import models
# Import all skills
from qary.skills import parul_bots, basebots, glossary_bots
# , elastic_bots, eliza_bots, faq_bots, juan_bots, nima_bots, pattern_bots,)


parul_bot = parul_bots.Bot()
basebot = basebots.HiBot()
glossary_bot = glossary_bots.Bot()
# make branch of master / git checkout master -b radio_button
# git push -u orgin radio_button
# git commit
# git push

# bot = CLIBot(bots=('glossary',))


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
    print(my_question)
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
