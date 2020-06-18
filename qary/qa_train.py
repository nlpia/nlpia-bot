from simpletransformers.question_answering import QuestionAnsweringModel
import json
import os
import logging

from tqdm import tqdm

from qary.constants import DATA_DIR
log = logging.getLogger(__name__)

SQUAD_TRAINING_JSON = os.path.join(DATA_DIR, 'simple-transformers', 'train-v2.0.json')
SQUAD_DEVSET_JSON = os.path.join(DATA_DIR, 'simple-transformers', 'dev-v2.0.json')
ST_TRAINING_JSON = os.path.join(DATA_DIR, 'simple-transformers', 'squad-train.json')
MODEL_DIR = os.path.join(DATA_DIR, 'qa-models', 'squad')


def preprocess_squad(squad_path=SQUAD_TRAINING_JSON):
    """ Load raw SQUAD training set v2.0 from Stanford format json and convert to simpletransformer format

    Cache the simpletransformer json format, if it doesn't yet exist in data/simple-transformer
    or the provided path
    """
    with open(squad_path, 'r') as fin:
        squad_train = json.load(fin)
    log.info(f"Loaded {len(squad_train['data'])} examples from {squad_path} dataset...")
    return [item for topic in tqdm(squad_train['data']) for item in topic['paragraphs']]


def load_trainset(train_path=ST_TRAINING_JSON, squad_path=SQUAD_TRAINING_JSON):
    """ Load a preprocessed SQUAD training set into RAM as a list or create it using the raw squad dataset """
    try:
        with open(train_path, 'r') as fin:
            trainset = json.load(fin)
    except (IOError, FileNotFoundError):
        trainset = preprocess_squad(squad_path)
        with open(train_path, 'w') as fout:
            json.dump(trainset, fout)
    return trainset


def train_squad(train_path=ST_TRAINING_JSON, squad_path=SQUAD_TRAINING_JSON, model_path=MODEL_DIR):
    trainset = load_trainset(train_path, squad_path=squad_path)
    model = QuestionAnsweringModel('distilbert', 'distilbert-base-uncased-distilled-squad',
                                   args={'reprocess_input_data': True, 'overwrite_output_dir': True})
    model.train_model(trainset, output_dir=model_path)

    return model


def evaluate(model, test_path=ST_TRAINING_JSON, model_path=MODEL_DIR):
    # Evaluate the model. (Being lazy and evaluating on the train data itself)
    trainset = load_trainset(test_path)

    result, text = model.eval_model(trainset)

    log.info(result)
    log.info(text, output_dir=model_path)
    return result, text


if __name__ == '__main__':
    model = train_squad()
    result_train, text_train = evaluate(model)
    result_dev, text_dev = evaluate(model, test_path=SQUAD_DEVSET_JSON)
