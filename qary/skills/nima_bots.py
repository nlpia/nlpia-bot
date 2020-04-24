#!/usr/bin/env python
# coding: utf-8

# # Project 1 - Text Questions Classification:
# ## Classify a Given Question Text to One of the Six Categories
#
# Description: https://docs.google.com/document/d/14YP8_z1iH4X_eg9wY1HN57HGxlpT53YFMdbe8GeZNUk/edit?usp=sharing
import os
import re
from collections import Counter

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier

from keras import layers
from keras.models import Model
from keras import backend as K
import tensorflow as tf
import tensorflow_hub as hub

from ..constants import DATA_DIR
from .. import spacy_language_model

nlp = spacy_language_model.load("en_core_web_lg")

file_name = os.path.join(DATA_DIR, 'trec', 'train_5500.label')

with open(file_name, 'rb') as f:
    txt = f.read()

lines = txt.decode('latin').splitlines()


df = []
for idx, line in enumerate(lines):
    match = re.match('([A-Z]+):([a-z]+)[ ]+(.+)', line)
    # print(match.groups())
    df.append(match.groups())

df = pd.DataFrame(df, columns=['label', 'sublabel', 'question'])

print(df.head())


# ### 2.1 NLP: Word2Vec
# #### Output: A DataFrame of document vectors


vectors = []

for idx, row in df.iterrows():
    doc = nlp(row['question'])
    vectors.append(pd.DataFrame([t.vector for t in doc]).mean())
    # print(pd.DataFrame([t.vector for t in doc]).mean())

df_vec = pd.DataFrame(vectors)
print(df_vec.head())


# ## 3. ML Modelling
# ### 3.1 Logistic Regression: Main Lable Classification

# #### 3.1.1 Training

# In[84]:

vec_train, vec_test, label_train, label_test = train_test_split(
    df_vec, df['label'], test_size=0.25, random_state=0, stratify=df['label'])


# In[85]:


# import the class

# instantiate the model (using the default parameters)
logreg = LogisticRegression(solver='liblinear', multi_class='auto', class_weight='balanced')

# fit the model with data
logreg.fit(vec_train, label_train)


# #### 3.1.2 Inference

# In[86]:


# Predictions
label_pred_test = logreg.predict(vec_test)
label_pred_train = logreg.predict(vec_train)


# #### 3.1.3 Modelling Performance
# #### Confusion Matrix, Accuracy, Precision, Recall, and F1 Score

# In[87]:


classes = list(set(label_test))

print(classes)


# In[88]:


# import the metrics class

cnf_matrix = metrics.confusion_matrix(label_test, label_pred_test, labels=classes)
cnf_matrix = pd.DataFrame(cnf_matrix, columns=classes)
cnf_matrix.rename(index={i: k for i, k in enumerate(classes)}, inplace=True)

print("Note: Columns (predictions) vs. Rows (actuals)\n")
print(cnf_matrix)


# In[89]:


