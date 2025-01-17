import spacy
import os
import json
import re

nlp = spacy.load("pt_core_news_sm")

def chunkenizacao(text):

    chunking = []

    doc = nlp(text)

    # Extração de sintagmas nominais, verbos, entidades nomeadas e números
    for chunk in doc.noun_chunks:
        chunking.append(chunk.text)
        
    for ent in doc.ents:
        if ent.label_ == 'DATE' or ent.label_ == 'CARDINAL':
            chunking.append(ent.text)
        else:
            chunking.append(ent.text)
    
    # Adicionar números diretamente, caso não sejam capturados
    for token in doc:
        if token.like_num: 
            chunking.append(token.text)

    # Verificação explícita para datas no formato "dd/mm/yyyy"
    date_pattern = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
    dates = re.findall(date_pattern, text)
    for date in dates:
        if date not in chunking:
            chunking.append(date)
    
    return chunking
        
def recursao(value):

    result = {}

    if type(value) == str:
        result = chunkenizacao(value)
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

if __name__ == '__main__':
    for arq in os.listdir('../../data_teste/L15041'):
        with open(f'../../data_teste/L15041/{arq}', 'r', encoding='utf-8', errors='ignore') as file:
            data = json.load(file);
        print(f'{arq[:-5]} aberto!')
        
        dictionary = {}

        for key, value in data.items():
            chunkings = recursao(value)
            if chunkings: 
                dictionary[key] = chunkings
            else:
                dictionary[key] = value

        with open(f'../../data_teste/chunking/{arq[:-5]}.json', 'w', encoding='utf-8', errors='ignore') as file_processed:
            json.dump(dictionary, file_processed, ensure_ascii=False, indent=4)

        print(f'{arq[:-5]}')
