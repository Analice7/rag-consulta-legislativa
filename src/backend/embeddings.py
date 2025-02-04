import json
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import json
import os
import torch
from transformers import AutoModel, AutoTokenizer

# Carregar variáveis de ambiente
load_dotenv()

huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
huggingfacehub_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')

# Caminho para o arquivo de chunkings
folder_list = ['atividade_legislativa']
#, 'leis', 'vetos'
for folder in folder_list:
    chunking_file = f"../../data/chunkings/{folder}/chunkings.json"

model = "WhereIsAI/UAE-Large-V1"

# Carregar chunkings em JSON e transformar em objetos Document
with open(chunking_file, "r", encoding="utf-8") as f:
    chunks = json.load(f)

docs = [
    Document(
        page_content=chunk["chunk"],
        metadata=chunk["metadata"]
    ) for chunk in chunks
]

print(f"Exemplo de documento criado: {docs[0] if docs else 'Nenhum documento criado'}")

print("OK")

# Caminho para salvar/carregar o índice FAISS
for folder in folder_list:
    index_path = f"../../data/embeddings/{folder}/index.faiss"

print("OK")

# Garantir que o diretório existe
os.makedirs(os.path.dirname(index_path), exist_ok=True)

print("Criando um novo índice FAISS...")

print(f"Total de documentos: {len(docs)}")


# Criar o índice FAISS com as embeddings geradas
try:
    batch_size = 16  # Ajuste conforme necessário

    embeddings = HuggingFaceEmbeddings(model_name=model)
    print("OK")

    docsdb = None

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        batch_db = FAISS.from_documents(batch, embeddings)
        
        if docsdb is None:
            docsdb = batch_db
        else:
            docsdb.merge_from(batch_db)

    print("OK")

    docsdb.save_local(index_path)
    print("Índice FAISS criado e salvo com sucesso.")

    sample_doc = docsdb.similarity_search("teste", k=1)
    print(f"Exemplo de resultado FAISS: {sample_doc[0].metadata if sample_doc else 'Nenhum resultado encontrado'}")

except Exception as e:
    print(f"Erro ao criar índice FAISS: {e}")