accuracy = metrics.accuracy_score(label_test, label_pred_test)
precision_score = metrics.precision_score(label_test, label_pred_test, average='macro', labels=classes)
recall_score = metrics.recall_score(label_test, label_pred_test, average='macro', labels=classes)
f1_score = metrics.f1_score(label_test, label_pred_test, average='macro', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# In[90]:


accuracy = metrics.accuracy_score(label_train, label_pred_train)
precision_score = metrics.precision_score(label_train, label_pred_train, average='macro', labels=classes)
recall_score = metrics.recall_score(label_train, label_pred_train, average='macro', labels=classes)
f1_score = metrics.f1_score(label_train, label_pred_train, average='macro', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# **To compute the metrics on the training data as well

# ### 3.2 Logistic Regression: Sublabel Classification

# In[91]:


vec_train, vec_test, sublabel_train, sublabel_test = train_test_split(
    df_vec, df['sublabel'], test_size=0.25, random_state=0, stratify=df['sublabel'])

# instantiate the model (using the default parameters)
logreg = LogisticRegression(solver='liblinear', multi_class='auto', class_weight='balanced')

# fit the model with data
logreg.fit(vec_train, sublabel_train)

# Predictions
sublabel_pred_test = logreg.predict(vec_test)
sublabel_pred_train = logreg.predict(vec_train)


# In[92]:


classes = list(set(sublabel_test))

print(classes)


# In[93]:


cnf_matrix = metrics.confusion_matrix(sublabel_test, sublabel_pred_test, labels=classes)
cnf_matrix = pd.DataFrame(cnf_matrix, columns=classes)
cnf_matrix.rename(index={i: k for i, k in enumerate(classes)}, inplace=True)

print("Note: Columns (predictions) vs. Rows (actuals)\n")
print(cnf_matrix)


# In[94]:


accuracy = metrics.accuracy_score(sublabel_test, sublabel_pred_test)
precision_score = metrics.precision_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
recall_score = metrics.recall_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
f1_score = metrics.f1_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# In[95]:


accuracy = metrics.accuracy_score(sublabel_train, sublabel_pred_train)
precision_score = metrics.precision_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
recall_score = metrics.recall_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
f1_score = metrics.f1_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# ### 3.3 Logistic Regression: Conditional Classification

# In[96]:


for lb in ['ABBR', 'HUM', 'DESC', 'NUM', 'LOC', 'ENTY']:

    vec_train, vec_test, sublabel_train, sublabel_test = train_test_split(
        df_vec[df['label'] == lb], df[df['label'] == lb]['sublabel'],
        test_size=0.25, random_state=0, stratify=df[df['label'] == lb]['sublabel'])

    # instantiate the model (using the default parameters)
    logreg = LogisticRegression(solver='liblinear', multi_class='auto', class_weight='balanced')

    # fit the model with data
    logreg.fit(vec_train, sublabel_train)

    # Predictions
    sublabel_pred_test = logreg.predict(vec_test)
    sublabel_pred_train = logreg.predict(vec_train)

    classes = list(set(sublabel_test))

    cnf_matrix = metrics.confusion_matrix(sublabel_test, sublabel_pred_test, labels=classes)
    cnf_matrix = pd.DataFrame(cnf_matrix, columns=classes)
    cnf_matrix.rename(index={i: k for i, k in enumerate(classes)}, inplace=True)

    print("\n------------------ ", lb, " --------------------\n")
    print("Note: Columns (predictions) vs. Rows (actuals)\n")
    print(cnf_matrix, '\n')

    accuracy = metrics.accuracy_score(sublabel_test, sublabel_pred_test)
    precision_score = metrics.precision_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
    recall_score = metrics.recall_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
    f1_score = metrics.f1_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)

    print("\n------------------ Test --------------------\n")
    print("Accuracy:", accuracy)
    print("Precision:", precision_score)
    print("Recall:", recall_score)
    print("Unweighted Average F1 Score:", f1_score)

    accuracy = metrics.accuracy_score(sublabel_train, sublabel_pred_train)
    precision_score = metrics.precision_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
    recall_score = metrics.recall_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
    f1_score = metrics.f1_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)

    print("\n------------------ Train --------------------\n")
    print("Accuracy:", accuracy)
    print("Precision:", precision_score)
    print("Recall:", recall_score)
    print("Unweighted Average F1 Score:", f1_score)


# 2-stage model: first Pr(main labels) -> add to the vector -> 306 dimension -> new logistic model

# ### 3.4 Decision Tree: Main Labels

# In[97]:


vec_train, vec_test, label_train, label_test = train_test_split(
    df_vec, df['label'], test_size=0.25, random_state=0, stratify=df['label'])

# Create Decision Tree classifer object
clf = DecisionTreeClassifier(criterion="entropy", class_weight='balanced')

# Train Decision Tree Classifer
clf = clf.fit(vec_train, label_train)

# Predict the response for test dataset
label_pred_test = clf.predict(vec_test)
label_pred_train = clf.predict(vec_train)

accuracy = metrics.accuracy_score(label_test, label_pred_test)
print("\n------------------ Test --------------------\n")
print("Accuracy:", accuracy)

accuracy = metrics.accuracy_score(label_train, label_pred_train)
print("\n------------------ Train --------------------\n")
print("Accuracy:", accuracy)


# Explainable but Random forest is better for modelling
# Find out key dimensions

# ### 3.5 Performance Comparison

# ### 3.5.1 **1000 data samples**
#
# || LGR-Main Lables | LGR-Sublabels| LGR-Conditional | Decision Tree-Labels |
# |-----|--------|--------|--------|--------|
# |Accuracy| 0.684 | 0.544 | 0.443 - 0.854 | 0.384 |
#
#
#  **Observation:** Poor calssification performance of ENTY sublabels given the main label, i.e., ENTY.
#
# **Conditioanl Classification**
#
#
# |   | ABBR | HUM | DESC | NUM | LOC | ENTY|
# |---|---|---|---|---|---|---|
# |Accuracy| 0.800 | 0.854 | 0.755 | 0.737 | 0.692 | 0.443 |

