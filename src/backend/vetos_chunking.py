import os
import re
import json

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
    
    salvar_chunk_json(chunk_final, output_file)

def extrair_dados(dados, txt_path):
    lista = []
    titulo = None
    pl = ""

    dados_list = re.split('\n', dados)
    for item in dados_list:
        titulo_temp = re.search(r'Veto: (.+)', item)
        if titulo_temp:
            titulo = titulo_temp.group(1)  

        pl_temp = re.search(r'Projeto de Lei(.*?nº \d+.*?de \d{4})', item)
        if pl_temp:
            pl = pl_temp.group(1)

        match = re.search(r'(Ementa: .+|Mensagem: .+)', item)
        if match:
            lista.append(match.group(1))

    return titulo, pl, normalizar_list_chunks(lista, titulo, txt_path)

def extrair_dispositivos(dispositivos, titulo, pl, txt_path):
    lista = []
    
    if pl:
        dispositivos = re.sub(r"Projeto de Lei(?! nº)", f"Projeto de Lei{pl}", dispositivos)

    dados_list = re.split(r'\n\n', dispositivos)

    for item in dados_list:
        padrao = r'\s*Dispositivo vetado:\s*(.*?)\n\s*(Texto do dispositivo:\s*.*?)\n\s*(Razão do veto:\s*.*)'
        match = re.search(padrao, item, re.DOTALL)

        if match:
            dispositivo_vetado = match.group(1).strip()
            texto_dispositivo = match.group(2).strip()
            razao_veto = match.group(3).strip()

            if f"Projeto de Lei{pl}" not in dispositivo_vetado:
                dispositivo_completo = f"{dispositivo_vetado} do Projeto de Lei{pl}"
            else:
                dispositivo_completo = dispositivo_vetado

            lista.append({
                'chunk': texto_dispositivo,
                'metadata': {
                    'titulo': titulo,
                    'nome_arquivo': os.path.basename(txt_path).replace('.txt', ''),
                    'tipo': 'Veto',
                    'dispositivo_vetado': dispositivo_completo
                }
            })

            lista.append({
                'chunk': razao_veto,
                'metadata': {
                    'titulo': titulo,
                    'nome_arquivo': os.path.basename(txt_path).replace('.txt', ''),
                    'tipo': 'Veto',
                    'dispositivo_vetado': dispositivo_completo
                }
            })

    return lista

def normalizar_list_chunks(lista, titulo, txt_path):
    nome_arquivo = os.path.basename(txt_path).replace('.txt', '')
    return [{'chunk': item, 'metadata': {'titulo': titulo, 'nome_arquivo': nome_arquivo, 'tipo': 'Veto'}} for item in lista]

def salvar_chunk_json(chunk_final, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(chunk_final, file, ensure_ascii=False, indent=4)

input_folder = 'data/extracted/vetos'
output_file = 'data/chunkings/vetos/chunkings.json' 

processar_chunk(input_folder, output_file)
