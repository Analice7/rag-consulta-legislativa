from bs4 import BeautifulSoup #Extrai dados do html
import os #Encontra o caminho dos arquivos
import json
import re

def extract_text_from_html(arquivo):
    file_path = os.path.join(directory, arquivo)  # Usar os.path.join para construir o caminho
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read() #Lê o arquivo html
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return None
    
    soup = BeautifulSoup(content, 'html.parser')
    
    titulo = soup.find('span', class_='Epigrafecaractere', string=lambda text: text and text.startswith("LEI")).get_text()
    if titulo:
        titulo = titulo.replace(".",'')
    
    pattern = r'\d+[\.,]+\d+'
    
    descricao = soup.find('p', class_='Ementaparagrafo').get_text()
    descricao = descricao.replace(descricao[0], descricao[0].lower())
    descricao = re.sub(pattern, lambda m:m.group().replace('.',''), descricao)

    lei_texto_aux1 = soup.find_all('p', class_='DefaultParagraph') #Encontra todos os paragrafos relevantes
    
    if lei_texto_aux1:
        lei_texto_aux2 = [p.get_text() for p in lei_texto_aux1] #Retira tags restantes
        lei_texto = '\n'.join(lei_texto_aux2) #Transforma em string
        lei_texto = lei_texto.replace("(NR)", "")
        lei_texto = lei_texto.replace("\n", "")
        lei_texto = lei_texto.replace("art.", "artigo")
        lei_texto = lei_texto.replace("Art.", "Artigo")
        lei_texto = lei_texto.replace("arts.", "artigos")
        lei_texto = lei_texto.replace("§", "parágrafo")
        lei_texto = lei_texto.replace("..", "")
        lei_texto = re.sub(pattern, lambda m:m.group().replace('.',''), lei_texto)
    else:
        lei_texto = None
        
    if arquivo[1] == 'C':
       link = f'https://www.planalto.gov.br/ccivil_03/leis/lcp/{arquivo[:-5]}.htm'
    else:
       link = f'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/{arquivo[:-5]}.htm'
       
    output_directory = "data/extracted/leis"
    os.makedirs(output_directory, exist_ok=True) #Verifica se o diretorio existe
    
    with open(f"data/extracted/leis/{arquivo[:-5]}.txt", "w", encoding="utf-8") as txt_file:
        txt_file.write('{0}.\nA lei {1}\n{2}\n{3}'.format(titulo, descricao, lei_texto, link))
        print(f"salvo! {arquivo[:-5]}")    
    
if __name__ == "__main__":
    directory = "data/raw/leis"
    extension = ".html"

    for arquivo in os.listdir(directory):
        if arquivo.endswith(extension):
            extract_text_from_html(arquivo)
            