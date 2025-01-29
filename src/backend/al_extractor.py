import fitz 
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def concatenar(dados, nivel=0):
    texto = ""
    indentacao = "  " * nivel

    if isinstance(dados, dict):
        for chave, valor in dados.items():
            texto += f"{indentacao}{chave.capitalize()}: "
            if isinstance(valor, (dict, list)):
                texto += "\n" + concatenar(valor, nivel + 1)
            elif valor: 
                texto += f"{valor}\n"
            else:
                texto += "Não disponível\n" 
    elif isinstance(dados, list):
        for item in dados:
            texto += concatenar(item, nivel + 1)
    else:
        # if "Atividade Legislativa" in texto:
        #     text = re.sub(r'Atividade Legislativa[\s\S]*?n[º°] \d+, de \d{4}', '', text, flags=re.IGNORECASE)
        texto += f"{indentacao}{dados}\n"

    return texto

# Extrai texto de todas as páginas de um arquivo PDF.
def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
       return "".join(re.sub(r"\bpg\s*\d+\b", "", page.get_text(), flags=re.IGNORECASE) for page in pdf)

# Processa o texto extraído do PDF e organiza em um formato estruturado.
def parse_text_to_structure(text):
    
    structured_data = {} 

    # Extrai número e ano do projeto
    title_match = re.search(r"(.+? n[º°] \d+, de \d{4})", text)
    if title_match:
        structured_data["atividade legislativa"] = title_match.group(1)
    
    # Extrai autoria
    author_match = re.search(r"Autoria:\s*(.+)", text)
    if author_match:
        structured_data["autoria"] = author_match.group(1)

    # Extrai iniciativa
    initiative_match = re.search(r"Iniciativa:\s*(.+?)(?:\n(Ementa:|$))", text)
    if initiative_match:
        structured_data["iniciativa"] = initiative_match.group(1)

    # Extrai ementa
    ementa_match = re.search(r"Ementa:\s*(.*?)(?=\s*Assunto:|Explicação da Ementa:|$)", text, re.DOTALL)
    if ementa_match:
        structured_data["ementa"] = ementa_match.group(1).strip()

    # Extrai explicação da ementa
    explication_match = re.search(r"Explicação da Ementa:\s*(.+?)(?=\nAssunto:)", text, flags=re.DOTALL)
    if explication_match:
        structured_data["explicação da ementa"] = explication_match.group(1)

    # Extrai o Assunto (Não mudar)
    subject_match = re.search(r"Data de Leitura:\s*([^\n]+)", text)
    if subject_match:
        structured_data["assunto"] = subject_match.group(1).strip()

    # Extrai a Data de Leitura
    reading_date_match = re.search(r"Data de Leitura:\s*([^\n]+)(?:\n(Tramitação encerrada)|$)", text)
    if reading_date_match:
        structured_data["data de leitura"] = reading_date_match.group(1).strip()

    # Extrai despacho
    dispatch_match = re.search(r"Despacho:\s+((?:.|\n)*?)(?:\nAtividade\s+Legislativa.*|$)", text, re.DOTALL)
    if dispatch_match:
        dispatch = dispatch_match.group(1).strip()
        if "despacho" in structured_data:
            structured_data["despacho"] += " " + dispatch.strip()
        else:
            structured_data["despacho"] = dispatch.strip()

    # Extrai relatoria
    reporting_match = re.search(r"Relatoria:\s+((?:.|\n)*?)(?:\n(Despacho:)|$)", text, re.DOTALL)
    if reporting_match:
        reporting = reporting_match.group(1)
        if "relatoria" in structured_data:
            structured_data["relatoria"] += " " + reporting.strip()
        else:
            structured_data["relatoria"] = reporting.strip()

    # Extrai tramitação encerrada
    tramitation_cloded_match = re.search(r"Tramitação encerrada\s+(.+?)(?=\s*(Relatoria:|Despacho:|$))", text, re.DOTALL)
    if tramitation_cloded_match:
        tramitation_cloded = tramitation_cloded_match.group(1)

        tramitation_lines = {}
        
        decision = re.search(r"(.+?)\s*Decisão:", tramitation_cloded, re.DOTALL)
        decision = decision.group(1).strip() if decision else None
                                        
        destiny = re.findall(r"Último local:\s*(.+?)(?=\s*(Destino:|Último estado:|$))", tramitation_cloded, re.DOTALL)
        destiny = destiny[0][0].strip() if destiny else None

        last_location = re.findall(r"Decisão:\s*(.+?)(?=\s*(Último local:|Destino:|Último estado:|$))", tramitation_cloded, re.DOTALL)
        last_location = last_location[0][0].strip() if last_location else None

        last_state = re.findall(r"Último estado:\s*(.+?)(?=\s*(Matérias Relacionadas:|$))", tramitation_cloded, re.DOTALL)
        last_state = last_state[0][0].strip() if last_state else None

        tramitation_lines = {
            "decisão": decision,
            "destino": destiny,
            "último local": last_location,
            "último estado": last_state
        } 

        structured_data["tramitação encerrada"] = tramitation_lines

    
    # Extrai tramitação
    tramitation_matches = re.findall(r"TRAMITAÇÃO[\s\S]+?(?=\nDOCUMENTOS|pg \d|$)", text, re.DOTALL)
    if not tramitation_matches:
        print("Nenhuma tramitação encontrada.")
        return []
    
    combined_tramitation = " ".join(tramitation_matches)

    tramitation_blocks = re.findall(r"(\d{2}/\d{2}/\d{4}.*?Ação:.*?(?=\d{2}/\d{2}/\d{4}|$))", combined_tramitation, re.DOTALL)

    organized_tramitation = []

    for block in tramitation_blocks:
        if not block.strip():
            continue

        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", block)
        date = date_match.group(1) if date_match else None

        org_match = re.search(r"\d{2}/\d{2}/\d{4}\s+([^\n]+)", block)
        org = org_match.group(1).strip() if org_match else None

        if org and "Situação:" in block: 
            situacao_match = re.search(rf"{re.escape(org)}\s*(.*?)(?=\s*Situação:|$)", block, re.DOTALL) if org else None
            situacao = situacao_match.group(1).strip() if situacao_match else None

            acao_match = re.search(rf"{re.escape(org)}.*?Situação:\s*(.*?)(?=\s*(Ação:|$))", block, re.DOTALL) if org else None
            acao = acao_match.group(1).strip() if acao_match else None

        else:
            situacao = None
            acao_match = re.search(rf"{re.escape(org)}.*?Situação:\s*(.*?)(?=\s*(Ação:|$))", block, re.DOTALL) if org else None
            acao = acao_match.group(1).strip() if acao_match else None

        tramitation_entry = {
            "data": date,
            "órgão": org,
            "situação": situacao,
            "ação": acao
        }

        organized_tramitation.append(tramitation_entry)

    structured_data["tramitação"] = organized_tramitation

    # Extrai documentos
    documents_matches = re.findall(r"DOCUMENTOS[\s\S]*?(?=\n[A-Z ]+:\s|$)", text, re.DOTALL)
    text = re.sub(r'\bDOCUMENTOS\b', '', text) 
    flag = 0

    if not documents_matches:
        print("Nenhum documento encontrado.")
        return []
        
    combined_documents = " ".join(documents_matches)

    documents_blocks = re.findall(r"(.*?\d{2}/\d{2}/\d{4}\nData:.*?)(?=\d{2}/\d{2}/\d{4}\nData:|$)", combined_documents, re.DOTALL)

    organized_documents = []

    next_document = None
    for block in documents_blocks:
        if not block.strip():
            continue

        if not flag:

            document_match = re.search(r"(.+?)\s(\d{2}/\d{2}/\d{4})", block)
            document = document_match.group(1) if document_match else None

            data_match = re.search(rf"{re.escape(document)}\s*(.*?)(?=\s*Data:|$)", block, re.DOTALL) if document else None
            data = data_match.group(1).strip() if data_match else None

            autor_match = re.search(r"\d{2}/\d{2}/\d{4}\nData:\s+([^\n]+)", block)
            author = autor_match.group(1).strip() if autor_match else None

            place_match = re.search(r"Autor:\s+([^\n]+)", block)
            place = place_match.group(1).strip() if place_match else None

            action_match = re.search(r"Local:\s*(.+?)(?=\s*(Ação Legislativa:|$))", block)
            action = action_match.group(1).strip() if action_match else None

            describe_match = re.search(r"Ação Legislativa:\s*(.+?)(?=\s*(Descrição/Ementa:|$))", block)
            describe = describe_match.group(1).strip() if describe_match else None

            next_document_match = re.search(r"(Descrição/Ementa:)\s*(.+?)(?=\n[A-Z ]+:|$)", block, re.DOTALL)

            if not next_document_match:
                next_document_match = re.search(r"(Ação Legislativa:)\s*(.+?)(?=\n[A-Z ]+:|$)", block, re.DOTALL)

            next_document = next_document_match.group(2).strip() if next_document_match else None

            flag = 1

        else:

            document = next_document

            data_match = re.search(r"(.*?)(?=\s*Data:)", block)
            data = data_match.group(1).strip() if data_match else None

            autor_match = re.search(r"\d{2}/\d{2}/\d{4}\nData:\s+([^\n]+)", block)
            author = autor_match.group(1).strip() if autor_match else None

            place_match = re.search(r"Autor:\s+([^\n]+)", block)
            place = place_match.group(1).strip() if place_match else None

            action_match = re.search(r"Local:\s*(.+?)(?=\s*(Ação Legislativa:|$))", block)
            action = action_match.group(1).strip() if action_match else None

            describe_match = re.search(r"Ação Legislativa:\s*(.+?)(?=\s*(Descrição/Ementa:|$))", block, re.DOTALL)

            if not describe_match:
                describe_match = re.search(r"Local:\s*(.+?)(?=\s*(Descrição/Ementa:|$))", block, re.DOTALL)

            describe = describe_match.group(1).strip() if describe_match else None

            next_document_match = re.search(r"(Descrição/Ementa:)\s*(.+?)(?=\n[A-Z ]+:|$)", block, re.DOTALL)

            if not next_document_match:
                next_document_match = re.search(r"(Ação Legislativa:)\s*(.+?)(?=\n[A-Z ]+:|$)", block, re.DOTALL)

            next_document = next_document_match.group(2).strip() if next_document_match else None

        # Montar o bloco estruturado
        document_entry = {
            "documento" : document,
            "data": data,
            "autor": author,
            "local": place,
            "ação legislativa": action,
            "descrição/Ementa": describe
        }

        organized_documents.append(document_entry)

    structured_data["documentos"] = organized_documents

    return structured_data

def save_to_txt(data, output_file):
    formatted_text = concatenar(data)
    # Removendo quebras de linha
    formatted_text = formatted_text.replace('\n', ' ')
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(formatted_text)

# Processo completo: extrai texto do PDF, aplica a função concatenar e salva no TXT.
def process_pdf(pdf_path, txt_output_path):
    print(f"Processando o arquivo: {pdf_path}...")
    try:
        text = extract_text_from_pdf(pdf_path)
        text = parse_text_to_structure(text)
        save_to_txt(text, txt_output_path)

        print(f"Texto extraído e salvo em {txt_output_path}")
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")


# Processa todos os PDFs em uma pasta de entrada e salva os TXTs na pasta de saída.
def process_all_pdfs(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, file_name)
            txt_output_path = os.path.join(
                output_folder, os.path.splitext(file_name)[0] + ".txt"
            )
            process_pdf(pdf_path, txt_output_path)

# Main:
input_folder = "../../data/raw/atividade_legislativa/"
output_folder = "../../data/extracted/atividade_legislativa/"

process_all_pdfs(input_folder, output_folder)