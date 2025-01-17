# Geração de embeddings

import os
import json
from nltk.corpus import Tokenizer

sentences = [
    'This is a text',
    'This is a poem',
    'Deep Learning is like poem!'
]

test_data = []

def embedding(sentences):
    tokenizer = Tokenizer(num_words = 100, oov_token = '<OOV>')
    tokenizer.fit_on_texts(sentences)
    
    word_index = tokenizer.word_index
    codes = tokenizer.texts_to_sequences(test_data)
    
    print(word_index)
    print(codes)
    
def recursao(value):
    result = {}
    if type(value) == str:
        result = embedding(value)
    elif type(value) == dict:
        for key, value_sub in value.items():
            result[key] = recursao(value_sub)
    elif type(value) == list:
        list_result = []
        for item in value:
            list_result.append(recursao(item))
        result = list_result
    else:
        result = value
    return result
    
if __name__ == '__main__' :
    directory = "data/extracted"
    extension = ".json"
    for i in ['atividade_legislativa', 'leis', 'vetos']:
         for arquivo in os.listdir(f"{directory}/{i}"):
            with open(f'{directory}/{i}/{arquivo}', 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f'{arquivo[:-5]}.json aberto')
            for key, value in data.items():
                recursao(value)