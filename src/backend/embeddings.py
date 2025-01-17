# Geração de embeddings
'''
import os
import json

sentences = [
    'This is a text',
    'This is a poem',
    'Deep Learning is like poem!'
]

test_data = []

def chucking(sentences):
    tokenizer = Tokenizer(num_words = 100, oov_token = '<OOV>')
    tokenizer.fit_on_texts(sentences)
    
    word_index = tokenizer.word_index
    codes = tokenizer.texts_to_sequences(test_data)
    
    print(word_index)
    print(codes)
    
if __name__ == '__main__' :
    directory = "data/extracted"
    extension = ".json"
    for i in ['atividade_legislativa', 'leis', 'vetos']:
         for arquivo in os.listdir(f"{directory}/{i}"):
            with open(f'{directory}/{i}/{arquivo}', 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f'{arquivo[:-5]}.json aberto')
            for key, value in data.items():
                chucking(value)
'''