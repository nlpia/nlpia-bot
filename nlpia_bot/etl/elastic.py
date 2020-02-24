import os
import json
from elasticsearch import Elasticsearch
import wikipediaapi
from slugify import slugify

client = Elasticsearch()


''' 
Search and scrape wikipedia articles from a chosen category

'''

wiki_wiki = wikipediaapi.Wikipedia('en')


def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


cat = wiki_wiki.page("Category:Natural_language_processing")

# Save articles in separate .txt files

def save_articles(path = 'data', wiki_dict = cat.categorymembers):
    for key, value in wiki_dict.items():
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



def index_dir(path=os.path.expanduser('~')):

    paths = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                paths.append(os.path.join(r, file))
    
    return paths


class Document:
    
    def __init__(self, title, text, source):
        self.title = title
        self.text = text
        self.source = source
        
        self.body = {}
        
        try:
            
            self.body = {
                "title": self.title,
                "text": self.text,
                "source": self.source
            }
            print("Elasticsearch Document JSON created:", self.body)
            
        except Exception as error:
            print("Document JSON instance error: ", error)

    def insert(self):
        
        slug = slugify(self.body['title'])

        try:
            res = client.index(index = slug, body = self.body)

        except Exception as error:
            print(f"Could not create a JSON entry for an article {slug}")


# Example document search:

def search_elastic(search_term, index = ''):
    return client.search(index = index, 
                         body = {"query": 
                                 {"match": 
                                  {"text": search_term}
                                 }
                                }
    )

res = search_elastic(search_term = 'text similarity')

print('Relevant articles:')
print('===================')
for doc in res['hits']['hits']:
    print(doc['_source']['title'])
