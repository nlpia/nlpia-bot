from django.shortcuts import render
from nlpia_bot.clibot import CLIBot


bot = CLIBot()

# Create your views here.
n = ''


def home_view(request):
    request.GET
    # print(request.POST)
    global n
    n = str(request.GET)

    # logic of view will be implemented here
    return render(request, "home.html")


def reply(request):

    bot_reply = bot.reply(n)

    dict_1 = {'insert': bot_reply}

    return render(request, "index.html", context=dict_1)
