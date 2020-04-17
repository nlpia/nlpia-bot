
""" Search and scrape wikipedia articles from a chosen category """
import os
# import json
from elasticsearch import Elasticsearch
import wikipediaapi
from slugify import slugify
from .. import constants

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


# def read_up_on(categories):


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
            log.info(f"Elasticsearch Document JSON created: {self.body}")
        except Exception as error:
            log.warning(f"Document JSON instance error: ", error)

    def insert(self):
        slug = slugify(self.body['title'])
        res = None
        try:
            res = client.index(index=slug, body=self.body)
        except Exception as e:
            log.error(f"Could not create a JSON entry for an article {slug}. error: {e}")
        return res


def search(text, index=''):
    """ Full text search within an ElasticSearch index (''=all indexes) for the indicated text """
    return client.search(index=index,
                         body={"query": {"match": {"text": text}}}
                         )


def test_search():
    res = search(text='text similarity')

    print()
    print('Relevant Articles')
    print('=================')
    for doc in res['hits']['hits']:
        print(doc['_source']['title'])
    print('=================')
    print()
    return res


if __name__ == '__main__':
    print(test_search())
