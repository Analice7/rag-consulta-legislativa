import json
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import json
import os

# Carregar variáveis de ambiente
load_dotenv()

huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
huggingfacehub_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')

# Caminho para o arquivo de chunkings
folder_list = ['atividade_legislativa', 'leis']
for folder in folder_list:
    chunking_file = f"data/chunkings/{folder}/chunkings.json"

# Carregar chunkings em JSON e transformar em objetos Document
with open(chunking_file, "r", encoding="utf-8") as f:
    chunks = json.load(f)

docs = [
    Document(
        page_content=chunk["chunk"],
        metadata=chunk["metadata"]
    ) for chunk in chunks
]

# Caminho para salvar/carregar o índice FAISS
for folder in folder_list:
    index_path = f"data/embeddings/{folder}/index.faiss"

# Garantir que o diretório existe
os.makedirs(os.path.dirname(index_path), exist_ok=True)

print("Criando um novo índice FAISS...")

docsdb = FAISS.from_documents(docs, HuggingFaceEmbeddings(model_name="nlpaueb/legal-bert-base-uncased"))
docsdb.save_local(index_path)

print("Índice FAISS criado e salvo com sucesso.")