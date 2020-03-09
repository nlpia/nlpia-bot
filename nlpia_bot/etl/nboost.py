import requests
from pprint import pprint

response = requests.get(
    url='http://localhost:9200/*/_search',
    json={
        'nboost': {
            'uhost': 'localhost',
            'uport': 9200,
            'query_path': 'body.query.match.text',
            'topk_path': 'body.size',
            'default_topk': 10,
            'topn': 50,
            'choices_path': 'body.hits.hits',
            'cvalues_path': '_source.text'
        },
        'size': 2,
        'query': {
            'match': {'text': 'When Barack Obama was born?'}
        }
    }
)

pprint(response.json())