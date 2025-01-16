import json
import os
import re

def process_texts_in_file(data, remove_chars=r'[^\w\s]'):
    result = {}
    for key, value in data.items():
        if type(value) == list:
            list_result = []
            for item in value:
                list_result.append(process_texts_in_file(item, remove_chars))
            result[key] = list_result
        if type(value) == dict:
            result[key] = process_texts_in_file(value, remove_chars)
        else:
            if value:
                if type(value) != list:
                    texto = value.lower()
                else:
                    result[key] = [item.lower() if isinstance(item, str) else item for item in value]
                if(key != 'link'):
                    texto = re.sub(remove_chars, '', texto)
                    texto = texto.replace("º", "")
                result[key] = texto
            else:
                result[key] = value
    return result

if __name__ == "__main__":
    directory = "../../data/extracted"
    extension = ".json"
    for i in ['atividade_legislativa', 'leis', 'vetos']:
         for arquivo in os.listdir(f"{directory}/{i}"):
            dictionary = []
            with open(f'{directory}/{i}/{arquivo}', 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f'{arquivo[:-5]}.json aberto')
                
            dictionary = process_texts_in_file(data)
            
            with open(f'../../data/processed/{i}/{arquivo[:-5]}_processed.json', 'w', encoding = 'utf-8', errors= 'ignore') as file_processed:
                json.dump(dictionary, file_processed, ensure_ascii=False, indent=4)