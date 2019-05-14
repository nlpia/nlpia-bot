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


def get_dataframe(filename):
    lines = open(filename, 'r').read().splitlines()
    data = []
    for i in range(0, len(lines)):
        label = lines[i].split(' ')[0]
        label = label.split(":")[0]
        text = ' '.join(lines[i].split(' ')[1:])
        text = re.sub(r'[^A-Za-z0-9 ,\?\'\"-._\+\!/\`@=;:]+', ' ', text)
        data.append([label, text])

    df = pd.DataFrame(data, columns=['label', 'text'])
    df['label'] = df.label.astype('category')
    return df


test_reviews = ["It was a decent movie, lots of ups and downs. Good thriller -- horrific, disturbing.",
                "I didn't care for the unheroic Protagonist that chose to win the fight to avoid the melodramatic ending of curing his psychosis."]
test_labels = [0, 1]


def use_lambda(x):
    return use_encode(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"]


QA_DF = get_dataframe('train_5500.txt')
QA_CATEGORIES = QA_DF.label.cat.categories.tolist()


def normalize_trainset(df_train=QA_DF):
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


def train_model(model, train_texts, train_labels):
    with tf.Session() as session:
        K.set_session(session)
        session.run(tf.global_variables_initializer())
        session.run(tf.tables_initializer())
        history = model.fit(train_texts, train_labels,
                            # validation_data=(test_text, test_label),
                            epochs=10,
                            batch_size=32)
        model.save_weights('model.h5')
    return history


def test_model(model, categories=QA_CATEGORIES):
    new_text = ["In what year did the titanic sink ?",
                "What is the highest peak in California ?",
                "Who invented the light bulb ?"]

    new_text = np.array(new_text, dtype=object)[:, np.newaxis]
    with tf.Session() as session:
        K.set_session(session)
        session.run(tf.global_variables_initializer())
        session.run(tf.tables_initializer())
        model.load_weights('model.h5')
        predictions = model.predict(new_text, batch_size=32)

    predict_logits = predictions.argmax(axis=1)
    predicted_labels = [categories[logit] for logit in predict_logits]
    print(predicted_labels)
    return predictions, predicted_labels
