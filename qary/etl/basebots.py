""" Transformer based chatbot dialog engine for answering questions """
import logging
import os
import uuid
import urllib.request
import zipfile
# from multiprocessing import cpu_count

from qary.etl.netutils import DownloadProgressBar
from qary.constants import DATA_DIR, args  # , USE_CUDA


log = logging.getLogger(__name__)


class ContextBot:
    """ Manages self.context attribute with update_, reset_ and reply(context=...) methods

    >>> conbot = ContextBot({'init': 'init_value'})
    >>> conbot.context
    {'init': 'init_value'}
    >>> conbot.update_context({'new': 'new_value'})
    >>> conbot.context
    {'init': 'init_value', 'new': 'new_value'}
    >>> conbot.update_context({'init': 'updated_exisiting', 'new': {'inner': 'new_innards'}})
    >>> conbot.context
    {'init': 'updated_exisiting', 'new': {'inner': 'new_innards'}}
    >>> conbot.reply('Hi', {'new': {'inner_reply': 'new_inner_reply'}})
    >>> conbot.context
    {'init': 'updated_exisiting', 'new': {'inner_reply': 'new_inner_reply'}}
    """

    def __init__(self, context=None, args=args):
        super().__init__()
        self.context = {}
        if isinstance(context, str):
            log.warning("Deprecated API: `context` should be a nested dictionary. Texts belong at `context['doc']['text']`).")
            self.context.update({'doc': {'text': context}})
        else:
            self.context.update(context)
        self.context.update({'args': args})

    def update_context(self, context=None):
        context = {} if context is None else context
        self.context.update(context)

    def reset_context(self, context=None):
        self.context = {} if context is None else context

    def reply(self, statement, context=None):
        """ Chatbot "main" function to respond to a user command or statement

        >>> reply('Hi')[0][1]
        Hello!
        """
        return []


class HistoryBot:
    """ Remembers the history of every user statement and bot response string

    >>> hb = HistoryBot()
    >>> responses1 = hb.reply('Hi')
    >>> responses2 =
    """

    def __init__(self, history=None):
        super().__init__()
        self.history = history or []

    def reply(self, statement):
        """ Chatbot "main" function to respond to a user command or statement

        >>> reply('Hi')[0][1]
        Hello!
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
        url_str = f"http://totalgood.org/midata/models/qa/{qa_model}.zip"
        model_dir = os.path.join(DATA_DIR, 'qa-models', f"{qa_model}")
        model_type = qa_model.split('-')[0].lower()
        if not os.path.isdir(model_dir):
            os.makedirs(model_dir)

        if (
            not os.path.exists(os.path.join(model_dir, 'config.json')) or
            not os.path.exists(os.path.join(model_dir, 'pytorch_model.bin')) or
            not os.path.exists(os.path.join(model_dir, 'tokenizer_config.json')) or
            not os.path.exists(os.path.join(model_dir, 'version.json')) or
            (model_type == 'bert' and not os.path.exists(os.path.join(model_dir, 'vocab.txt'))) or
            (model_type == 'albert' and not os.path.exists(os.path.join(model_dir, 'spiece.model')))
        ):
            zip_local_path = os.path.join(DATA_DIR, 'qa-models', f"{qa_model}.zip")
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url_str.split('/')[-1]) as t:
                urllib.request.urlretrieve(url_str, filename=zip_local_path, reporthook=t.update_to)
            with zipfile.ZipFile(zip_local_path, 'r') as zip_file:
                zip_file.extractall(os.path.join(DATA_DIR, 'qa-models'))
            os.remove(zip_local_path)

    def encode_tranformer_input(self, statement, context=None):
        """ Convert statement and context strings into nested dict format compatible with [AL]BERT transformer

        >>> bot = Bot()
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
            self.context.update({'doc': {'text': text}})
        else:
            self.context.update(context)
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

        >>> bot = Bot()
        >>> bot.decode_output([{'id': 'unique_id', 'answer': 'response', 'probability': 0.75}])
        (0.75, 'response')
        """
        return output[0]['probability'], output[0]['answer']

    def reply(self, statement, context=''):
        responses = []
        return responses
