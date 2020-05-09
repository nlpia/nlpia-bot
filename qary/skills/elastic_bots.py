""" Transformer based chatbot dialog engine for answering questions with ElasticSearch of Wikipedia"""

import logging
from qary.skills.qa_bots import Bot

log = logging.getLogger(__name__)


def test_reply():
    bot = Bot()
    answers = bot.reply('What is natural language processing?')
    print(answers)