# ### 3.5.2 **5452 data samples**
#
# || LGR-Main Lables | LGR-Sublabels| LGR-Conditional | Decision Tree-Labels |
# |-----|--------|--------|--------|--------|
# |Accuracy| 0.743 | 0.650 | 0.689 - 0.909 | 0.428 |
#
#
#  **Observation:** Poor calssification performance of ENTY sublabels given the main label, i.e., ENTY.
#
#  **Conditioanl Classification**
#
#
# |   | ABBR | HUM | DESC | NUM | LOC | ENTY|
# |---|---|---|---|---|---|---|
# |Accuracy| 0.909 | 0.882 | 0.818 | 0.808 | 0.899 | 0.687 |

# ### 3.5.3 **5452 data samples, Balanced training and Stratified sets**
#
# || LGR-Main Lables | LGR-Sublabels| LGR-Conditional | Decision Tree-Labels |
# |-----|--------|--------|--------|--------|
# |Accuracy| 0.733 | 0.643 | 0.716 - 0.954 | 0.440 |
#
#
#  **Observation:** Poor calssification performance of ENTY sublabels given the main label, i.e., ENTY.
#
#  **Conditioanl Classification**
#
#
# |   | ABBR | HUM | DESC | NUM | LOC | ENTY|
# |---|---|---|---|---|---|---|
# |Accuracy| 0.954 | 0.925 | 0.859 | 0.844 | 0.919 | 0.716 |

# - vertical form: how long it takes to train.
# - F1
# - imbalanced dataset
# - balanced = true , or auto
# - Stratified train test split
# - oversampling: repeating the infrequent test data

# Next Step- USE (just encoder)
# BERT (enc/dec) - generate sentence

# ## 4. USE

# ### 4.1 Vector Generation

# In[135]:

module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"
# Import the Universal Sentence Encoder's TF Hub module
embed = hub.Module(module_url)

# Compute a representation for each message, showing various lengths supported.
messages = list(df['question'])

with tf.Session() as session:
    session.run([tf.global_variables_initializer(), tf.tables_initializer()])
    message_embeddings = session.run(embed(messages))


# In[50]:


message_embeddings.shape


# ### 4.2 Logistic Regression: Main Lable Classification

# In[98]:


# import sklearn

vec_train, vec_test, label_train, label_test = train_test_split(
    message_embeddings, df['label'], test_size=0.25, random_state=0, stratify=df['label'])

# import the class

# instantiate the model (using the default parameters)
logreg = LogisticRegression(solver='liblinear', multi_class='auto', class_weight='balanced')

# fit the model with data
logreg.fit(vec_train, label_train)

# Predictions
label_pred_test = logreg.predict(vec_test)
label_pred_train = logreg.predict(vec_train)


# In[99]:


classes = list(set(label_test))

# import the metrics class

cnf_matrix = metrics.confusion_matrix(label_test, label_pred_test, labels=classes)
cnf_matrix = pd.DataFrame(cnf_matrix, columns=classes)
cnf_matrix.rename(index={i: k for i, k in enumerate(classes)}, inplace=True)

print("Note: Columns (predictions) vs. Rows (actuals)\n")
print(cnf_matrix)


# In[102]:


