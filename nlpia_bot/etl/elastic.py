import os
import json
from elasticsearch import Elasticsearch 
import wikipediaapi 
from slugify import slugify
from nlpia_bot import constants
from nlpia_bot.etl import wikisearch as ws
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
            print(page.title)

    print("Done")


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

    def delete(self, index):
        client.indices.delete(index=index, ignore=[400,404])
        print(f'{index} has been successfully deleted from database')



# Example document search:

def get_indices():
    return client.indices.get_alias("*")

def search(text, index=''):
    return client.search(index=index, 
                         body={"query": 
                                 {"match": 
                                  {"text": text}
                                 }
                                }
    )

def search_title(text, index=''):
    return client.search(index=index, 
                         body={"query": 
                                 {"match": 
                                  {"title": text}
                                 }
                                }
    )

def search_url(text, index=''):
    return client.search(index=index, 
                         body={"query": 
                                 {"match": 
                                  {"source": text}
                                 }
                                }
    )

def delete_index(index):
    client.indices.delete(index=index, ignore=[400,404])
    print(f'{index} has been successfully deleted from database')

def test_search(statement):
    res = search(text=statement)
    res_wiki = ws.summary(statement)
    print('Relevant articles from your ElasicSearch library:')
    print('===================')
    for doc in res['hits']['hits']:
        print(doc['_source']['title'])
        print(doc['_source']['source'])
        print("----------------------")

    print('Summary found on Wikipedia')
    print("======================")
    print(res_wiki)
    print('Full text of the article')
    print("=======================")
    print(ws.content(statement))


if __name__=="__main__":

    statement = "who is Stan Lee"


    def test_indices():
        res = get_indices()
        ind_list = []
        for r in res:
            ind_list.append(r)
        return ind_list

    test_search(statement)

    # Add new categories to elasticsearch:
    # categories = ['Machine learning',
    #             'Marvel Comics',
    #             'Marvel Comics editors-in-chief',
    #             'American science fiction television series',
    #             'Science fiction television',
    #             'Natural language processing',
    #             'American comics writers', 
    #             'Presidents of the United States'
    #             ]
    # search_insert_wiki(categories)
    
