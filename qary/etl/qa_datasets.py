""" Question Answering dataset loaders """
import re
import os
import logging
import json
from itertools import chain

import numpy as np
import pandas as pd
import requests
from editdistance import distance

from qary.spacy_language_model import nlp
from qary.constants import DATA_DIR
from qary.etl import scrape_wikipedia


log = logging.getLogger(__name__)

PRIMARY_WORD_LIST_NAMES = ('religion|lang|loca|name|substance|instrument|peop|perc|plant|prof|sport|state'
                           '|temp|title|unit|univ|money|vessel|job|group'
                           ).split('|')
SECONDARY_WORD_LIST_NAMES = ('other|currency|code|num|ord|speed|time|weight|body|def|desc|quot|tech|letter|symbol|word|color'
                             '|abb|act|anim|art|cause|city|comp|country|date|dimen|dise|dist|eff|event|food|mount|popu|prod|term'
                             ).split('|')


def load_trec_taxonomy(url='http://cogcomp.org/Data/QA/QC/definition.html'):
    dfs = pd.read_html(url)
    df = dfs[3]
    df.columns = 'class description'.split()
    df['class'] = df['class'].str.replace('&nbsp ', '')
    df['class'] = df['class'].str.strip()
    df['description'] = df['description'].str.strip()
    df['subclass'] = [x if x != x.upper() else np.nan for x in df['class']]
    df['class'] = [x if x == x.upper() else np.nan for x in df['class']]
    df['class'] = df['class'].fillna(method='ffill')
    df = df.dropna()
    df = df['class subclass description'.split()]
    df.columns = 'label sublabel description'.split()
    df['label'] = df['label'].astype('category')
    df['sublabel'] = df['sublabel'].astype('category')
    taxonomy = dict(question_types=df)
    for k, u in [('profession', 'http://cogcomp.org/Data/QA/QC/lists/prof'),
                 ('mountain', 'http://cogcomp.org/Data/QA/QC/lists/mount'),
                 ('food', 'http://cogcomp.org/Data/QA/QC/lists/food')]:
        taxonomy[k] = requests.get(u).content.decode('latin').split('\n')

    return taxonomy


# def download_word_lists(
#         source_url_path='https://cogcomp.seas.upenn.edu/Data/QA/QC/lists',
#         dest_path='~/midata/public/upenn_word_lists',
#         word_list_names=None):
#     dest_path = expand_filepath(dest_path)
#     mkdir_p(dest_path)

#     if not word_list_names:
#         word_list_names = PRIMARY_WORD_LIST_NAMES + SECONDARY_WORD_LIST_NAMES
#     source_url_path = source_url_path or 'https://cogcomp.seas.upenn.edu/Data/QA/QC/lists'
#     dest_file_paths = []
#     for name in tqdm(word_list_names):
#         source_url_file_path = f'{source_url_path}/{name}'
#         try:
#             resp = requests.get(source_url_file_path)
#         except Exception as e:
#             log.warning(f'Unable to download {source_url_file_path}')
#             log.warning(str(e))
#             continue
#         file_path = os.path.join(dest_path, f'{name}.txt')
#         dest_file_paths.append(file_path)
#         with open(file_path, 'w') as fout:
#             fout.write(resp.text)
#     return list(zip(word_list_names, dest_file_paths))


def load_trec_trainset(url='http://cogcomp.org/Data/QA/QC/train_5500.label'):
    lines = []
    for i in [5500]:  # [1000, 2000, 3000, 4000, 5500]:
        u = url.replace(str(5500), str(i))
        resp = requests.get(u)
        lines.extend(resp.content.decode('latin').split('\n'))
    r = re.compile(r'\s*([A-Z]+)\s*:\s*([a-z]+)\s*(.*)')
    rows = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            row = r.match(line).groups()
        except AttributeError:
            print(f'PROBLEM on line {i}/{len(lines)}:')
            print(line)
            row = line.split(':')
            row = row[0], ':'.join(row[1:]).split()
            try:
                row = row[0], row[1][0], ' '.join(row[1][1:])
            except IndexError:
                row = row[0], 'unknown', str(row[-1])
                break
        rows.append(row)
    df = pd.DataFrame(rows, columns='label sublabel text'.split())
    df['label'] = df['label'].astype('category')
    df['sublabel'] = df['sublabel'].astype('category')
    return df


