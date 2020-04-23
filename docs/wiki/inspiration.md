# Inspiration

A lot of the patterns and ideas were gleaned from other awesome prosocial chatbots and modular open source frameworks.

## Mental Health Coaches

- [WYSA](wysa.io) from London is free
    - https://www.techinasia.com/ai-chatbot-wysa-touchkin-penguin
    - open source (touchkin)?
    - ionic?
    - passive sensing of sleep patterns (accelerometers?)
    - guided meditation
    - exercise suggestions
    - free text dialog with buttons to suggest replies
    - based on open source touchkin/mindlogger ?
    - [list of alternative apps](https://github.com/akeshavan/mHealthLandscape/blob/0ea138267f13af1c8a0733296ebcfb9683485528/mHealth_iOS.csv)
- [Replika](replika.ai) from US is paywalled
    - personality profile test
    - pay to unlock "skills" training
- [Youper](youper.ai) 


## Open Source Frameworks

- [will](https://github.com/skoczen/will)
    - lang: python
    - web: zeromq
    - db: redis, couchbase, flat file, user-defined
    - integrations: hipchat, rocketchat, shell, slack
- [ai-chatbot-framework](https://github.com/alfredfrancis/ai-chatbot-framework/blob/master/app/intents/models.py)
    - lang: python
    - web: flask
    - orm: flask?
    - db: mongodb
    - nice general json syntax for specifying intent/goals for conversation manager (agent)
- [rasa](https://github.com/RasaHQ/rasa)
    - lang: python
    - web: sanic (async)
    - orm: sqlalchemy
    - db: sqlite
    - rich, complex, mature framework
- [botpress](https://github.com/botpress/botpress)
    - javascript (typescript)
    - meta-framework allowing your to write your own modules in javascript
- [Program-Y](https://github.com/keiffster/program-y/wiki)
    - python
    - web: flask (rest), sanic (async)
    - db: aiml flat files (XML)
    - integrations: facebook messenger, google search, kik, line, alexa, webchat, viber