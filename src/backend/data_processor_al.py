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

def parse_text_to_structure(text):
    """
    Processa o texto extraído do PDF e organiza em um formato estruturado.
    """
    structured_data = {"paginas": []}  # Estrutura para armazenar os dados
    page_data = {}

    structured_data["paginas"].append(page_data)

    page_data = {}

    # Extrair número e ano do projeto
    title_match = re.search(r"(.+? n[º°] \d+, de \d{4})", text)
    if title_match:
        page_data["Atividade legislativa"] = title_match.group(1)

    # Extrair autoria
    author_match = re.search(r"Autoria:\s*(.+)", text)
    if author_match:
        page_data["Autoria"] = author_match.group(1)

    # Extrair iniciativa
    initiative_match = re.search(r"Iniciativa:\s*(.+?)(?:\n(Ementa:|$))", text)
    if initiative_match:
        page_data["Iniciativa"] = initiative_match.group(1)

    # Extrair ementa
    ementa_match = re.search(r"Ementa:\s*(.*?)(?=\s*Assunto:|$)", text, re.DOTALL)
    if ementa_match:
        page_data["Ementa"] = ementa_match.group(1).strip()

    # Extrair o Assunto (Não mudar)
    subject_match = re.search(r"Data de Leitura:\s*([^\n]+)", text)
    if subject_match:
        page_data["Assunto"] = subject_match.group(1).strip()

    # Extrair a Data de Leitura
    reading_date_match = re.search(r"Data de Leitura:\s*([^\n]+)(?:\n(Tramitação encerrada)|$)", text)
    if reading_date_match:
        page_data["Data de leitura"] = reading_date_match.group(1).strip()

    # Extrair despacho
    dispatch_match = re.search(r"Despacho:\s+((?:.|\n)*?)(?:\n(Relatoria:|TRAMITAÇÃO)|$)", text, re.DOTALL)
    if dispatch_match:
        dispatch = dispatch_match.group(1).split("\n")
        if "Despacho" in page_data:
            page_data["Despacho"].extend(d.strip() for d in dispatch if d.strip())
        else:
            page_data["Despacho"] = [d.strip() for d in dispatch if d.strip()]

    # Extrair relatoria
    reporting_match = re.search(r"Relatoria:\s+((?:.|\n)*?)(?:\n(Despacho:)|$)", text, re.DOTALL)
    if reporting_match:
        reporting = reporting_match.group(1).split("\n")
        if "Relatoria" in page_data:
            page_data["Relatoria"].extend(r.strip() for r in reporting if r.strip())
        else:
            page_data["Relatoria"] = [r.strip() for r in reporting if r.strip()]

    # Extrair tramitação encerrada
    tramitation_cloded_match = re.search(r"Tramitação encerrada\s+(.+?)(?=\s*(Relatoria:|Despacho:|$))", text, re.DOTALL)
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

    
    # Extrair tramitação
    tramitation_matches = re.findall(r"TRAMITAÇÃO[\s\S]+?(?=\nDOCUMENTOS|pg \d|$)", text, re.DOTALL)
    if not tramitation_matches:
        print("Nenhuma tramitação encontrada.")
        return []
    
    combined_tramitation = " ".join(tramitation_matches)

    # Dividir tramitação em blocos por data
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

            acao_match = re.search(rf"{re.escape(org)}.*?Situação:\s*(.*?)(?=\s*Ação:|$)", block, re.DOTALL) if org else None
            acao = acao_match.group(1).strip() if acao_match else None
        else:
            situacao = None
            acao_match = re.search(rf"{re.escape(org)}\s*(.*?)(?=\s*Situação:|$)", block, re.DOTALL) if org else None
            acao = acao_match.group(1).strip() if acao_match else None


        # Montar o bloco estruturado
        tramitation_entry = {
            "Data": date,
            "Órgão": org,
            "Situação": situacao,
            "Ação": acao
        }

        organized_tramitation.append(tramitation_entry)

    page_data["Tramitação"] = organized_tramitation

    # Extrair documentos
    documents_matches = re.findall(r"DOCUMENTOS[\s\S]*?(?=\n[A-Z ]+:\s|$)", text, re.DOTALL)
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
            "Documento" : document,
            "Data": data,
            "Autor": author,
            "Local": place,
            "Ação Legislativa": action,
            "Descrição/Ementa": describe
        }

        organized_documents.append(document_entry)

    page_data["Documentos"] = organized_documents
    
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
    input_folder = "../../data/raw/atividade_legislativa/"
    output_folder = "../../data/processed/atividade_legislativa/"
    process_all_pdfs(input_folder, output_folder)
