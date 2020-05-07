# from qarysite.qary_app.models import Documnet
""" find and store dooocumnets and model in django database

>>> cache_doc("hello world",title='world')
'world'
"""


def cache_doc(text, title):
    # insert text into database,URL
    # Documnet.objects.create(title=title)
    return title


def find_in_cache(title):
    # search database for title match in the column title (field)
    text = None  # change
    return text
