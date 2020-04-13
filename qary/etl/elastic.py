""" Search and scrape wikipedia articles from a chosen category """
import os
from elasticsearch import Elasticsearch 
from bs4 import BeautifulSoup
import wikipediaapi 
from slugify import slugify
from qary.etl.wikiparse import get_references, parse_article
from qary import constants

try:
    client = Elasticsearch("localhost:9200")
except ConnectionRefusedError:
    print("Failed to launch Elsticisearch")


log = constants.logging.getLogger(__name__)

mapping = {
    "properties": {
        
            "text": {
                "type": "nested",
                "properties":{
                    "section_num": {"type":"integer"},
                    "section_title": {"type":"text"},
                    "section_content": {"type":"text"}
                }
            },
        
            "references": {
                "type": "nested",
                "properties":{
                    "section_num": {"type":"integer"},
                    "section_title": {"type":"text"},
                    "section_content": {"type":"text"}
                }
            },
        
            "title": {
                "type": "text"
            },
        
            "source": {
                "type": "text"
            },
        
            "page_id": {
                "type": "long"
            },
            
        }
    }

class Document:
    
    def __init__(self):
        self.title = ''
        self.page_id = None
        self.source = ''
        self.text = ''
        
    def __if_exists(self, page_id, index=""):
        '''
        Check if the article already exists in the database
        with a goal to avoid duplication
        '''
        
        return client.search(index=index, 
                             body={"query": 
                                   {"match": 
                                    {"page_id": page_id}
                                   }})['hits']['total']['value']
        
    def insert(self, title, page_id, url, text, references, index):
        ''' Add a new document to the index'''
        
        self.title=title
        self.page_id=page_id
        self.source=url
        self.text=text
        self.references = references
        self.body = {'title': self.title,
            'page_id': self.page_id,
            'source':self.source,
            'text': self.text,
            'references':self.references}
        
        if self.__if_exists(page_id) == 0:
        
            try:
                client.index(index=index, body=self.body)
                log.info(f'Successfully added document {self.title} to index {index}.')
            except Exception as error:
                log.error(f"Error writing document {page_id}: {error}")
                
        else:
            log.info(f"Article {self.title} is already in the database")



def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


def search_insert_wiki(category, mapping):
    
    if type(category) is not list: category = [ category ]

    wiki_wiki = wikipediaapi.Wikipedia('en')
    
    for c in category:
        
        try:
                    
            '''Create and empty index with predefined data structure'''
            client.indices.create(index=slugify(c), body={"mappings":mapping})
            log.info(f'New index {slugify(c)} has been created')
            
            '''Access the list of wikipedia articles in category c'''
            cat = wiki_wiki.page(f"Category:{c}")
            
            ''' Parse and add articles in the category to database'''
            for key in cat.categorymembers.keys():
                page = wiki_wiki.page(key)

                if not "Category:" in page.title:

                    text = parse_article(page)
                    content, references = get_references(text)
                    doc = Document()
                    doc.insert(page.title, page.pageid, page.fullurl, content, references, index=slugify(c))


        except Exception as error:
            log.error(f"The following exception occured while trying to create index '{slugify(c)}': ", error)


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

def get_indices():
    return client.indices.get_alias("*")

def search(index = '', text="coronavirus"):  

    # client = Elasticsearch("elasticsearch:9200")
    client = Elasticsearch("localhost:9200")

    body = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": {
                        'query': text,
                        "boost":3
                    }}},
                    {
                        "nested": {
                            "path": "text",
                            "query": {
                                "bool": {
                                    "should": [
                                        {"term": { "text.section_num": 0 }},
                                        { "match": { "text.section_content":  text }}
                                    ]
                                }
                            },
                            "inner_hits":{
                                "highlight": {
                                    "fields": {"text.section_content": {"number_of_fragments" : 1, 'fragment_size':200, 'order': "score"}}
                                }
                            }
                        }
                    }
                    
                ]
            }
        }
    }


    """ Full text search within an ElasticSearch index (''=all indexes) for the indicated text """
    return client.search(index=index,
                         body=body)

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
    log.info(f'{index} has been successfully deleted from database')

def get_highlights(statement):
    query = search(text=statement)
    results = []

    for doc in query['hits']['hits']:

        for highlight in doc['inner_hits']['text']['hits']['hits']:

            try:
                snippet = ' '.join(highlight['highlight']['text.section_content']),
                snippet_with_html = BeautifulSoup(snippet[0], features="lxml")
                mytuple = (doc['_source']['title'],
                            doc['_score'],
                            doc['_source']['source'],
                            snippet_with_html.get_text(),
                            highlight['_source']['section_num'],
                            highlight['_source']['section_title'],
                            highlight['_score'],
                            highlight['_source']['section_content'])

                results.append(mytuple)

            except:  # noqa
                pass

    return results

    
def test_highlights(statement):
    res = get_highlights(statement)
    print('Relevant articles from your ElasicSearch library:')
    print('===================')
    for i in res:
        print(i)

def test_index(category):
    search_insert_wiki(category, mapping=mapping)


if __name__=="__main__":

    # test_index('American science fiction television series')
    test_highlights("altered carbon")

    # To add new categories to elasticsearch, run the following :
    # categories = ['Marvel Comics',
    #             'Machine learning',
    #             'Marvel Comics editors-in-chief',
    #             'American science fiction television series',
    #             'Science fiction television',
    #             'Natural language processing',
    #             'American comics writers', 
    #             'Presidents of the United States',
    #             'Coronaviridae',
    #             'Pandemics'
    #             ]
    #
    # search_insert_wiki(categories)


