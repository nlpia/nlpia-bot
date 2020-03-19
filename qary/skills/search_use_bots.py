""" Universal Sentence Encoding loaded as a lambda function into a Keras model

https://www.dlology.com/blog/keras-meets-universal-sentence-encoder-transfer-learning-for-text-data/

## QUESTION_CATEGORIES

    ABBR - 'abbreviation': expression abbreviated, etc.
    DESC - 'description and abstract concepts': manner of an action, description of sth. etc.
    ENTY - 'entities': animals, colors, events, food, etc.
    HUM - 'human beings': a group or organization of persons, an individual, etc.
    LOC - 'locations': cities, countries, etc.
    NUM - 'numeric values': postcodes, dates, speed,temperature, etc
"""
import re
import pandas as pd
import numpy as np

import tensorflow as tf
import tensorflow_hub as hub

from keras import layers
from keras import Model
from keras import backend as K

# from qa_datasets import load_trec_trainset


# Import the Universal Sentence Encoder's TF Hub module
use_encode = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-large/3")


def encode_texts(texts=["That band rocks!", "That song is really cool."], use_encode=use_encode):
    texts = [texts] if isinstance(texts, str) else texts

    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        usevectors = session.run(use_encode(texts))

    return usevectors


def get_dataframe(filename='train_5500.txt'):
    lines = open(filename, 'r').read().splitlines()
    data = []
    for i in range(0, len(lines)):
        label = lines[i].split(' ')[0]
        label = label.split(":")[0]
        text = ' '.join(lines[i].split(' ')[1:])
        text = re.sub(r'[^A-Za-z0-9 ,\?\'\"-._\+\!/\`@=;:]+', ' ', text)
        data.append([label, text])

    df = pd.DataFrame(data, columns=['label', 'text'])
    df = df[~df.label.isnull()]
    df = df[df.label.str.len().astype(bool)]
    df['label'] = df.label.astype('category')
    return df


test_reviews = ["It was a decent movie, lots of ups and downs. Good thriller -- horrific, disturbing.",
                "I didn't care for the unheroic Protagonist that chose to win the fight to avoid the melodramatic ending of curing his psychosis."]
test_labels = [0, 1]


def use_lambda(x):
    return use_encode(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"]


QA_DF = None  # get_dataframe('train_5500.txt')
QA_CATEGORIES = None  # QA_DF.label.cat.categories.tolist()
TRAIN_TEXTS = None
TRAIN_LABELS = None


def normalize_trainset(df_train=QA_DF):
    global QA_DF
    if df_train is None:
        if QA_DF is None:
            QA_DF = get_dataframe('train_5500.txt')
        df_train = QA_DF
        # get_dataframe('train_5500.txt')
    # df_train = load_trec_trainset()
    # print(df_train.head())
    print(df_train.head())

    train_text = df_train['text'].tolist()
    train_text = np.array(train_text, dtype=object)[:, np.newaxis]
    train_label = np.asarray(pd.get_dummies(df_train.label), dtype=np.int8)
    return train_text, train_label


def build_use_classifier(num_classes=7):
    usevector_shape = (512,)
    input_text = layers.Input(shape=(1,), dtype=tf.string)
    usevector = layers.Lambda(use_lambda, output_shape=usevector_shape)(input_text)
    dense = layers.Dense(256, activation='relu')(usevector)
    pred = layers.Dense(num_classes, activation='softmax')(dense)
    model = Model(inputs=[input_text], outputs=pred)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def train_model(model, train_texts=TRAIN_TEXTS, train_labels=TRAIN_LABELS, filename='model.h5'):
    global TRAIN_TEXTS, TRAIN_LABELS
    if train_texts is None:
        if TRAIN_TEXTS is None:
            TRAIN_TEXTS, TRAIN_LABELS = normalize_trainset()
        train_texts, train_labels = TRAIN_TEXTS, TRAIN_LABELS
    with tf.Session() as session:
        K.set_session(session)
        session.run(tf.global_variables_initializer())
        session.run(tf.tables_initializer())
        history = model.fit(train_texts, train_labels,
                            # validation_data=(test_text, test_label),
                            epochs=10,
                            batch_size=32)
        model.save_weights(filename)
    print(f'Saved model to {filename}.')
    return history


TEST_TEXTS = ["In what year did the titanic sink ?",
              "What is the highest peak in California ?",
              "Who invented the light bulb ?"]


def test_model(model='model.h5', texts=TEST_TEXTS, categories=QA_CATEGORIES):
    texts = np.array(texts, dtype=object)[:, np.newaxis]
    with tf.Session() as session:
        K.set_session(session)
        session.run(tf.global_variables_initializer())
        session.run(tf.tables_initializer())
        if isinstance(model, str):
            filename = model
            model = build_use_classifier(num_classes=len(categories))
            print(f'Loading model from {filename}')
            model.load_weights(filename)
        predictions = model.predict(texts, batch_size=32)

    predict_logits = predictions.argmax(axis=1)
    predicted_labels = [categories[logit] for logit in predict_logits]
    print(predicted_labels)
    df = pd.DataFrame(predictions)
    df.columns = categories
    df['text'] = [t[0] for t in texts]
    df['label'] = predicted_labels
    return df


def generate_from_use(usevector=[]):
    return "Dummy placeholder text until USE generator is working."


def reply(text):
    match = re.match(r'^\s*([Uu][Ss][Ee]\b)?(.*)$')
    conf = 1e-6
    if match:
        text = match.groups()[1]
        conf = 1.
    usevector = encode_texts([text] if isinstance(text, str) else list(text))
    return [(conf, str(pd.Series(usevector).round(2)))]
