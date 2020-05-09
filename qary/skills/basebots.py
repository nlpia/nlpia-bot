""" Transformer based chatbot dialog engine for answering questions """
import logging
import os
import uuid
import urllib.request
import zipfile
# from multiprocessing import cpu_count

from qary.etl.netutils import DownloadProgressBar
from qary.constants import DATA_DIR, MIDATA_URL, MIDATA_QA_MODEL_DIR, args  # , USE_CUDA
from qary.etl.nesting import dict_merge


log = logging.getLogger(__name__)


class Replies(list):
    """ WIP: Container for 2-tuples of scored replies (strings)

    TODO:
        - override __getitem__ to return None when empty
        - validate method to make sure 2-tuples of float, str
        - normalize method to ensures scores add up to 1
        - softmax to improve likelihood of best replies
        - sort method?
    """
    pass


class ContextDict(dict):
    """ WIP: Container for context dict attributes for bots

    ContextDict.merge should use dict_merge
    """

    def merge(self, other):
        dict_merge(self, other)

    def dict_merge(self, other):
        dict_merge(self, other)


class EmptyRepliesBot:
    # def __init__(self, **kwargs):
    #     super().__init__()

    def reply(self, statement, context=None):
        """ Chatbot "main" function to respond to a user command or statement

        >>> bot = EmptyRepliesBot()
        >>> bot.reply('Hi')
        []
        """
        return []


class HiBot(EmptyRepliesBot):
    def reply(self, statement, context=None):
        """ Chatbot "main" function to respond to a user command or statement

        >>> bot = HiBot()
        >>> bot.reply('Hi')
        [(1.0, 'Hi!')]
        """
        s = statement.lower().strip().split()
        if s and s[0] in ('hi', 'hello', 'howdy', 'helo', 'yo'):
            return [(1.0, 'Hi!')]
        return []


class ContextBot:
    """ Manages self.context attribute with update_, reset_ and reply(context=...) methods

    >>> conbot = ContextBot({'init': 'init_value'})
    >>> conbot.context
    {'args': Namespace(bots=...words=[]), 'init': 'init_value'}
    >>> conbot.update_context({'new': 'new_value', 'args': None})
    {'args': None, 'init': 'init_value', 'new': 'new_value'}
    >>> conbot.context
    {'args': None, 'init': 'init_value', 'new': 'new_value'}
    >>> conbot.update_context({'init': 'updated_existing', 'new': {'inner': 'new_innards'}})
    {'args': None, 'init': 'updated_existing', 'new': {'inner': 'new_innards'}}
    >>> conbot.context
    {'args': None, 'init': 'updated_existing', 'new': {'inner': 'new_innards'}}
    >>> conbot.reply('Hi', context={'new': {'inner_reply': 'new_inner_reply'}})
    []
    >>> conbot.context['init']
    'updated_existing'
    >>> conbot.context['new']
    {'inner': 'new_innards', 'inner_reply': 'new_inner_reply'}
    """

    def __init__(self, context=None, args=args, **kwargs):
        super().__init__(**kwargs)
        self.args = args
        self.context = {'args': self.args}
        # self.context = {}
        if isinstance(context, str):
            log.warning("Deprecated API: `context` should be a nested dictionary. Texts belong at `context['doc']['text']`).")
            self.update_context({'doc': {'text': context}})
        else:
            self.update_context(context)

    def update_context(self, context=None):
        logging.warning(f"Reseting self.context using context: {context}")
        if isinstance(context, str):
            context = {'doc': {'text': context}}
        context = {} if context is None else context
        dict_merge(self.context, context)
        logging.warning(f"Updated self.context: {self.context}")
        return self.context

    def reset_context(self, context=None):
        self.context = {'args': self.args}
        if isinstance(context, str):
            context = {'doc': {'text': context}}
        dict_merge(self.context, context)
        logging.warning(f"Reset self.context: {self.context}")
        return self.context

    def reply(self, statement, context=None):
        """ Chatbot "main" function to respond to a user command or statement

        >>> bot = ContextBot()
        >>> bot.reply('Hi', context={'new': 'context'})
        []
        >>> bot.context['new']
        'context'
        >>> len(bot.context.keys())
        2
        """
        self.update_context(context=context)
        return []


