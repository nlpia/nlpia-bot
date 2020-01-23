|Build Status| |Coverage| |GitHub release| |PyPI version| |License|

nlpia_bot
=========

Use `NLP in
Action <https://www.manning.com/books/natural-language-processing-in-action>`__
to build a virtual assistant that actually assists! Most bots manipulate
you to make money for their corporate masters. Your bot can help protect
you and amplify your abilities and prosocial instincts.

This hybrid chatbot combines 4 techniques explained in `NLP in
Action <https://www.manning.com/books/natural-language-processing-in-action>`__:

::

   1. search: [chatterbot](https://github.com/gunthercox/ChatterBot), [will](https://github.com/skoczen/will)
   2. pattern matching and response templates: Alexa, [AIML](https://github.com/keiffster/program-y)
   3. generative deep learning: [robot-bernie](https://github.com/nlpia/robot-bernie), [movie-bot](https://github.com/totalgood/nlpia/blob/master/src/nlpia/book/examples/ch10_movie_dialog_chatbot.py)
   4. grounding: [snips](https://github.com/snipsco/snips-nlu)

The presentations for San Diego Python User Group are in
`docs/ </docs/2019-08-22--San%20Diego%20Python%20User%20Group%20--%20How%20to%20Build%20a%20Chatbot.odp>`__

Install
-------

You’ll want to install and use the conda package manager within
Anaconda3, especially if your development environment is not a open
standard operating system like Linux.

.. code:: bash

   git clone git@github.com:nlpia/nlpia-bot
   cd nlpia-bot
   conda env create -n nlpia -f environment.yml  # or environment-windoze.yml
   conda activate nlpia
   pip install --editable .

Usage
-----

.. code:: bash

   $ bot --help
   usage: bot [-h] [--version] [--name STR] [-p] [-b STR] [-v] [-vv]
              [words [words ...]]

   Command line bot application, e.g. bot how do you work?

   positional arguments:
     words                Words to pass to bot as an utterance or conversational
                          statement requiring a bot reply or action.

   optional arguments:
     -h, --help           show this help message and exit
     --version            show program's version number and exit
     --name STR           IRC nick or CLI command name for the bot
     -p, --persist        Don't exit. Retain language model in memory and
                          maintain dialog until user says 'exit', 'quit' or 'bye'
                          (this is the default behavior if you do not provide a statement)
     -b STR, --bots STR   comma-separated list of bot personalities to load
                          default: pattern,parul,search_fuzzy,time,eliza
     -v, --verbose        set loglevel to INFO
     -vv, --very-verbose  set loglevel to DEBUG

Examples
--------

You can run bot just like any other command line app, giving it your
statement/query as an argument.

.. code:: bash

   $ bot hello
   # 2019-11-21 12:42:13,620 WARNING:nlpia.constants:107:            <module> Starting logger in nlpia.constants...
   # 100%|█████████████████████████████████████████████████████████████████████████████████████████████| 64350/64350 [00:00<00:00, 540679.58it/s]
   BOT: Hello

And if you want quicker turnaround on your bot you can just run it in
peristent mode (without any positional arguments for your statement or
words).

Travis’s probabilistic reply selector is working nicely to chose a reply
from multiple sources (default settings):

-  ``pattern_bots.py``: regex patterns and greeting templates
-  ``fuzzy_search_bots.py``: movie dialog fuzzy matching
-  ``parul_bots.py``: Wikipedia searches using conventional TFIDF like a
   search engine
-  ``eliza_bots.py``: A python port of the ELIZA therapist bot
-  ``time_bots.py``: A time and productivity tracker that parses your
   git logs and bash history

.. code:: bash

   $ bot
   (nlpia) hobs@Hobsons-MacBook-Air:~/code/chatbot/nlpia-bot$ bot
   # 2019-11-21 12:59:05,854 WARNING:nlpia.constants:107:            <module> Starting logger in nlpia.constants...
   # 100%|█████████████████████████████████████████████████████████████████████████████████████████████| 64350/64350 [00:00<00:00, 495935.48it/s]
   YOU: Hi
   BOT: hey there. tired of breathing?
   YOU: Hello
   BOT: How do you do. Please state your problem.
   YOU: What is an ELIZA chatbot?
   BOT: joey never told you we went out, did he?
   YOU: ^[[A
   BOT: I am sorry! I dont understand you
   YOU: What is an ELIZA chatbot?
   BOT: Does that question interest you ?
   YOU: What is a chatbot?
   BOT: hello barbie is an internet-connected version of the doll that uses a chatbot provided by the company toytalk, which previously used the chatbot for a range of smartphone-based characters for children.
   YOU: Hello
   BOT: hello.
   YOU: Hello
   BOT: How do you do. Please state your problem.
   YOU: bye
   $

Work in Progress
----------------

-  Travis (@travis-harper): markhov chain reply selection and other data
   science enhancements
-  Nima (@hulkgeek): question answering bot based on his state of the
   art question classifier
-  Xavier (@spirovanni): employment counselor for workforce.org and the
   city of San Diego
-  Hobson (@hobson): infrastructure (CI, webapp) and framework features
   (nltk->spacy, USE vectors)
-  Erturgrul: Turkish wikipedia QA bot (parul bot)
-  You: What big chatbot idea would you like to make a reality?

Ideas
-----

Please submit your feature ideas `github
issues <https://github.com/nlpia/nlpia-bot/issues/>`__. Here are a few
ideas to get you started.

1.  movie dialog in django database to hold the statement->response
    pairs

    1. graph schema compatible with MxGraph (draw.io) and other js
       libraries for editing graphs/flow charts.
    2. ubuntu dialog corpus in db
    3. mindfulness faq corpus in db
    4. famous quotes as responses to the statement “tell me something
       inspiring”
    5. jokes for “tell me a joke”
    6. data science faq
    7. nlpia faq
    8. psychology/self-help faq

2.  html django template so there is a web interface to the app rather
    than just the command line command ``bot``
3.  use Django Rest Framework to create a basic API that returns json
    containing a reply to any request sent to the local host url, like
    ``http://localhost:8000/api?statement='Hello world'`` might return
    {‘reply’: ‘Hello human!’}
4.  have the command line app use the REST API from #3 rather than the
    slow reloading of the csv file every time you talk to the bot
5.  use database full text search to find appropriate statements in the
    database that we have a response for
6.  use semantic search instead of text similarity (full text search or
    fuzzywyzzy text matches)

    1. add embedding vectors (300D document vectors from spacy) to each
       statement and response in the db
    2. create a semantic index of the document vectors using ``annoy``
       so “approximate nearest neighbors” (semantic matches) can be
       found quickly
    3. load the annoy index of the document vectors every time the
       server is started and use it to find the best reply in the
       database.
    4. use universal sentence encodings instead of docvecs from spacy.

7.  create a UX for dialog graph creation/design:

    1. install `mxgraph <https://github.com/totalgood/mxgraph>`__ in the
       django app
    2. create a basic page based on this mxgraph example so the user can
       build and save dialog to the db as a graph:
       `tutorial <https://jgraph.github.io/mxgraph/docs/tutorial.html#1>`__,
       `example
       app <https://jgraph.github.io/mxgraph/javascript/examples/grapheditor/www/index.html>`__
    3. convert the dialog graph into a set of records/rows in the
       nlpia-bot db so it acts

8.  tag different dialog graphs in the db so the user can turn them
    on/off for their bot

    1. allow the user to prioritize some dialogs/models over others
    2. allow the user to create their own weighting function to
       prioritize individual statements produced by the api

9.  train a character-based generative model

    1. decoder half of autoencoder to generate text based on docvecs
       from spacy
    2. decoder part of autoencoder to generate text based on universal
       sentence encodings
    3. train model to generate reply embeddings (doc vecs and/or use
       vecs) using statement embeddings (dialog engine encoder-decoder
       using docvecs or use vecs for the encoder half

10. add a therapy/mindfulness-coach feature to respond with mindfulness
    ideas to some queries/statements
11. add the “translate ‘this text’ to spanish” feature

    1. train character-based LSTM models on english-spanish,
       english-french, english-german, english<->whatever
    2. add module for this to the django app/api

12. AIML engine fallback

Inspiration
-----------

A lot of the patterns and ideas were gleaned from other awesome
prosocial chatbots and modular open source frameworks.

Mental Health Coaches
~~~~~~~~~~~~~~~~~~~~~

-  `WYSA <wysa.io>`__ from London is free

   -  https://www.techinasia.com/ai-chatbot-wysa-touchkin-penguin
   -  open source (touchkin)?
   -  ionic?
   -  passive sensing of sleep patterns (accelerometers?)
   -  guided meditation
   -  exercise suggestions
   -  free text dialog with buttons to suggest replies
   -  based on open source touchkin/mindlogger ?
   -  `list of alternative
      apps <https://github.com/akeshavan/mHealthLandscape/blob/0ea138267f13af1c8a0733296ebcfb9683485528/mHealth_iOS.csv>`__

-  `Replika <replika.ai>`__ from US is paywalled

   -  personality profile test
   -  pay to unlock “skills” training

-  `Youper <youper.ai>`__ (thank you Maria and
   `tangibleai.com <tangibleai.com>`__)

Open Source Frameworks
~~~~~~~~~~~~~~~~~~~~~~

-  `will <https://github.com/skoczen/will>`__

   -  lang: python
   -  web: zeromq
   -  db: redis, couchbase, flat file, user-defined
   -  integrations: hipchat, rocketchat, shell, slack

-  `ai-chatbot-framework <https://github.com/alfredfrancis/ai-chatbot-framework/blob/master/app/intents/models.py>`__

   -  lang: python
   -  web: flask
   -  orm: flask?
   -  db: mongodb
   -  nice general json syntax for specifying intent/goals for
      conversation manager (agent)

-  `rasa <https://github.com/RasaHQ/rasa>`__

   -  lang: python
   -  web: sanic (async)
   -  orm: sqlalchemy
   -  db: sqlite
   -  rich, complex, mature framework

-  `botpress <https://github.com/botpress/botpress>`__

   -  javascript (typescript)
   -  meta-framework allowing your to write your own modules in
      javascript

-  `Program-Y <https://github.com/keiffster/program-y/wiki>`__

   -  python
   -  web: flask (rest), sanic (async)
   -  db: aiml flat files (XML)
   -  integrations: facebook messenger, google search, kik, line, alexa,
      webchat, viber

.. |Build Status| image:: https://api.travis-ci.com/nlpia/nlpia-bot.svg?branch=master
   :target: https://travis-ci.com/nlpia/nlpia-bot
.. |Coverage| image:: https://codecov.io/gh/nlpia/nlpia-bot/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/nlpia/nlpia-bot
.. |GitHub release| image:: https://img.shields.io/github/release/nlpia/nlpia-bot.svg
   :target: https://github.com/nlpia/nlpia-bot/releases/latest
.. |PyPI version| image:: https://img.shields.io/pypi/pyversions/nlpia-bot.svg
   :target: https://pypi.org/project/nlpia-bot/
.. |License| image:: https://img.shields.io/pypi/l/nlpia-bot.svg
   :target: https://pypi.python.org/pypi/nlpia-bot/
