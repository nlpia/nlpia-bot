""" Cache the pytorch version of BERT in the `transformers` python site-packages dir

Only needs to be run once during install of simpletransformers to avoid this error:

OSError: Error no file named ['pytorch_model.bin', 'tf_model.h5', 'model.ckpt.index']
         found in directory /home/hobs/code/chatbot/qary/data/simple-transformer
         or `from_tf` set to False
"""
from transformers import BertForMaskedLM


bert = BertForMaskedLM.from_pretrained("bert-base-cased")
