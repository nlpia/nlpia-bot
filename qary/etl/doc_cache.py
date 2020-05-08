from qary_app.models import Document


""" find and store dooocumnets and model in django database
>>> cache_doc("hello world",title='world')
'world'
"""


def cache_doc(text, title):

    # insert text into database,URL
    # Documnet.objects.create(title=title)
    return title


def find_in_cache(title):
    pass
    # search database for title match in the column title (field)
