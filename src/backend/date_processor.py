import os
import json
import re
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Baixar os dados do NLTK, se necessário
nltk.download('punkt')
nltk.download('stopwords')

def extract_text_from_pdf(pdf_path):
    """
    Extrai o texto bruto de um arquivo PDF.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def clean_text(text):
    """
    Remove stopwords, caracteres especiais e normaliza o texto.
    """
    # Tokenizar o texto
    words = word_tokenize(text.lower())

    # Carregar stopwords em português
    stop_words = set(stopwords.words('portuguese'))

    # Filtrar palavras
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    # Recriar o texto filtrado
    return " ".join(filtered_words)

def parse_text_to_structure(text):
    """
    Estrutura o texto em um dicionário baseado nos padrões encontrados.
    """
    # Regex para capturar informações estruturadas
    projeto_de_lei = re.search(r"Projeto de Lei n° (\d+), de (\d+)", text.replace('\n', ' '))
    ementa = re.search(r"Ementa:\s*(.*?)\nAssunto", text, re.DOTALL)
    
    # A nova regex para tramitações, mais flexível
    tramitações = re.findall(r"(Tramitação\s*.*?Decisão.*?transformada.*?norma jurídica)", text, re.DOTALL)

    # Exibindo as capturas para depuração
    print(f"Projeto de Lei: {projeto_de_lei.groups() if projeto_de_lei else 'Não encontrado'}")
    print(f"Ementa: {ementa.group(1).strip() if ementa else 'Não encontrado'}")
    print(f"Tramitações: {tramitações}")

    # Montar o JSON estruturado
    data = {
        "projeto_de_lei": {
            "numero": projeto_de_lei.group(1) if projeto_de_lei else None,
            "ano": projeto_de_lei.group(2) if projeto_de_lei else None,
            "ementa": ementa.group(1).strip() if ementa else None,
            "tramitações": [{"detalhes": tr.strip()} for tr in tramitações]
        }
    }
    return data


def save_to_json(data, output_path):
    """
    Salva o dicionário em um arquivo JSON.
    """
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def process_all_pdfs(input_folder, output_folder):
    """
    Processa todos os PDFs de uma pasta e salva os resultados em outra pasta.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".pdf", ".json"))

            print(f"Processando: {filename}...")
            try:
                raw_text = extract_text_from_pdf(pdf_path)
                print(f"Texto extraído: {raw_text[:500]}")
                cleaned_text = clean_text(raw_text)
                print(f"Texto limpo: {cleaned_text[:500]}")
                structured_data = parse_text_to_structure(cleaned_text)
                print(f"Dados estruturados: {structured_data}")
                save_to_json(structured_data, output_path)
                print(f"Salvo em: {output_path}")
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

if __name__ == "__main__":
    input_folder = "../../date/raw/"
    output_folder = "../../date/processed/"
    process_all_pdfs(input_folder, output_folder)
    
 

