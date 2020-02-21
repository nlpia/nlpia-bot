import os
import json
from elasticsearch import Elasticsearch
import wikipediaapi
from slugify import slugify

client = Elasticsearch("http://localhost:9200")

''' 
Search and scrape wikipedia articles by category

'''

def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


cat = wiki_wiki.page("Category:Natural_language_processing")
print("Category members: Category:Natural_language_processing")
print_categorymembers(cat.categorymembers)

# Save the articles in separate .txt files

def save_articles(path = 'C:\PythonPrograms\Jupyter\elasticsearch_test\wikipedia_articles', wiki_dict = cat.categorymembers):
    for key, value in wiki_dict.items():
        page = .page(key)
        slug = slugify(key)
        
        with open(f'{path}\{slug}.txt', 'w') as new_file:
            new_file.write(page.title)
            new_file.write('\n')
            new_file.write(page.fullurl)
            new_file.write('\n')
            new_file.write(page.text)



def index_dir(path=os.path.expanduser('~')):

    paths = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.py' in file:
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
                "text": self.text
                "source": self.source,
            }
            print("Elasticsearch Document JSON:", self.json)
            
        except Exception as error:
            print("Document JSON instance error: ", error)

    def insert_to_elastic(self.body):

        slug = slugify(self.body["title"])

        try:
            res = client.index(index = slug, body = self.body)

        except Exception as error:
        print(f"Could not create a JSON entry for an article {slug}"



# Example document search

def query_document(index="chatbot",id=1):

    try:
        res = client.search(index = "", body = {"query": {"match": {"text": "text similarity"}}})
        
        print('Relevant articles:')
        for doc in res['hits']['hits']:
            print(doc['_source']['title'])
    
    except Exception as error:
        print ("client.index() ERROR:", error, "n")

