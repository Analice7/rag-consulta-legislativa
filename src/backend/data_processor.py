import fitz 
import json
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto de todas as páginas de um arquivo PDF.
    """
    text = ""
    tramitacao = []
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            page_text = page.get_text()
            
            # Adiciona a marcação de página ao texto
            text += page_text + f"\npg {page_num + 1}\n"
            
            # Captura a ementa
            if "ementa" in page_text.lower():
                ementa = re.findall(r"ementa[:\s]+(.*?)\n", page_text, re.IGNORECASE)
                if ementa:
                    text += f"Ementa: {ementa[0]}\n"
            
            # Captura a tramitação
            tramitacao_data = re.findall(r"(\d{2}/\d{2}/\d{4})\s*(.*?)(?=\d{2}/\d{2}/\d{4}|$)", page_text, re.DOTALL)
            for date, action in tramitacao_data:
                tramitacao.append({"date": date, "action": action.strip()})
    
    return text, tramitacao

# def clean_text(text):
#     """
#     Remove stopwords, caracteres especiais e normaliza o texto.
#     """
#     nltk.download('stopwords')
#     nltk.download('punkt')
#     stop_words = set(stopwords.words('portuguese'))
    
#     # Tokenização e remoção de stopwords
#     words = word_tokenize(text, language="portuguese")
#     cleaned_words = [word for word in words if word.lower() not in stop_words and re.match(r'\w+', word)]
    
#     return " ".join(cleaned_words)

