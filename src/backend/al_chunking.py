import re
import json
import os

def extrair_tramitacoes(texto):
    tramitation_matches = re.findall(r"Tramitação:\s*([\s\S]+?)(?=\nDocumentos:|$)", texto, re.DOTALL)
    
    tramitacoes = []
    
    for tram in tramitation_matches:
        blocos = re.split(r"\s*(Data:.*?)(?=\s*Data:|$)", tram, flags=re.DOTALL)

        for bloco in blocos:
            if bloco.strip():
                tramitacoes.append("Tramitação:\n" + bloco.strip())
    
    return tramitacoes

def extrair_documentos(texto):

    documentos_matches = re.findall(r"(?<=Documentos:)[\s\S]+", texto, re.DOTALL)

    documentos = []

    for doc in documentos_matches:
        blocos = re.split(r"\s*(Documento:.*?)(?=\s*Documento:|$)", doc, flags=re.DOTALL)
    
        for bloco in blocos:
            if bloco.strip():
                documentos.append(bloco.strip())
    
    return documentos

# Adiciona metadados
def add_metadados(chunks, texto, caminho):
    title_match = re.search(r"Atividade legislativa:\s*(.*?)\s*Autoria:", texto)
    if title_match:
        title = title_match.group(1)
        chunks_com_metadados = [{"chunk": chunk, "metadata": {"titulo": title, "caminho": caminho}} for chunk in chunks]
        return chunks_com_metadados
    
    return [{"chunk": chunk, "metadata": {"caminho": caminho}} for chunk in chunks]

# Salva os chunks extraídos em um arquivo JSON
def salvar_chunks_json(chunks, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=4)

# Lê todos os PDFs convertidos para texto e extrai chunks
def processar_textos(input_folder, output_file):
    chunks_totais = []

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            txt_path = os.path.join(input_folder, file_name)
            with open(txt_path, "r", encoding="utf-8") as file:
                texto = file.read()
                chunks = extrair_chunks(texto, txt_path)
                chunks_totais.extend(chunks)
    
    salvar_chunks_json(chunks_totais, output_file)

def extrair_chunks(texto, caminho):
    chunks = []

    for padrao in padroes:
        match = re.search(padrao, texto, re.DOTALL)
        if match:
            chunks.append(match.group().strip())

    chunks.extend(extrair_tramitacoes(texto))
    chunks.extend(extrair_documentos(texto))
    chunks = add_metadados(chunks, texto, caminho) 

    return chunks

padroes = [
    r"Atividade legislativa:\s*(.*?)(?=\s*Assunto:|Explicação da ementa:|$)",
    r"Explicação da ementa:\s*(.*?)(?=\s*Assunto:|$)",
    r"Assunto:\s*(.*?)(?=\s*Relatoria:|$)",
    r"Relatoria:\s*(.*?)(?=\s*Tramitação encerrada:|$)",
    r"Tramitação encerrada:\s*(.*?)(?=\s*Tramitação:|$)",
]

# Caminhos de entrada e saída
input_folder = "../../data/extracted/atividade_legislativa/"
output_file = "../../data/chunkings/atividade_legislativa/chunkings.json"

# Executa o processamento
processar_textos(input_folder, output_file)

print("Successfull!")