class HistoryBot(EmptyRepliesBot):
    """ Remembers the history of every user statement and bot response string

    >>> histbot = HistoryBot()
    >>> responses1 = histbot.reply('Hi')
    >>> responses2 = histbot.reply('Hello')
    >>> histbot.history
    [('Hi', ()), ('Hello', ())]
    """

    def __init__(self, history=None, **kwargs):
        super().__init__(**kwargs)
        self.history = history or []

    def reply(self, statement):
        """ Chatbot "main" function to respond to a user command or statement

        >>> bot = HistoryBot()
        >>> bot.reply('Hi')
        []
        """
        responses = super().reply(statement) or []
        self.history.append((statement, tuple(responses)))
        return responses


class TransformerBot(HistoryBot, ContextBot):
    """ Base Bot class that maintains context and load transformer models.  """

    def __init__(self, context=None, args=args, history=None, **kwargs):
        super().__init__(context=context, args=args, history=history, **kwargs)

    def load_model(self, args):
        self.transformer_loggers = []
        for name in logging.root.manager.loggerDict:
            if (len(name) >= 12 and name[:12] == 'transformers') or name == 'qary.skills.qa_utils':
                self.transformer_loggers.append(logging.getLogger(name))
                self.transformer_loggers[-1].setLevel(logging.ERROR)

        qa_model = args.qa_model
        url_str = f"{MIDATA_URL}/{MIDATA_QA_MODEL_DIR}/{qa_model}.zip"
        log.warning(f"Attempting to download url: {url_str}")
        model_dir = os.path.join(DATA_DIR, 'qa-models', f"{qa_model}")
        model_type = qa_model.split('-')[0].lower()
        if not os.path.isdir(model_dir):
            os.makedirs(model_dir)

        if not all((
            os.path.exists(os.path.join(model_dir, 'config.json')),
            os.path.exists(os.path.join(model_dir, 'pytorch_model.bin')),
            os.path.exists(os.path.join(model_dir, 'tokenizer_config.json')),
            os.path.exists(os.path.join(model_dir, 'version.json')),
            any((model_type == 'bert' and os.path.exists(os.path.join(model_dir, 'vocab.txt'))),
                (model_type == 'albert' and os.path.exists(os.path.join(model_dir, 'spiece.model')))),
        )):
            zip_local_path = os.path.join(DATA_DIR, 'qa-models', f"{qa_model}.zip")
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url_str.split('/')[-1]) as t:
                urllib.request.urlretrieve(url_str, filename=zip_local_path, reporthook=t.update_to)
            with zipfile.ZipFile(zip_local_path, 'r') as zip_file:
                zip_file.extractall(os.path.join(DATA_DIR, 'qa-models'))
            os.remove(zip_local_path)

    def encode_transformer_input(self, statement, context=None):
        """ Convert statement and context strings into nested dict format compatible with [AL]BERT transformer

        >>> bot = TransformerBot()
        >>> encoded = bot.encode_transformer_input('statement', 'context')
        >>> encoded[0]['qas'][0]['question']
        'statement'
        >>> encoded[0]['context']
        'context'
        """
        if context is None:
            context = self.context
        if isinstance(context, str):
            # TODO try/except on [] instead of get to provide deprecation warnings
            text = context
            super().update_context({'doc': {'text': text}})
        else:
            super().update_context(context)
        text = self.context['doc']['text']
        encoded = [{
            'qas': [{
                'id': str(uuid.uuid1()),
                'question': statement
            }],
            'context': text}]
        return encoded

    def decode_transformer_output(self, output):
        """ Extract reply string from the transformer model's prediction output (nested dict)

        >>> bot = TransformerBot()
        >>> bot.decode_transformer_output([{'id': 'unique_id', 'answer': 'response', 'probability': 0.75}])
        (0.75, 'response')
        """
        return output[0]['probability'], output[0]['answer']

    def reply(self, statement, context=None):
        responses = []
        return responses
