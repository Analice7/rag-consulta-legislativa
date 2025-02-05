import json
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
import config

# Carregar variáveis de ambiente
load_dotenv()

huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
huggingfacehub_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')

# Lista de pastas a serem processadas
folder_list = ['atividade_legislativa', 'leis', 'vetos'] 

# Modelo de embeddings
model = config.MODEL_EMBEDDINGS

# Lista para armazenar todos os documentos
all_docs = []

# Processar cada pasta na lista
for folder in folder_list:
    # Caminho para o arquivo de chunkings
    chunking_file = f"../../data/chunkings/{folder}/chunkings.json"
    
    # Carregar chunkings em JSON e transformar em objetos Document
    try:
        with open(chunking_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        
        docs = [
            Document(
                page_content=chunk["chunk"],
                metadata=chunk["metadata"]
            ) for chunk in chunks
        ]
        
        print(f"Exemplo de documento criado da pasta {folder}: {docs[0] if docs else 'Nenhum documento criado'}")
        
        # Adicionar os documentos da pasta à lista geral
        all_docs.extend(docs)
        
        print(f"Total de documentos na pasta {folder}: {len(docs)}")
    
    except Exception as e:
        print(f"Erro ao processar a pasta {folder}: {e}")

# Agora que todos os documentos estão na lista all_docs, criamos o índice FAISS

# Caminho para salvar o índice FAISS
index_path = "../../data/embeddings/all/"

# Garantir que o diretório existe
os.makedirs(os.path.dirname(index_path), exist_ok=True)

# Criar o índice FAISS com as embeddings geradas
batch_size = 100
embeddings = HuggingFaceEmbeddings(model_name=model)
print("Embeddings carregadas com sucesso.")

docsdb = None

for i in range(0, len(all_docs), batch_size):
    batch = all_docs[i:i+batch_size]
    batch_db = FAISS.from_documents(batch, embeddings)
    
    if docsdb is None:
        docsdb = batch_db
    else:
        docsdb.merge_from(batch_db)

print("Índice FAISS criado com sucesso.")

# Salvar o índice FAISS
docsdb.save_local(index_path)
print(f"Índice FAISS salvo em {index_path}.")

# Testar a busca de similaridade
sample_doc = docsdb.similarity_search("teste", k=1)
print(f"Exemplo de resultado FAISS: {sample_doc[0].metadata if sample_doc else 'Nenhum resultado encontrado'}")

