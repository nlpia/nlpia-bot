# Turkish Parul_bot

Can our chatbot answer questions in Turkish about Chatbots or Python or Data Science?

Spacy doesn't yet have a [Turkish language model](https://spacy.io/usage/models#languages). NLTK does.

## erturgrul_bot

Try replacing [this](https://github.com/nlpia/nlpia-bot/blob/474b9d7157503ce494bcbb46a551daad1ec354c8/nlpia-bot/scrape_wikipedia.py#L38) call to `Wikipedia()` with `Wikpedia('tr')`.

Then you will need to come up with a way to seed the page scraper with an appropriate equivalent for the wikipedia page on chatbots. What is the Turkish word for Chatbot?

```python
>>> import wikipediaapi as wapi
>>> wiki = wapi.Wikipedia('tr')
>>> page = wiki.page('Chatbot')
>>> page.text
''
>>> page = wiki.page('Python')
>>> page.text
"Python şu anlamlara gelebilir:\n\nPiton (Pythonidae, Pitongiller), bir yılan familyası.\nPython (cins), bir yılan cinsi.\nPython, yüksek seviyeli bir programlama dili.\nCPython, Python'un tamamen C ile yazılmış geleneksel gerçekleştirimi.\nPithon, Yunan mitolojisinde Apollon'un öldürdüğü dev yılan.\nMonty Python, Britanyalı komedi grubu."
>>> history -o -p
```

## NLTK

Here's how to use the NLTK turkish language model (tokenizer):

```python
>>> import nltk
>>> nltk.download('popular')
>>> nltk.corpus.stopwords.words('turkish')
['acaba',
 'ama',
 'aslında',
 'az',
 'bazı',
 'belki',
 'biri',
 'birkaç',
 'birşey',
 'biz',
 'bu',
 'çok',
 'çünkü',
 'da',
 'daha',
 'de',
 'defa',
 'diye',
 'eğer',
 'en',
 'gibi',
 'hem',
 'hep',
 'hepsi',
 'her',
 'hiç',
 'için',
 'ile',
 'ise',
 'kez',
 'ki',
 'kim',
 'mı',
 'mu',
 'mü',
 'nasıl',
 'ne',
 'neden',
 'nerde',
 'nerede',
 'nereye',
 'niçin',
 'niye',
 'o',
 'sanki',
 'şey',
 'siz',
 'şu',
 'tüm',
 've',
 'veya',
 'ya',
 'yani']
```