def load_qa_dataset(filepath=os.path.join('qa_pairs', 'qa-tiny-2020-05-24.json')):
    """ Load a json file containing desired responses, scored for truthfulness

    >>> d = load_qa_dataset()
    >>> d[0]
    {'score': 1.0, 'question': "Who was Jimmy Carter's wife?", 'answer': 'Rosalynn Carter', 'topic': 'Famous People'}
    >>> d[-1]
    {'score': 0.99, 'question': 'When was Barack Obama born?', 'answer': 'August 4, 1961)', 'topic': 'Famous People'}
    """

    filepath = os.path.join(DATA_DIR, filepath) if not os.path.exists(filepath) else filepath
    with open(filepath) as fp:
        dataset = json.load(fp)
    scored_qa_pairs = []
    for topic, qa_pairs in dataset.items():
        log.debug(topic, qa_pairs)
        for question, scored_answers in qa_pairs.items():
            log.debug(question, len(scored_answers))
            if isinstance(scored_answers, str):
                scored_answers = qa_pairs[scored_answers]
            for score, ans in scored_answers:
                scored_qa_pairs.append(dict(zip(
                    'score question answer topic'.split(),
                    (score, question, ans, topic))))
    return scored_qa_pairs


def fold_characters(s):
    r""" Like stemming but for single characters and punctuation rather than multi-char tokens

    >>> s = "Hello -- world's-class\t.\n?"
    >>> fold_characters(s)
    'hello;world;sclass;;'
    """
    s = s.lower().strip()
    s = re.sub(r'\s', '', s)
    s = re.sub(r'-[-]+', ';', s)
    s = s.replace('-', '')
    s = re.sub(r'\W', ';', s)
    return s


def get_bot_accuracies(bot, scored_qa_pairs=None, min_qa_bot_confidence=.2, num_questions=None, shuffle_seed=None):
    """ Compare answers from bot to answers in test set

    >>> from qary.skills import glossary_bots
    >>> bot = glossary_bots.Bot()
    >>> scored_qa_pairs = [dict(question='What is RMSE?', answer='Root Mean Square Error', score=.9, topic='ds')]
    >>> next(get_bot_accuracies(bot=bot, scored_qa_pairs=scored_qa_pairs))['bot_accuracy']
    1.0
    >>> scored_qa_pairs = [dict(question='What is RMSE?', answer='root-mean-sqr-error', score=.9, topic='ds')]
    >>> next(get_bot_accuracies(bot=bot, scored_qa_pairs=scored_qa_pairs))
    {'question': 'What is RMSE?',
     'answer': 'root-mean-sqr-error',
     'score': 0.9,
     'topic': 'ds',
     'bot_answer': 'Root Mean Square Error',
     'bot_w2v_similarity': 0.64...,
     'bot_ed_distance': 0.52...,
     'bot_ed_distance_low': 0.31...,
     'bot_ed_distance_folded': 0.15...,
     'bot_accuracy': 0.65...}
    """
    if scored_qa_pairs is None:
        scored_qa_pairs = load_qa_dataset()
    elif isinstance(scored_qa_pairs, str):
        scored_qa_pairs = load_qa_dataset(scored_qa_pairs)
    if shuffle_seed:
        np.random.seed(shuffle_seed)
        np.random.shuffle(scored_qa_pairs)
    bot_answers = {}
    for i, truth in enumerate(scored_qa_pairs):
        if num_questions and i >= num_questions:
            break
        topic = truth.get('topic')
        if not topic or not truth or not truth['answer'] or not truth['question']:
            continue
        log.warning(f"topic: {truth['topic']}, question: {truth['question']}")
        textgen = scrape_wikipedia.find_article_texts(query=[topic], max_articles=5)
        texts = chain(textgen, scrape_wikipedia.find_article_texts(query=truth['question'], max_articles=10))

        # TODO: def get_best_bot_answer(bot, question, texts)  # memoize
        bot_answer = bot_answers.get(truth['question'], None)
        if not bot_answer:
            for context in texts:
                bot.reset_context(context)
                replies = sorted(bot.reply(truth['question']))
                if len(replies) and sorted(replies)[-1][0] > min_qa_bot_confidence:
                    break
            replies = replies or [(0, "Sorry, I don't know.")]
            bot_answer = replies[-1][1]
            bot_answers[truth['question']] = bot_answer
        truth['bot_answer'] = bot_answer
        # END TODO: def get_best_bot_answer(bot, question, texts)

        truth['bot_w2v_similarity'] = nlp(truth['bot_answer']).similarity(nlp(truth['answer']))
        truth['bot_ed_distance'] = distance(truth['answer'], truth['bot_answer']) / len(truth['answer'])
        truth['bot_ed_distance_low'] = distance(
            truth['answer'].lower().strip(),
            truth['bot_answer'].lower().strip()
        ) / len(truth['answer'].strip())
        truth['bot_ed_distance_folded'] = distance(
            fold_characters(truth['answer']),
            fold_characters(truth['bot_answer'])
        ) / len(truth['answer'].strip())
        truth['bot_accuracy'] = .5 * truth['bot_w2v_similarity'] + .5 * (
            1 - (truth['bot_ed_distance'] + truth['bot_ed_distance_low'] + truth['bot_ed_distance_folded']) / 3)
        log.warning(f"q: accuracy: {truth['question']}: {truth['bot_accuracy']}")
        yield dict(truth)
