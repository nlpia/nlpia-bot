# Book Smarts

Human-composed summaries, paraphrasings, and quotes from books like AIMA, Exhalation: Stories, and Blind Sight.

Yaml files with one file per book, chapter, section or paragraph.

Example:

```python
>>> abbrev = 'aima'
>>> chapter = 1
>>> section = 0
>>> paragraph = 2
>>> filename = f"{abbrev}-{chapter}-{section}-{paragraph}.yml"
>>> data = [
...         "We call ourselves Homo sapiens--man the wise--because our **intelligence** is so important to us.",
...         dict(page=1, line=7, endline=8, chapter=chapter, section=section, paragraph=paragraph),
...        ]
...
>>> filename
'aima-1-0-2.yml'
>>> data
['We call ourselves Homo sapiens--man the wise--because our **intelligence** is so important to us.',
 {'page': 1, 'line': 7, 'endline': 8, 'chapter': 1, 'section': 0, 'paragraph': 2}]
>>> import yaml
>>> with open(filename, 'wt') as fout:
...     yaml.dump(data, fout)
```

#### **`aima-1-0-2.yml`**
```yml
- We call ourselves Homo sapiens--man the wise--because our **intelligence** is so
  important to us.
- chapter: 1
  endline: 8
  line: 7
  page: 1
  paragraph: 2
  section: 0
```

## Books

 AIMA - Artirificial Intelligence a Modern Approach, Fourth Edition

## References

- conversational teaching of logic: https://web.stanford.edu/class/archive/cs/cs103/cs103.1184/notes/Guide%20to%20Logic%20Translations.pdf
- example english->logic translations: https://www.ics.uci.edu/~welling/teaching/271fall09/FOL271-f09.pdf#p15
