from simpletransformers.question_answering import QuestionAnsweringModel
import json
import os

from nlpia_bot.constants import DATA_DIR

SQUAD_TRAINING_JSON = os.path.join(DATA_DIR, 'simple-transformers', 'train-v2.0.json')
ST_TRAINING_JSON = os.path.join(DATA_DIR, 'simple-transformers', 'squad-train.json')


def train_squad(path=SQUAD_TRAINING_JSON):
    return path


with open(SQUAD_TRAINING_JSON, 'r') as fin:
    squad_train = json.load(fin)

squad_train = [item for topic in squad_train['data'] for item in topic['paragraphs']]

# Save as a JSON file
with open(ST_TRAINING_JSON, 'w') as fout:
    json.dump(squad_train, fout)


# Create the QuestionAnsweringModel
model = QuestionAnsweringModel('distilbert', 'distilbert-base-uncased-distilled-squad',
                               args={'reprocess_input_data': True, 'overwrite_output_dir': True})

# Train the model with JSON file
model.train_model(ST_TRAINING_JSON)

# The list can also be used directly
# model.train_model(train_data)

# Evaluate the model. (Being lazy and evaluating on the train data itself)
result, text = model.eval_model(ST_TRAINING_JSON)

print(result)
print(text)

print('-------------------')

# Making predictions using the model.
to_predict = [{'context': 'This is the context used for demonstrating predictions.',
               'qas': [{'question': 'What is this context?', 'id': '0'}]}]

print(model.predict(to_predict))
