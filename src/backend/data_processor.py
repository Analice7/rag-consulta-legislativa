import json
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

# Baixar stopwords e recursos do NLTK
nltk.download('stopwords')

# Inicializando stopwords e stemmer
stop_words = set(stopwords.words('portuguese'))
stemmer = RSLPStemmer()

def process_texts_in_file(data, remove_chars=r'[^\w\s/]', remove_stopwords=False, perform_stemming=False, normalize=False):
    result = {}
    for key, value in data.items():
        
        if type(value) == list:
            list_result = []
            for item in value:
                list_result.append(process_texts_in_file(item, remove_chars, remove_stopwords, perform_stemming))
            result[key] = list_result

        elif type(value) == dict:
            result[key] = process_texts_in_file(value, remove_chars, remove_stopwords, perform_stemming)

        elif type(value) == str:
            texto = value
            if normalize:
                texto = value.lower()
            if key != 'link':
                if normalize:
                    texto = re.sub(remove_chars, '', texto) 

                if remove_stopwords:
                    texto = ' '.join([word for word in texto.split() if word not in stop_words])

                if perform_stemming:
                    texto = ' '.join([stemmer.stem(word) for word in texto.split()])

            result[key] = texto
        else:
            result[key] = value
    return result

if __name__ == "__main__":
    directory = "../../data/extracted"
    extension = ".json"
    
    # Parâmetros para controle de stopwords e stemming
    remove_stopwords = False 
    perform_stemming = False 
    normalize = False

    for i in ['atividade_legislativa', 'leis', 'vetos']:
        for arquivo in os.listdir(f"{directory}/{i}"):
            dictionary = []
            with open(f'{directory}/{i}/{arquivo}', 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f'{arquivo[:-5]}.json aberto')
                
            dictionary = process_texts_in_file(data, remove_stopwords=remove_stopwords, perform_stemming=perform_stemming, normalize=normalize)
            
            with open(f'../../data/processed/{i}/{arquivo[:-5]}.txt', 'w', encoding='utf-8', errors='ignore') as file_processed:
                json.dump(dictionary, file_processed, ensure_ascii=False, indent=4)
