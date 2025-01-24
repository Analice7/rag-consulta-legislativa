import fitz  # PyMuPDF
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
    ementa_match = re.sub(r'(\d)\.(\d)', r'\1\2', ementa_match.group(1))
    ementa_match = re.sub(r'(?i)\bart\.', 'artigo', ementa_match)
    ementa_match = re.sub(r'§', 'parágrafo', ementa_match)
    ementa = ementa_match.replace("\n", " ").strip() if ementa_match else None

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
    dispositivos_text = re.sub(r'“(.)”', r'"\1"', dispositivos_text)
    dispositivos_text = re.sub(r'(\d)\.(\d)', r'\1\2', dispositivos_text)
    dispositivos_text = re.sub(r'(?i)\bart\.', 'artigo', dispositivos_text)
    dispositivos_text = re.sub(r'§', 'parágrafo', dispositivos_text)
    dispositivos_text = re.sub(r'\.{4,}', '', dispositivos_text)

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
            'texto do dispositivo': texto_dispositivo,
            'razao do veto': razao_veto
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

def save_as_txt(data, output_file):
    def format_dict(d, level=0):
        result = []
        indent = "\t" * level
        
        if "veto" in d and d["veto"]["número"] and d["veto"]["ano"]:
            result.append(f"{indent}Veto: Veto número {d['veto']['número']}, de {d['veto']['ano']}")
        
        if "ementa" in d and d["ementa"]:
            result.append(f"{indent}Ementa: {d['ementa']}")
        
        if "mensagem" in d and d["mensagem"]["número"] and d["mensagem"]["ano"]:
            result.append(f"{indent}Mensagem: Mensagem número {d['mensagem']['número']}, de {d['mensagem']['ano']}")
        
        if "dispositivos vetados" in d:
            result.append(f"{indent}Dispositivos vetados:")
            for item in d["dispositivos vetados"]:
                result.append(f"{indent}\tDispositivo vetado: {item['dispositivo vetado']}")
                result.append(f"{indent}\tTexto do dispositivo: {item['texto do dispositivo']}")
                result.append(f"{indent}\tRazão do veto: {item['razao do veto']}")
                result.append("")  # Adiciona uma linha em branco após cada dispositivo
        
        return result

    formatted_text = "\n".join(format_dict(data))
    with open(output_file, "w", encoding="utf-8") as txt_file:
        txt_file.write(formatted_text)

def process_vetos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            input_file = os.path.join(input_folder, file_name)
            output_file = os.path.join(output_folder, file_name.replace(".pdf", ".txt"))
            
            print(f"Processando: {file_name}")
            try:
                veto_data = extract_veto_details(input_file)
                save_as_txt(veto_data, output_file)
                print(f"Salvo: {output_file}")
            except Exception as e:
                print(f"Erro ao processar {file_name}: {e}")

# Uso do script
if __name__ == "__main__":
    input_folder = "../../data/raw/vetos"  # Substitua pelo caminho da pasta com os PDFs
    output_folder = "../../data/extracted/vetos"
    process_vetos(input_folder, output_folder)
