# Crazy Ideas

Please submit your feature ideas [GitLab issues](https://gitlab.com/tangibleai/qary/issues/). Here are a few ideas to get you started.

1. movie dialog in django database to hold the statement->response pairs
    1. graph schema compatible with MxGraph (draw.io) and other js libraries for editing graphs/flow   charts.
    2. ubuntu dialog corpus in db
    3. mindfulness faq corpus in db
    4. famous quotes as responses to the statement "tell me something inspiring"
    5. jokes for "tell me a joke"
    6. data science faq
    7. nlpia faq
    8. psychology/self-help faq
2. html django template so there is a web interface to the app rather than just the command line command `bot`
3. use Django Rest Framework to create a basic API that returns json containing a reply to any request sent to the local host url, like `http://localhost:8000/api?statement='Hello world'` might return {'reply': 'Hello human!'}
4. have the command line app use the REST API from #3 rather than the slow reloading of the csv file every time you talk to the bot
5. use database full text search to find appropriate statements in the database that we have a response for
6. use semantic search instead of text similarity (full text search or fuzzywyzzy text matches)
    1. add embedding vectors (300D document vectors from spacy) to each statement and response in the db
    2. create a semantic index of the document vectors using `annoy` so "approximate nearest neighbors" (semantic matches) can be found quickly
    3. load the annoy index of the document vectors every time the server is started and use it to find the best reply in the database.
    4. use universal sentence encodings instead of docvecs from spacy.
7. create a UX for dialog graph creation/design:
    1. install [mxgraph](https://github.com/totalgood/mxgraph) in the django app
    2. create a basic page based on this mxgraph example so the user can build and save dialog to the db as a graph: [tutorial](https://jgraph.github.io/mxgraph/docs/tutorial.html#1), [example app](https://jgraph.github.io/mxgraph/javascript/examples/grapheditor/www/index.html)
    3. convert the dialog graph into a set of records/rows in the qary db so it acts
8. tag different dialog graphs in the db so the user can turn them on/off for their bot
    1. allow the user to prioritize some dialogs/models over others
    2. allow the user to create their own weighting function to prioritize individual statements produced by the api
9. train a character-based generative model
    1. decoder half of autoencoder to generate text based on docvecs from spacy
    2. decoder part of autoencoder to generate text based on universal sentence encodings
    3. train model to generate reply embeddings (doc vecs and/or use vecs) using statement embeddings (dialog engine encoder-decoder using docvecs or use vecs for the encoder half
10. add a therapy/mindfulness-coach feature to respond with mindfulness ideas to some queries/statements
11. add the "translate 'this text' to spanish" feature
    1. train character-based LSTM models on english-spanish, english-french, english-german, english<->whatever
    2. add module for this to the django app/api
12. AIML engine fallback