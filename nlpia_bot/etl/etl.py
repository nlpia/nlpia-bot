import os
from elasticsearch import Elasticsearch

client = Elasticsearch("http://localhost:9200")

def index_dir(path=os.path.expanduser('~')):

    paths = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.py' in file:
                paths.append(os.path.join(r, file))
    
    return paths, len(paths)


class Document:
    
    def __init__(self, index, id, source):
        self.index = index
        self.id = id
        self.source = source
        
        self.json = {}
        
        try:
            
            self.json = {
                "_index": self.index,
                "_id": self.id,
                "doc_type":"_doc",
                "_source": self.source,
            }
            print("Elasticsearch Document JSON:", self.json)
            
        except Exception as error:
            print("Document JSON instance error: ", error)

# Example document entry
doc = Document(index = "chatbot", 
               id =1, 
               source = {'author1': 'Louis',
                        'author2': 'Clark'})

def insert_document(document):

    try:
        response = client.index(doc.index, body=doc.source, id=doc.id)
        print ("Document index() response:", response, "n")
    except Exception as error:
        print ("client.index() ERROR:", error, "n")


def query_document(index="chatbot",id=1):

    try:
        response = client.get(index = index, id=id)
        print ("Document index() response:", response, "n")
    except Exception as error:
        print ("client.index() ERROR:", error, "n")