accuracy = metrics.accuracy_score(label_test, label_pred_test)
precision_score = metrics.precision_score(label_test, label_pred_test, average='macro', labels=classes)
recall_score = metrics.recall_score(label_test, label_pred_test, average='macro', labels=classes)
f1_score = metrics.f1_score(label_test, label_pred_test, average='macro', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# In[103]:


accuracy = metrics.accuracy_score(label_train, label_pred_train)
precision_score = metrics.precision_score(label_train, label_pred_train, average='macro', labels=classes)
recall_score = metrics.recall_score(label_train, label_pred_train, average='macro', labels=classes)
f1_score = metrics.f1_score(label_train, label_pred_train, average='macro', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# ### 4.3 Logistic Regression: Sublabel Classification

# In[104]:


vec_train, vec_test, sublabel_train, sublabel_test = train_test_split(
    message_embeddings, df['sublabel'], test_size=0.25, random_state=0, stratify=df['sublabel'])

# instantiate the model (using the default parameters)
logreg = LogisticRegression(solver='liblinear', multi_class='auto', class_weight='balanced')

# fit the model with data
logreg.fit(vec_train, sublabel_train)

# Predictions
sublabel_pred_test = logreg.predict(vec_test)
sublabel_pred_train = logreg.predict(vec_train)

classes = list(set(sublabel_test))

cnf_matrix = metrics.confusion_matrix(sublabel_test, sublabel_pred_test, labels=classes)
cnf_matrix = pd.DataFrame(cnf_matrix, columns=classes)
cnf_matrix.rename(index={i: k for i, k in enumerate(classes)}, inplace=True)

print("Note: Columns (predictions) vs. Rows (actuals)\n")
print(cnf_matrix, "\n")

accuracy = metrics.accuracy_score(sublabel_test, sublabel_pred_test)
precision_score = metrics.precision_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
recall_score = metrics.recall_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
f1_score = metrics.f1_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# In[105]:


accuracy = metrics.accuracy_score(sublabel_train, sublabel_pred_train)
precision_score = metrics.precision_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
recall_score = metrics.recall_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
f1_score = metrics.f1_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)

print("Accuracy:", accuracy)
print("Precision:", precision_score)
print("Recall:", recall_score)
print("Unweighted Average F1 Score:", f1_score)


# ### 4.4 Logistic Regression: Conditional Classification

# In[106]:


for lb in ['ABBR', 'HUM', 'DESC', 'NUM', 'LOC', 'ENTY']:

    vec_train, vec_test, sublabel_train, sublabel_test = train_test_split(
        message_embeddings[df['label'] == lb], df[df['label'] == lb]['sublabel'],
        test_size=0.25, random_state=0, stratify=df[df['label'] == lb]['sublabel'])

    # instantiate the model (using the default parameters)
    logreg = LogisticRegression(solver='liblinear', multi_class='auto', class_weight='balanced')

    # fit the model with data
    logreg.fit(vec_train, sublabel_train)

    # Predictions
    sublabel_pred_test = logreg.predict(vec_test)
    sublabel_pred_train = logreg.predict(vec_train)

    classes = list(set(sublabel_test))

    cnf_matrix = metrics.confusion_matrix(sublabel_test, sublabel_pred_test, labels=classes)
    cnf_matrix = pd.DataFrame(cnf_matrix, columns=classes)
    cnf_matrix.rename(index={i: k for i, k in enumerate(classes)}, inplace=True)

    print("\n------------------ ", lb, " --------------------\n")
    print("Note: Columns (predictions) vs. Rows (actuals)\n")
    print(cnf_matrix, '\n')

    accuracy = metrics.accuracy_score(sublabel_test, sublabel_pred_test)
    precision_score = metrics.precision_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
    recall_score = metrics.recall_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)
    f1_score = metrics.f1_score(sublabel_test, sublabel_pred_test, average='weighted', labels=classes)

    print("\n------------------ Test --------------------\n")
    print("Accuracy:", accuracy)
    print("Precision:", precision_score)
    print("Recall:", recall_score)
    print("Unweighted Average F1 Score:", f1_score)

    accuracy = metrics.accuracy_score(sublabel_train, sublabel_pred_train)
    precision_score = metrics.precision_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
    recall_score = metrics.recall_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)
    f1_score = metrics.f1_score(sublabel_train, sublabel_pred_train, average='weighted', labels=classes)

    print("\n------------------ Train --------------------\n")
    print("Accuracy:", accuracy)
    print("Precision:", precision_score)
    print("Recall:", recall_score)
    print("Unweighted Average F1 Score:", f1_score)


# ### 4.5 Decision Tree: Main Labels

# In[110]:

vec_train, vec_test, label_train, label_test = train_test_split(
    message_embeddings, df['label'], test_size=0.25, random_state=0, stratify=df['label'])

# Create Decision Tree classifer object
clf = DecisionTreeClassifier(criterion="entropy", class_weight='balanced')

# Train Decision Tree Classifer
clf = clf.fit(vec_train, label_train)

# Predict the response for test dataset
label_pred_test = clf.predict(vec_test)
label_pred_train = clf.predict(vec_train)

accuracy = metrics.accuracy_score(label_test, label_pred_test)
print("\n------------------ Test --------------------\n")
print("Accuracy:", accuracy)

accuracy = metrics.accuracy_score(label_train, label_pred_train)
print("\n------------------ Train --------------------\n")
print("Accuracy:", accuracy)


# ### 4.6 Performance

# #### 4.6.1 **Accuracy - 5452 data samples**
#
# || LGR-Main Lables | LGR-Sublabels| LGR-Conditional | Decision Tree-Labels |
# |-----|--------|--------|--------|--------|
# |Spacy| 0.743 | 0.650 | 0.689 - 0.909 | 0.428 |
# |USE| 0.896 | 0.728 | 0.712 - 0.895 | 0.717 |
#
#
#  **Conditioanl Classification**
#
#
# |   | ABBR | HUM | DESC | NUM | LOC | ENTY|
# |---|---|---|---|---|---|---|
# |Spacy| 0.909 | 0.882 | 0.818 | 0.808 | 0.899 | 0.687 |
# |USE| 0.727 | 0.895 | 0.835 | 0.790 | 0.885 | 0.712 |

