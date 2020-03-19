import os
import regex

import pandas as pd
import numpy as np
import sqlite3

from ..constants import BASE_DIR

from git import Repo, InvalidGitRepositoryError, NoSuchPathError

import logging
log = logging.getLogger(__name__)


FIREFOX_PATHS = [
    os.path.expanduser(os.path.join('~', 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')),
    os.path.expanduser(os.path.join('~', 'Library', 'Application Support', 'Firefox', 'Profiles'))
]
IPYTHON_HISTORY_PATH = os.path.expanduser(os.path.join(*('~/.ipython/profile_default/history.sqlite'.split('/'))))


def walk_repos(base_dir=BASE_DIR):
    """ yield a git-python Repo instance for each contained directory with a valid git repo

    Does not recurse within .git repos!

    >>> next(walk_repos(BASE_DIR))
    <git.Repo "...qary/.git">
    """
    base_dir = os.path.abspath(os.path.expanduser(base_dir))
    if os.path.basename(base_dir) == '.git' or not os.path.isdir(base_dir):
        yield
    try:
        yield Repo(base_dir)
    except (InvalidGitRepositoryError, NoSuchPathError):
        pass
    if os.path.basename(base_dir) == '.git' or not os.path.isdir(base_dir):
        yield
    else:
        for d in os.listdir(base_dir):
            for repo in walk_repos(os.path.join(base_dir, d)):
                yield repo


def walk_commits(base_dir=BASE_DIR, author_regex=None, email_regex=None):
    """ yield one commit at a time for repo in base_dir and any contained directories

    >>> recent_commits = next(walk_commits(BASE_DIR))
    >>> sorted(recent_commit.items()))
    [('commit', '...'),
     ('datetime', '20...'),
     ('email', '...'),
     ('name', '...'),
     ('stats',
      {'...': {...}})]
    """
    for repo in walk_repos(base_dir):
        if repo is None:
            continue
        if isinstance(repo, Repo):
            repo.config_reader()
            if repo.git_dir == base_dir:
                continue
            # FIXME: `for branch in repo.branches:`
            try:
                commit_generator = repo.iter_commits()
            except ValueError:
                continue  # base_dir is a '.../.git/' directory
            for c in commit_generator:
                if (not author_regex or regex.match(author_regex, c.author.name)) and (
                        not email_regex or regex.match(email_regex, c.author.email)):
                    # return c
                    yield dict(zip('datetime path refspec email name stats'.split(),
                                   (c.authored_datetime.isoformat(),
                                    repo.working_dir,
                                    c.hexsha,
                                    c.author.email,
                                    c.author.name,
                                    c.stats.files)))


def get_timeline(base_dir=BASE_DIR, author_regex='.*hobs.*', email_regex=None, file_regex='.*[.]py'):
    timeline = []
    for commit in walk_commits(base_dir=base_dir, author_regex=author_regex, email_regex=email_regex):
        file_matches = [f for f in commit['stats'] if not file_regex or regex.match(file_regex, f)]
        timeline.append((
            commit['datetime'],
            commit['path'],
            commit['email'],
            len(commit['stats']),
            ':'.join(file_matches),
            sum(commit['stats'][f]['lines'] for f in file_matches),
            sum(commit['stats'][f]['insertions'] for f in file_matches),
            sum(commit['stats'][f]['deletions'] for f in file_matches),
        ))
    df = pd.DataFrame(timeline, columns='datetime path email num_files files lines insertions deletions'.split())
    df = df.sort_values('datetime')
    df['datetime'] = df['datetime'].apply(lambda dt: pd.to_datetime(dt).tz_convert('US/Pacific'))
    df['date'] = df['datetime'].dt.date
    df['repo'] = df.path.str.split(os.path.sep).apply(lambda x: x[-1])
    # df = df.set_index('datetime')
    return df


def render_report(base_dir=BASE_DIR, author_regex='.*hobs.*', email_regex=None, file_regex='.*[.]py',
                  columns='repo lines'.split(), repos='estuary mcweb anticipate'.split()):
    df = get_timeline(base_dir=base_dir, author_regex=author_regex, email_regex=email_regex)
    df = pd.concat([df[df['repo'] == repo] for repo in repos], axis=0)
    df = df.set_index('date')
    df = pd.concat([df[df['repo'] == repo] for repo in repos], axis=0)['repo lines'.split()]
    html = df[columns].to_html()
    return html

# execute a query on sqlite cursor


def execute_query(cursor, query):
    """ Try to execute a query and if it fails log the error and the sql query that failed """
    try:
        cursor.execute(query)
    except Exception as error:
        log.error(error)
        log.error(f'Failed SQL query: {query}')


def find_firefox_path(path=None):
    if isinstance(path, str):
        if os.path.isdir(path) and path.lower().endswith('profiles'):
            return path
        elif path:
            path = [path]
    paths = FIREFOX_PATHS
    if isinstance(path, (list, tuple, np.ndarray)):
        paths = list(path) + paths
    for path in paths:
        if os.path.isdir(path):
            break
    return path


def find_bookmarks_path(path=None):
    if path and isinstance(path, str) and os.path.isfile(path):
        return path
    else:
        path = find_firefox_path(path)
    path = os.path.join(path, next((fp for fp in os.listdir(path) if fp.endswith('.default'))), 'places.sqlite')
    if os.path.isfile(path):
        return path
    log.error(f'Unable to find {path}')
    return path


def get_bookmarks_cursor(path=None):
    return get_cursor(find_bookmarks_path(path))


# get bookmarks from firefox sqlite database file and print all
def get_bookmarks(cursor_or_path=None):
    cursor = cursor_or_path
    if not hasattr(cursor, 'open') or cursor is None or isinstance(cursor, str):
        cursor = get_bookmarks_cursor(path=cursor_or_path)
    bookmarks_query = (
        "select * from moz_places join moz_bookmarks on moz_bookmarks.fk=moz_places.id where visit_count>0 and moz_places.url like 'http%'"
    )
    execute_query(cursor, bookmarks_query)
    return pd.DataFrame([row for row in cursor],
                        columns='url title rev_host frequency last_visited'.split())


def get_cursor(path):
    return sqlite3.connect(path).cursor()


def get_ipython_cursor(path=IPYTHON_HISTORY_PATH):
    return get_cursor(path or IPYTHON_HISTORY_PATH)


# from .template_generators import generate_sentence  # noqa


class Bot:
    def reply(self, statement):
        """ Generate an invoice or timecard for a project """
        log.info('Timcard reply in progress...')
        responses = []
        match = regex.match(r'\b(timecard|punchcard|invoice)\b[\s]*([a-zA-Z0-9_-]*)\b', statement.lower())
        if match:
            responses.append((1.0, f"Here's your timecard for project {match}"))
        return responses
