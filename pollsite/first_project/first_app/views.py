from django.shortcuts import render
from nlpia_bot.clibot import CLIBot


bot = CLIBot()

n = ''


def home_view(request):
    request.GET
    global n
    n = str(request.GET)

    return render(request, "home.html")


def reply(request):

    bot_reply = bot.reply(n)

    dict_1 = {'insert': bot_reply}

    return render(request, "index.html", context=dict_1)
