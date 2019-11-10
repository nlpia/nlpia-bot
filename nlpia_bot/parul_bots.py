""" Meet Robo: your friend by Parul Pandey """
import os
import random
import string  # to process standard python strings
import warnings
# import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlpia_bot.constants import DATA_DIR

import nltk  # FIXME: from nlpia_bot.spacy_language_model import nlp
from nltk.stem import WordNetLemmatizer

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
WIKI_TEXT_PATH = os.path.join(DATA_DIR, 'chatbot-depth3.txt')
REMOVE_PUNCT_TRANS_DICT = dict((ord(punct), None) for punct in string.punctuation)

warnings.filterwarnings('ignore')
nltk.download('popular', quiet=True)  # for downloading packages
nltk.lemmer = WordNetLemmatizer()


def lemmatize_normalize(text):
    tokens = nltk.word_tokenize(text.lower().translate(REMOVE_PUNCT_TRANS_DICT))
    return [nltk.lemmer.lemmatize(token) for token in tokens]


# Unless your installer has already done this you'll need to download the punkt and wordnet corpora from nltk
# nltk.download('punkt') # first-time use only
# nltk.download('wordnet') # first-time use only
tfidf_vectorizer = TfidfVectorizer(tokenizer=lemmatize_normalize, stop_words='english')


def load_wikipedia_text(path=WIKI_TEXT_PATH):
    # Reading in the corpus
    with open(path, 'r', encoding='utf8', errors='ignore') as fin:
        raw = fin.read()

    # TOkenisation
    lowered = raw.lower()
    sent_tokens = nltk.sent_tokenize(lowered)  # converts to list of sentences
    word_tokens = nltk.word_tokenize(lowered)  # converts to list of words
    return sent_tokens, word_tokens


WIKI_SENTENCES, WIKI_WORDS = load_wikipedia_text()
WIKI_TFIDF = tfidf_vectorizer.fit_transform(WIKI_SENTENCES)


def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


# Generating response
def response(user_response):
    robo_response = ''
    user_tfidf = tfidf_vectorizer.transform(user_response)

    vals = cosine_similarity(user_tfidf, WIKI_TFIDF)
    idx = vals.argsort()[0][-1]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-1]
    if(req_tfidf == 0):
        robo_response = robo_response + "I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response + WIKI_SENTENCES[idx]
        return robo_response


def main():
    flag = True
    print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")
    while flag:
        user_response = input()
        user_response = user_response.lower()
        if(user_response != 'bye'):
            if(user_response == 'thanks' or user_response == 'thank you'):
                flag = False
                print("ROBO: You are welcome..")
            else:
                if(greeting(user_response) is not None):
                    print("ROBO: " + greeting(user_response))
                else:
                    print("ROBO: ", end="")
                    print(response(user_response))
                    # sent_tokens.remove(user_response)
        else:
            flag = False
            print("ROBO: Bye! take care..")


class Bot:
    def reply(self, statement):
        """ Chatbot "main" function to respond to a user command or statement

        >>> respond('Hi')[0][1]
        Hello!
        >>> len(respond('Hey Mycroft!'))
        4
        """
        responses = []
        bot_statement = response(statement.lower())
        responses.append((1.0, bot_statement))

        return responses


if __name__ == '__main__':
    main()
