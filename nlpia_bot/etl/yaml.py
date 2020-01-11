import re


def translate_yml_lines(path):
    """ Yield lines of a yaml file, with changes made to accomidate extensions, like unquoted hashtags.

    Transformations:
       any string: any string #hashtag #ht #etc
         => any string: "any string #hashtag #ht #etc"

    >>> import io
    >>> example = 'hello big: World, now. #good #bye'
    >>> list(stream_extended_yaml(io.StringIO())
    ['hello big: "World, now. #good #bye"']
    """
    with open(path, 'rt') as fin:
        for line in fin:
            match = re.match(r'((\s*[^:]*[:]\s*)([^":]*))')
            groups = match.groups() if match else [None]
            if groups[0] == line:
                yield groups[1] + ' "' + groups[2] + '"'
            else:
                yield line


def find_hashtags(s, pattern=r'\s*#[\w\d_-]+'):
    """ Find twitter-style tags embedded within a string.

    >>> d = find_hashtags("Find #this hashtag #too #sarcasm-not.")
    >>> d['cleaned']
    'Find hashtag.'
    >>> d['hashtags']
    ['#sarcasm-not', '#this', '#too']
    """
    s = s or ''
    hashtags = re.findall(pattern, s) or []
    hashtags = sorted(set([t.strip() for t in hashtags]))
    cleaned = re.sub(pattern, '', s)
    return {'cleaned': cleaned, 'hashtags': hashtags}
