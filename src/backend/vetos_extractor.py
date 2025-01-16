import fitz  # PyMuPDF
import json
import os
import re  # Biblioteca para expressões regulares

def extract_veto_details(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()

    # Extraindo o número e ano do veto
    veto_match = re.search(r"VETO N° (\d+), DE (\d{4})", text)
    veto_number, veto_year = veto_match.groups() if veto_match else (None, None)

    # Extraindo a ementa
    ementa_match = re.search(r"(Veto [Pp]arcial aposto.*?\".*?\")", text, re.DOTALL)
    ementa = ementa_match.group(1).replace("\n", " ").strip() if ementa_match else None

    # Extraindo número e ano da mensagem
    mensagem_match = re.search(r"Mensagem nº (\d+) de (\d{4})", text)
    mensagem_number, mensagem_year = mensagem_match.groups() if mensagem_match else (None, None)

    # Ajuste na regex para capturar o texto entre "Senhor Presidente do Senado Federal" e "Essas, Senhor Presidente, são..."
    dispositivos_section_match = re.search(r"veto.*?ao.*?:(.*?)Essas, Senhor Presidente, são as razões que me conduziram a vetar", text, re.DOTALL)

    # Captura a seção de dispositivos vetados (caso exista)
    dispositivos_text = dispositivos_section_match.group(1) if dispositivos_section_match else ""
    dispositivos_text = re.sub(r"Ouvi.*?:", "", dispositivos_text, flags=re.DOTALL)
    dispositivos_text = re.sub(r"Avulso do VET.*?]", "", dispositivos_text, flags=re.DOTALL)
    dispositivos_text = re.sub(r"^\d+\s*$", "", dispositivos_text, flags=re.MULTILINE)

    # Regex para capturar os dispositivos, seus textos e as razões do veto
    padrao = r'\n(.*?)\n(“.*?)(?:Raz|ANEXO).*?\n(“.*?”)'

    # Usando re.findall para capturar todas as ocorrências
    dispositivos_pattern = re.findall(padrao, dispositivos_text, re.DOTALL)

    # Armazenando os dispositivos em formato organizado
    dispositivos = []

    for dispositivo in dispositivos_pattern:
        dispositivo_vetado = dispositivo[0].strip().replace("\n", "")
        texto_dispositivo = dispositivo[1].strip().replace("“", "").replace("”", "").replace("\n", "")  # Remover aspas extras
        razao_veto = dispositivo[2].strip().replace("“", "").replace("”", "").replace("\n", "")  # Remover aspas extras
        
        dispositivos.append({
            'dispositivo vetado': dispositivo_vetado,
            'texto dispositivo': texto_dispositivo,
            'razao veto': razao_veto
        })

    # Montando o dicionário final
    return {
        "veto": {
            "número": veto_number,
            "ano": veto_year,
        },
        "ementa": ementa,
        "mensagem": {
            "número": mensagem_number,
            "ano": mensagem_year,
        },
        "dispositivos vetados": dispositivos
    }

def process_vetos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            input_file = os.path.join(input_folder, file_name)
            output_file = os.path.join(output_folder, file_name.replace(".pdf", ".json"))
            
            print(f"Processando: {file_name}")
            try:
                veto_data = extract_veto_details(input_file)
                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(veto_data, json_file, ensure_ascii=False, indent=4)
                print(f"Salvo: {output_file}")
            except Exception as e:
                print(f"Erro ao processar {file_name}: {e}")

# Uso do script
if __name__ == "__main__":
    input_folder = "../../data/raw/vetos"  # Substitua pelo caminho da pasta com os PDFs
    output_folder = "../../data/extracted/vetos"
    process_vetos(input_folder, output_folder)
