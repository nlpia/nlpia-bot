""" Transformer based chatbot dialog engine for answering questions """

import logging
import os
import uuid
from multiprocessing import cpu_count

from simpletransformers.question_answering import QuestionAnsweringModel

from nlpia_bot.etl import scrape_wikipedia
from nlpia_bot.constants import DATA_DIR, USE_CUDA

log = logging.getLogger(__name__)


class Bot:

    def __init__(self):
        self.transformer_loggers = []
        for name in logging.root.manager.loggerDict:
            if len(name) >= 11 and name[:11] in ['transformer', 'simpletrans']:
                self.transformer_loggers.append(logging.getLogger(name))
                self.transformer_loggers[-1].setLevel(logging.ERROR)

        process_count = cpu_count() - 2 if cpu_count() > 2 else 1
        model_path = os.path.join(DATA_DIR, 'simple-transformer')
        args = {
            'process_count': process_count,
            'output_dir': model_path,
            'cache_dir': model_path,
            'no_cache': True,
            'use_cached_eval_features': False,
            'overwrite_output_dir': False,
            'silent': True
        }
    
        self.model = QuestionAnsweringModel('bert', model_path, args=args, use_cuda=USE_CUDA)

    def encode_input(self, statement, context):
        encoded = [{
            'qas': [{
                'id': str(uuid.uuid1()),
                'question': statement
            }],
            'context': context
        }]
        return encoded

    def decode_output(self, output):
        return output[0]['answer']

    def reply(self, statement):
        responses = []
        docs = scrape_wikipedia.scrape_article_texts()
        for context in docs:
            encoded_input = self.encode_input(statement, context)
            encoded_output = self.model.predict(encoded_input)
            decoded_output = self.decode_output(encoded_output)
            if len(decoded_output) > 0:
                responses.append((1, decoded_output))
        return responses
