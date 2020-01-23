""" Transformer based chatbot dialog engine for answering questions """
import os
import uuid
import logging

from simpletransformers.question_answering import QuestionAnsweringModel

from nlpia_bot.etl import scrape_wikipedia
from nlpia_bot.constants import DATA_DIR, USE_CUDA

log = logging.getLogger(__name__)


class Bot:

    def __init__(self, path=os.path.join(DATA_DIR, 'simple-transformers')):
        #self.transformer_loggers = []
        #for name in logging.root.manager.loggerDict:
        #    if len(name) >= 12 and name[:12] == 'transformers':
        #        self.transformer_loggers.append(logging.getLogger(name))
        #        self.transformer_loggers[-1].setLevel(logging.ERROR)
        self.model = QuestionAnsweringModel('bert', path, use_cuda=USE_CUDA)

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
        response = ''
        docs = scrape_wikipedia.scrape_article_texts(statement)
        for context in docs:
            heading = context.split('\n')[0]
            log.info(f'Reading up on {heading}')
            encoded_input = self.encode_input(statement, context)
            encoded_output = self.model.predict(encoded_input)
            decoded_output = self.decode_output(encoded_output)
            if len(decoded_output) > 0:
                response = response + decoded_output + ' . . .\n'
                break
        return [(max(len(response), 1), response.rstrip())]


def main():
    pass


if __name__ == '__main__':
    main()