# #### 4.6.2 **Accuracy - 5452 data samples, Balanced/Stratified**
#
# || LGR-Main Lables | LGR-Sublabels| LGR-Conditional | Decision Tree-Labels |
# |-----|--------|--------|--------|--------|
# |Spacy| 0.733 | 0.643 | 0.716 - 0.954 | 0.440 |
# |USE| 0.902 | 0.739 | 0.770 - 0.957 | 0.718 |
#
#
#  **Conditioanl Classification**
#
#
# |   | ABBR | HUM | DESC | NUM | LOC | ENTY|
# |---|---|---|---|---|---|---|
# |Spacy|  0.954 | 0.925 | 0.859 | 0.844 | 0.919 | 0.716 |
# |USE| 0.818 | 0.957 | 0.859 | 0.879 | 0.923 | 0.770 |

# ## 5. Keras

# In[136]:


def UniversalEmbedding(x):
    return embed(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"]


input_text = layers.Input(shape=(1,), dtype=tf.string)
embedding = layers.Lambda(UniversalEmbedding, output_shape=(512,))(input_text)
dense = layers.Dense(256, activation='relu')(embedding)
pred = layers.Dense(6, activation='softmax')(dense)
model = Model(inputs=[input_text], outputs=pred)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()

text_train, text_test, label_train, label_test = train_test_split(
    df['question'], df['label'], test_size=0.25, random_state=0, stratify=df['label'])

label_train = np.asarray(pd.get_dummies(label_train), dtype=np.int8)
label_test = np.asarray(pd.get_dummies(label_test), dtype=np.int8)

with tf.Session() as session:
    K.set_session(session)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    history = model.fit(text_train,
                        label_train,
                        validation_data=(text_test, label_test),
                        epochs=10,
                        batch_size=32)
    model.save_weights('./model.h5')


# ### 5.1 Performance

# **Accuracy - 5452 data samples, Balanced/Stratified**
#
# || LGR-Main Lables | LGR-Sublabels| LGR-Conditional | Decision Tree-Labels | NN |
# |-----|--------|--------|--------|--------|-------|
# |Spacy| 0.733 | 0.643 | 0.716 - 0.954 | 0.440 | N.A. |
# |USE| 0.902 | 0.739 | 0.770 - 0.957 | 0.718 | 0.918|

# ## 6. Data Story


# In[178]:

labels = ['HUM', 'DESC', 'ENTY', 'LOC', 'ABBR', 'NUM']

word_count = dict.fromkeys(labels)

for label in labels:

    word_count_labeled = Counter()

    for idx, row in df[df['label'] == label].iterrows():
        doc = nlp(row['question'])
        word_count_labeled += Counter([t.text for t in doc
                                       if t.pos_ in
                                       ['NOUN', 'PROPN', 'ADJ', 'ADV', 'PRON']])

    word_count[label] = dict(word_count_labeled)

print(word_count)


# In[182]:


df_word_count = pd.DataFrame(word_count)

df_word_top_five = pd.DataFrame()

for col in df_word_count.columns:
    df_word_top_five = pd.concat([df_word_top_five, df_word_count[col].
                                  sort_values(ascending=False).head(5) /
                                  df_word_count[col].sum() * 100], axis=1, sort=False)


plt.rcParams['figure.figsize'] = [20, 5]
plt.rcParams.update({'font.size': 14})
df_word_top_five.plot.bar(width=0.8)
plt.xlabel('Top 5 Words in each Category')
plt.ylabel('% of Counts in each Category')
plt.xticks()
plt.show()


# In[150]:

df_tidy = pd.melt(df_word_top_five.reset_index(), id_vars='index')
sns.barplot(x='index', y='value', hue='variable', data=df_tidy)
plt.show()


df_label_dummy = pd.get_dummies(df.label)
df_vec_label = pd.concat([df_vec, df_label_dummy], axis=1)
df_vec_label_corr = df_vec_label.corr(method='pearson')
# df_vec_label_corr.style.background_gradient(cmap='coolwarm', axis=None)


fig, ax = plt.subplots(figsize=(3, 20))

ax = sns.heatmap(
    df_vec_label_corr,
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=10),
    square=False, ax=ax
)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=90,
    horizontalalignment='right'
)


# In[ ]:
