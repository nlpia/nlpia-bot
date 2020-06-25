# Qary Vision 2020-06-25

Monthly sprint planning for the month of July.
Recurring: Fourth Wednesday each month, day before SD PUG, so first official sprint planning was for July, held June  25.

## Achievements this month:
    * First qary-based app (TABot)
    * Everyone's story or Equisite corpse (django app not a bot?)
    * NLP & BERT improvement to core `qary` app
    * Elastic search flat index, retrained BERT working on fine-tuning on SQuAD
    * Django Celery for webapps like TABot
    * issues/features for new contributors
    * CodeCoverage integrated into gitlab-ci
    * Docs are working! Tests are passing! (on master... most of the time)


Directions for the future:

## qary:
    * +1 **ConvoManager** Improve the conversation manager (Finite State Machines), conversation planner and context manager (Alex followup feature)
        * Transitioning from flat-files to database data storage
    * +5 DuckBot Replacement: **Benchmarking** and improving accuracy of QA-bot (retraining the model, etc.)
    * +1 SocratesBot and add empathy and intent detection
    * Voice bot features/integrations
    * Improving accuracy of other bots (faq, etc.)
    * Add ability of user to give feedback (+1)
    * FormBot or an IntakeBot
    * +1 WritingTutorBot (expressing ideas is hard)
    * QuizBot or FlashcardBot
    * GameBot
    * +5 **MoodBot** CheerBot -- mental health coaching (focus on do no harm)
        * Sentiment analysis
    * +3 FAQ bot improved using U.S.E or BERT embedding


## django-qary:
    * Adding options for interfacing with external services (REST API)
    * Making it easier to add content to django-qary (indexing scripts)
    * Making Django-qary into an app (accounts, associating documents with accounts)
    * Increasing reply speed of django-qary


## Contributions:
- Improve the platform
- Improve qa-bot
- Create new bots or improve existing ones
- Build on top of qary / integrate qary into your app (i.e. reddit integration, web-apps)
- Improve elastic-qary

# Long term ideas:

Fake bot with scripted chats, hitting return at each line, typing then out with random pauses per letter, more for spaces,less for letters. Poisson.

B = Bot
Y = You

B: Good morning boss, what can I do for you?
--
- Y: I'm not sure. The news has got me down the past few days.
- Y: I'm feeling a little depressed
--
- B: last week Rattle and Hum cheered you up. I'll start playing  some energizing music while you work. You can tell me if it gets annoying.
- B: Yea, you aren't typing with the same enthusiasm you normally do. What's on your mind?
Y: I keep going over in my mind that conversation I had with my brother years ago.
B: Go on.
Y: And then that makes me think of how I'm not as successful as he is. And that keeps spiraling on and on into thoughts of dying alone.
B: wow that's a lot of stuff going on. Perhaps we can focus on one thing to improve today a little.
B: Is there something in particular this week or last night that triggered those thoughts?
Y: Perhaps it was those slides I have to put together for class.
How is that coming? Have you started on it?
Yea, I have a draft, but it's crap. It makea me look like a fool. It's full of mistakes. People will hate it.
Would you like me to help you try to improve it, or worried you rather we deal with some of the cognitive biases that are clouding your mind right now?
--
- Clouds
OK the first thing we need to do is give labels to your cognitive distortions so your brain can get better at sorting through your worries and anxieties better when they come to again today.
Do you remember some of the names you came up with for your favorite cognitive biases?
catastrophizing, mind reading, future proofing, over engineering
Good! Some of those might apply here. What about dichotomous thinking, do you remember that one?

- work on it
So what is the theme you’re working on?

- Y: can you give me some questions to ask someone on a first date? 10th date?
- B: what was your favorite thing about yesterday?
- B: if you were going on a trip next weekend where would you go? Who or what would you take with you?
- what is the meaning of life
- B: what is the most profound idea you heard about so far this year?
- B/Y: heard any good music lately?
- Y: anything in the news I should know about?
- B: someone made a change to that Wikipedia article on chocolate liquer, I did some bc research, want me to show you?
- B: there's a good TIL on Reddit you might like, but first you have to mail that card to your father
- B: Mohamed shared something interesting on Slack yesterday.
- B: Ted asked a really tough data science question on the TABot yesterday.
- B: Maria shared a TED talk on nonprofits she can thinks you would like
- Y: What's Brussels the capital of?
- Y: where do Brussels sprouts come from?
- Y: how is popcorn made?
- Y: give me a cool optics experiment I can show my neices
- Y: what's the best practice for running a long running machine learning model in a web app?
- Y: where did SirajRaval get the idea for that?
- Y: I really liked Leo's blog post. Let him know and make sure to tweet about it several times this week.
- Y: has anyone mentioned the OB Cafe on Reddit this week? People's market?
- y: what uses more carbon: peanut butter or chocolate covered cashews?
- y: what's the right temperature and time to bake sourdough
- Y: I'm bored.
- Y: I'm depressed.
- Y: who first came up with the concept of wisdom of the crowds.
- Y: what's this about a resource based economy I keep hearing about ?
- Y: what causes fake news?
- Y: how do animal herds and dolphin pods cooperate so we'll, but humans don't?
- B: you have a meeting with Raj at 10. Have you read his email yet?
- B: what's a good source of calcium and vitamin D?
- B: what do you have in the fridge?... I can suggest a recipe that uses bread and tomatoes  avacadoes

