from bs4 import BeautifulSoup #Extrai dados do html
import os #Encontra o caminho dos arquivos
import json

def extract_text_from_html(arquivo):
    file_path = os.path.join(directory, arquivo)  # Usar os.path.join para construir o caminho
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read() #Lê o arquivo html
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return None
    
    soup = BeautifulSoup(content, 'html.parser')
    
    titulo = soup.find('span', class_='Epigrafecaractere', string=lambda text: text and text.startswith("LEI"))
    descricao = soup.find('p', class_='Ementaparagrafo')
    lei_texto_aux1 = soup.find_all('p', class_='DefaultParagraph') #Encontra todos os paragrafos relevantes
    
    if lei_texto_aux1:
        lei_texto_aux2 = [p.get_text() for p in lei_texto_aux1] #Retira tags restantes
        lei_texto = '\n'.join(lei_texto_aux2) #Transforma em string
        lei_texto = lei_texto.replace("(NR)", "")
    else:
        lei_texto = None
        
    if arquivo[1] == 'C':
       link = f'https://www.planalto.gov.br/ccivil_03/leis/lcp/{arquivo[:-5]}.htm'
    else:
       link = f'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/{arquivo[:-5]}.htm'
    
    
    dados_extracao = {
        'lei': titulo.get_text() if titulo else None,
        'ementa': descricao.get_text() if descricao else None, 
        'texto': lei_texto,
        'link': link
    }
    
    output_directory = "data/extracted/leis"
    os.makedirs(output_directory, exist_ok=True) #Verifica se o diretorio existe
    
    with open(f"data/extracted/leis/{arquivo[:-5]}.json", "w", encoding="utf-8") as json_file:
        json.dump(dados_extracao, json_file, ensure_ascii=False, indent=4)
        print(f"salvo! {arquivo[:-5]}")
    
if __name__ == "__main__":
    directory = "data/raw/leis"
    extension = ".html"

    for arquivo in os.listdir(directory):
        if arquivo.endswith(extension):
            extract_text_from_html(arquivo)
            