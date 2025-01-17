import spacy
import os
import json

nlp = spacy.load("pt_core_news_sm")

def chunkenizacao(text):
    doc = nlp(text)
    # Tokenização e exibição das informações de cada token
    for token in doc:
        print(token.text, token.pos_, token.dep_)
        
def recursao(value):
    if type(value) == str:
        chunkenizacao(value)
    elif type(value) == dict:
        for key, value_sub in value.items():
            recursao(value_sub)
    elif type(value) == list:
        for item in value:
            recursao(item)
    else:
        print("nulo (null)")

if __name__ == '__main__':
    for arq in os.listdir('data_teste/L15041'):
        with open(f'data_teste/L15041/{arq}', 'r', encoding='utf-8', errors='ignore') as file:
            data = json.load(file);
        print(f'{arq[:-5]} aberto!')
        
        for key, value in data.items():
            recursao(value)