def parse_text_to_structure(text):
    """
    Processa o texto extraído do PDF e organiza em um formato estruturado.
    """
    # Dividir o texto em seções por páginas
    sections = []
    page_start = 0
    for match in re.finditer(r"pg \d+", text):
        page_end = match.start()  # Posição antes do marcador "pg"
        if page_end > page_start:
            sections.append(text[page_start:page_end].strip())  # Adiciona o conteúdo da página
        page_start = match.end()  # Atualiza o início da próxima página

    # Adiciona o conteúdo restante após o último marcador de página
    if page_start < len(text):
        sections.append(text[page_start:].strip())

    structured_data = {"paginas": []}

    for section in sections:
        page_data = {}

        # Extrair número e ano do projeto
        title_match = re.search(r"(.+? n[º°] \d+, de \d{4})", section)
        if title_match:
            page_data["Atividade legislativa"] = title_match.group(1)

        # Extrair autoria
        author_match = re.search(r"Autoria:\s*(.+)", section)
        if author_match:
            page_data["Autoria"] = author_match.group(1)

        # Extrair iniciativa
        initiative_match = re.search(r"Iniciativa:\s*(.+?)(?:\n(Ementa:|$))", section)
        if initiative_match:
            page_data["Iniciativa"] = initiative_match.group(1)

        # Extrair ementa
        ementa_match = re.search(r"Ementa:\s*(.*?)(?=\s*Assunto:|$)", section, re.DOTALL)
        if ementa_match:
            page_data["Ementa"] = ementa_match.group(1).strip()

        # Extrair o Assunto (Não mudar)
        subject_match = re.search(r"Data de Leitura:\s*([^\n]+)", section)
        if subject_match:
            # subject = subject_match.group(1).strip()
            page_data["Assunto"] = subject_match.group(1).strip()

        # Extrair a Data de Leitura
        reading_date_match = re.search(r"Data de Leitura:\s*([^\n]+)(?:\n(Tramitação encerrada)|$)", section)
        if reading_date_match:
            page_data["Data de leitura"] = reading_date_match.group(1).strip()


        # # Extrair decisão
        # decision_match = re.search(r"Decisão:\s*(.+)", section)
        # if decision_match:
        #     page_data["decisao"] = subject_match.group(1).strip()

        # Extrair despacho
        dispatch_match = re.search(r"Despacho:\s+((?:.|\n)*?)(?:\n(Relatoria:|TRAMITAÇÃO)|$)", section, re.DOTALL)
        if dispatch_match:
            dispatch = dispatch_match.group(1).split("\n")
            page_data["Despacho"] = [d.strip() for d in dispatch if d.strip()]

        # Extrair relatoria
        reporting_match = re.search(r"Relatoria:\s+((?:.|\n)*?)(?:\n(Despacho:)|$)", section, re.DOTALL)
        if reporting_match:
            reporting = reporting_match.group(1).split("\n")
            page_data["Relatoria"] = [r.strip() for r in reporting if r.strip()]

        # Extrair tramitação encerrada
        tramitation_cloded_match = re.search(r"Tramitação encerrada\s+(.+?)(?=\s*(Relatoria:|Despacho:|$))", section, re.DOTALL)
        if tramitation_cloded_match:
            tramitation_cloded = tramitation_cloded_match.group(1)

            # Divida o conteúdo nas partes corretas
            tramitation_lines = []
            
            # Expressões para capturar as seções específicas (NÃO MUDAR!!!)
            decision = re.search(r"(.+?)\s*Decisão:", tramitation_cloded, re.DOTALL)
            if decision:
                tramitation_lines.append(f"Decisão: {decision.group(1).strip()}")
                                         
            destiny = re.findall(r"Último local:\s*(.+?)(?=\s*(Destino:|Último estado:|$))", tramitation_cloded, re.DOTALL)
            if destiny:
                tramitation_lines.append(f"Destino: {destiny[0][0].strip()}") 

            last_location = re.findall(r"Decisão:\s*(.+?)(?=\s*(Último local:|Destino:|Último estado:|$))", tramitation_cloded, re.DOTALL)
            if last_location:
                tramitation_lines.append(f"Último local: {last_location[0][0].strip()}")  

            last_state = re.findall(r"Último estado:\s*(.+?)(?=\s*(Matérias Relacionadas:|$))", tramitation_cloded, re.DOTALL)
            if last_state:
                tramitation_lines.append(f"Último estado: {last_state[0][0].strip()}") 

            # Adiciona a tramitação finalizada ao JSON
            page_data["Tramitação encerrada"] = tramitation_lines

        # Extrair tramitação (Parei aqui)
        tramitation_match = re.search(r"TRAMITAÇÃO\s+(.+)", section, re.DOTALL)
        if tramitation_match:
            tramitation = tramitation_match.group(1).split("\n")
            page_data["Tramitação"] = [t.strip() for t in tramitation if t.strip()]

        # Extrair documentos
        # document_match = re.search(r"DOCUMENTOS\s+(.+)", section, re.DOTALL)
        # if document_match:
        #     document = document_match.group(1).split("\n")
        #     page_data["Documento"] = [t.strip() for t in document if t.strip()]

        # Extrair despachos e ações
        # actions = []
        # action_matches = re.findall(
        #     r"(\d{2}/\d{2}/\d{4})\s+Situação:(.+?)\nAção:(.+?)(?=\d{2}/\d{2}/\d{4}|$)",
        #     section,
        #     re.DOTALL
        # )
        # for match in action_matches:
        #     actions.append({
        #         "data": match[0],
        #         "situacao": match[1].strip(),
        #         "acao": match[2].strip()
        #     })
        # if actions:
        #     page_data["acoes"] = actions

        # Extrair documentos
        documents = []
        document_matches = re.findall(r"DOCUMENTOS\n(.+?)pg \d", section, re.DOTALL)
        for doc_section in document_matches:
            doc_lines = doc_section.split("\n")
            for line in doc_lines:
                if line.strip():
                    documents.append(line.strip())
        if documents:
            page_data["documents"] = documents

        # Adicionar página aos dados estruturados
        structured_data["paginas"].append(page_data)

    return structured_data

def save_to_json(data, output_path):
    """
    Salva o dicionário estruturado em um arquivo JSON.
    """
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def process_pdf(pdf_path, json_output_path):
    """
    Processo completo: extrai texto do PDF, estrutura os dados e salva no JSON.
    """
    print(f"Processando o arquivo: {pdf_path}...")
    try:
        text, tramitacao_data = extract_text_from_pdf(pdf_path)
        #cleaned_text = clean_text(text)
        structured_data = parse_text_to_structure(text)
        save_to_json(structured_data, json_output_path)
        print(f"Dados extraídos e salvos em {json_output_path}")
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")

def process_all_pdfs(input_folder, output_folder):
    """
    Processa todos os PDFs em uma pasta de entrada e salva os JSONs na pasta de saída.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, file_name)
            json_output_path = os.path.join(
                output_folder, os.path.splitext(file_name)[0] + ".json"
            )
            process_pdf(pdf_path, json_output_path)

if __name__ == "__main__":
    input_folder = "../../date/raw/"
    output_folder = "../../date/processed/"
    process_all_pdfs(input_folder, output_folder)

