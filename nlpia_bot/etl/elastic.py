
""" Search and scrape wikipedia articles from a chosen category """
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


log = constants.logging.getLogger(__name__)


def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


def search_insert_wiki(categories):
    print(categories)

    if type(categories) is not list: categories = [ categories ]

    wiki_wiki = wikipediaapi.Wikipedia('en')
    
    for c in categories:
        print(c)

        cat = wiki_wiki.page(f"Category:{c}")

        for key in cat.categorymembers.keys():
            page = wiki_wiki.page(key)

            if not "Category:" in page.title:
                
                doc = Document(page.title, page.text, page.fullurl, page.pageid, category = c)
                doc.insert()

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
            log.error(f"Error writing document {page.title}: {error}")


def index_dir(path=os.path.join(constants.DATA_DIR, "wikipedia")):

    paths = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                paths.append(os.path.join(r, file))

    return paths


class Document:
    
    def __init__(self, title, text, source, page_id, category):

        self.category = category
        self.title = title
        self.text = text
        self.source = source
        self.page_id = page_id
        
        self.body = {"title": self.title,
                     "text": self.text,
                     "source":self.source,
                     "page_id": self.page_id}

    def insert(self):
        
        slug = slugify(self.category)

        res = client.search(index="", 
                         body={"query": 
                                 {"match": 
                                  {"page_id": self.page_id}}})
        
        if res['hits']['hits'] == []:

            try:
                print(self.page_id, self.title, self.source)
                
                client.index(index=slug, body=self.body)

            except Exception as error:
                print(f"Could not create a JSON entry for an article {self.source}")
                
        else:
            print(f"Article {self.source} is already in the database")


# Example document search:

def get_indices():
    return client.indices.get_alias("*")

def search(text, index=''):
    """ Full text search within an ElasticSearch index (''=all indexes) for the indicated text """
    return client.search(index=index,
                         body={"query": {"match": {"text": text}}}
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

def search_field(text, field="text", index=''):
    return client.search(index=index, 
                         body={"query": 
                                 {"match": {field: text}}
                                })

def boosted_search(text, index='', boost_factor=3):
    return client.search(index=index, body=\
                        {
                        "query": {
                            "bool": {
                            "should": [
                                {
                                "match": {
                                    "title": {
                                    "query": text,
                                    "boost": boost_factor
                                    }
                                }
                                },
                                {
                                "match": { 
                                    "text": text
                                }
                                }
                            ]
                            }
                        }
                        })

def delete_index(index):
    client.indices.delete(index=index, ignore=[400,404])
    print(f'{index} has been successfully deleted from database')

def test_search(statement):
    res = boosted_search(text=statement)
    # res_wiki = ws.summary(statement)
    print('Relevant articles from your ElasicSearch library:')
    print('===================')
    for doc in res['hits']['hits']:
        print(doc['_source']['title'])
        print(doc['_source']['source'])
        print("----------------------")


if __name__=="__main__":

    # statement = "who is Stan Lee"


    # def test_indices():
    #     res = get_indices()
    #     ind_list = []
    #     for r in res:
    #         ind_list.append(r)
    #     return ind_list

    # test_indices()
    test_search("stan lee")

    # Add new categories to elasticsearch:
    # categories = ['Marvel Comics',
    #             'Machine learning',
    #             'Marvel Comics editors-in-chief',
    #             'American science fiction television series',
    #             'Science fiction television',
    #             'Natural language processing',
    #             'American comics writers', 
    #             'Presidents of the United States'
    #             ]
    
    # search_insert_wiki(categories)
    
