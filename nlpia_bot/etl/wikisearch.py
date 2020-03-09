import wikipedia

def search(term, limit = 3):
    return wikipedia.search(term, results=limit)

def summary(term):
    return wikipedia.summary(term)

def content(term):
    return wikipedia.page(term).content

def title(term):
    return wikipedia.page(term).title

def url(term):
    return wikipedia.page(term).url

if __name__=="__main__":
    term = "who is Stan Lee"
    # print(search(term))
    sum = summary(term)
    print(sum)
    print(type(sum))
    # print(content(term))
    # print(title(term))
    # print(title(term))
    # print(url(term))