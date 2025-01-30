import os
import re

def processar_chunk(input_folder, output_file):
    chunk_final = []
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.txt'):
            txt_path = os.path.join(input_folder, file_name)
            with open(txt_path, 'r', encoding='utf-8') as file:
                data = file.read()
            
            data_list = re.split('Dispositivos vetados:\n', data)
            titulo, pl, dados_lista = extrair_dados(data_list[0], txt_path)
            chunk_final.extend(dados_lista)
            chunk_final.extend(extrair_dispositivos(data_list[1], titulo, pl, txt_path))
    salvar_chunks_json(chunk_final, output_file)

def extrair_dados(dados, txt_path):
    lista = []
    dados_list = re.split('\n', dados)
    for item in dados_list:
        titulo_temp = re.search(r'Veto:\s*(.*?)', item)
        if titulo_temp:
            titulo = titulo_temp.group(1)
        else:
            pl_temp = re.search(r'Projeto de Lei nº (\d+) de (\d{4})', item)
            if pl_temp:
                pl = pl_temp.group(0)
            lista.append(re.search(r'Ementa: |Mensagem: ', item))
    return titulo, pl, normalizar_list_chunks(lista, titulo, txt_path)

def extrair_dispositivos(dispositivos, titulo, pl, txt_path):
    lista=[]
    dispositivos = re.sub("Projeto de Lei", pl, dispositivos)
    dados_list = re.split('\n\n', dispositivos)
    for item in dados_list:
        padrao = r'\sDispositivo vetado:\s*(.*?)\n\sTexto do dispositivo:\s*(.*?)\n\sRazão do veto:\s*(.*)'
        match = re.search(padrao, item, re.DOTALL)
        lista.extend([match.group(1).strip, match.group(2).strip, match.group(3).strip])
    return normalizar_list_chunks(lista, titulo, txt_path)

def normalizar_list_chunks(lista, titulo, txt_path):
    nome_arquivo = os.path.basename(txt_path).replace('.txt', '')
    return [{'chunk': item, 'metadata':{'titulo': titulo, 'nome_arquivo' :nome_arquivo, 'tipo': 'Veto'}} for item in lista]

def salvar_chunk_json(chunk_final, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(chunk_final, file, ensure_ascii=False, indent=4)

input_folder = 'data/extracted/vetos'
output_file = 'data/chunkings/vetos/chunkings.json' 

processar_chunk(input_folder, output_file)
    
    

            
        