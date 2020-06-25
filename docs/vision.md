# Qary

Achievements this month:
    * First qary-based app (TABot)
    * Everyone's story or Equisite corpse (django app not a bot?)
    * NLP & BERT improvement to core `qary` app
    * Elastic search flat index, retrained BERT working on fine-tuning on SQuAD
    * Django Celery for webapps like TABot
    * issues/features for new contributors
    * CodeCoverage integrated into gitlab-ci
    * Docs are working! Tests are passing! (on master... most of the time)


Directions for the future:

qary:
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


django-qary:
    * Adding options for interfacing with external services (REST API)
    * Making it easier to add content to django-qary (indexing scripts)
    * Making Django-qary into an app (accounts, associating documents with accounts)
    * Increasing reply speed of django-qary


Contributions:
- Improve the platform
- Improve qa-bot
- Create new bots or improve existing ones
- Build on top of qary / integrate qary into your app (i.e. reddit integration, web-apps)
- Improve elastic-qary
