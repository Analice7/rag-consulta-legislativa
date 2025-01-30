from semantic_router.encoders import HuggingFaceEncoder 
from semantic_chunkers import StatisticalChunker
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import re
import json
import os

encoder = HuggingFaceEncoder() 
chunker = StatisticalChunker(encoder = encoder)
tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
model = BertForSequenceClassification.from_pretrained('neuralmind/bert-base-portuguese-cased')

def processar_chunks(input_folder, output_file):
    chunks_final = []
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            txt_path = os.path.join(input_folder, file_name)
            with open(txt_path, 'r', encoding='utf-8') as file: 
                data = file.read()
            # Separa partes e artigos
            padrao = r"stop|\n"
            data_list = re.split(padrao, data)

            #Retorno no tipo Chunk
            chunks = chunker(docs=data_list, batch_size= 120) 
            #Transforma de List[List[Chunk]] para List[dict]
            chunks_list = normalizar_list_chunks(chunks, txt_path)
            chunks_final.extend(chunks_list)
            
    salvar_chunks_json(chunks_final, output_file)
    
def normalizar_list_chunks(chunks, txt_path):
    chunk_list = []
    padrao = r"(LEI\s+(?:COMPLEMENTAR\s+)?Nº\s+(\d+),\s+DE\s+(\d+)\s+DE\s+([A-ZÇ]+)\s+DE\s+(\d{4}))"
    nome_arquivo = os.path.basename(txt_path)
    nome_arquivo = nome_arquivo.replace('.txt', '')
    
    for chunk in chunks:
        for split in chunk:
            titulo_list = re.search(padrao, split.content)
            if(titulo_list):
                titulo = titulo_list.group(0).capitalize()
                
            text = split.content.replace(r'stop|\"|\\\"', "")
            if(split.token_count > 512):
                text = resumir_texto(text)
            if text.lower() != f'{titulo.lower()}.':
                chunk_com_metadados = [{"chunk": text, "metadata": {"titulo": titulo, "nome_arquivo": nome_arquivo, "tipo": "Lei"}}]
                chunk_list.extend(chunk_com_metadados)
            else:
                print(text)
    return chunk_list

def salvar_chunks_json(chunks_final, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(chunks_final, file, ensure_ascii=False, indent=4)

def resumir_texto(texto, max_length=300):
    #Tokenizar o texto
    inputs = tokenizer.encode_plus(
        texto,
        max_length = max_length,
        truncation = True,
        padding = 'max_length',
        return_tensors='pt'
    )
    # Passa pelo modelo
    with torch.no_grad():
        outputs = model(**inputs)
    # Obtem as previsoes
    logits = outputs.logits
    predicted_class = torch.argmax(logits,dim=1).item()
    # Decodifica
    resumo = tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)
    
    return resumo

input_folder = "data/extracted/leis"
output_file = "data/chunkings/leis/chunkings.json"

processar_chunks(input_folder, output_file)