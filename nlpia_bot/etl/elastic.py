import os
import json
from elasticsearch import Elasticsearch
import wikipediaapi
from slugify import slugify
from nlpia_bot import constants

try:
    client = Elasticsearch()
except ConnectionRefusedError:
    print("Failed to launch Elstcisearch")


''' 
Search and scrape wikipedia articles from a chosen category

'''


def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


def search_insert_wiki(category):

    if type(category) is not list: category = [ category ]

    wiki_wiki = wikipediaapi.Wikipedia('en')
    
    for c in category:

        cat = wiki_wiki.page(f"Category:{c}")

        for key in cat.categorymembers.keys():
            page = wiki_wiki.page(key)

            if not "Category:" in page.title:
                doc = Document(page.title, page.text, page.fullurl, category=c)
                doc.insert()


# Save articles in separate .txt files

def save_articles(path=os.path.join(constants.DATA_DIR, "wikipedia"), category='Natural_language_processing'):

    os.makedirs(path, exist_ok=True)

    wiki_wiki = wikipediaapi.Wikipedia('en')

    cat = wiki_wiki.page(f"Category:{category}")

    for key, value in cat.categorymembers.items():
        page = wiki_wiki.page(key)
        slug = slugify(key)
        
        try:
        
            with open(f'{path}/{slug}.txt', 'w') as new_file:
                new_file.write(page.title)
                new_file.write('\n')
                new_file.write(page.fullurl)
                new_file.write('\n')
                new_file.write(page.text)
                
        except Exception as error:
            print(f"Error writing document {page.title}: ", error)



def index_dir(path=os.path.join(constants.DATA_DIR, "wikipedia")):

    paths = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                paths.append(os.path.join(r, file))
    
    return paths


class Document:

    def __init__(self, title, text, source, category):

        self.category = category
        self.title = title
        self.text = text
        self.source = source
        
        self.body = {"title": self.title,
                     "text": self.text,
                     "source":self.source}

    def insert(self):
        
        index = slugify(self.category)

        try:
            client.index(index=index, body=self.body)

        except Exception as error:
            print(f"Could not create a JSON entry for an article {self.source}")


# Example document search:

def search(text, index=''):
    return client.search(index=index, 
                         body={"query": 
                                 {"match": 
                                  {"text": text}
                                 }
                                }
    )


def test_search():
    res = search(text='how many seasons is in altered carbon series?')

    print('Relevant articles:')
    print('===================')
    for doc in res['hits']['hits']:
        print(doc['_source']['title'])


categories = ['Machine learning',
            'Marvel Comics',
            'Marvel Comics editors-in-chief',
            'American science fiction television series',
            'Science fiction television',
            'Natural language processing',
            'American comics writers', 
            ]
search_insert_wiki(categories)
# test_search()