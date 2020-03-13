from django.shortcuts import render
from django.http import HttpResponse
from nlpia_bot.clibot import CLIBot


bot = CLIBot()


def index(request, user_statement='Hello world'):

    bot_reply = bot.reply(user_statement)

    my_dict = {'insert_me': bot_reply}

    return render(request, 'first_app/index.html', context=my_dict)


def reply(request, user_statement):

    bot_reply = bot.reply(user_statement)

    my_dict = {'insert_me': bot_reply,
               'user_statement': user_statement}

    return render(request, 'first_app/index.html', context=my_dict)
