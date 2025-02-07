import json
import numpy as np
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import config

# Criar índice FAISS com embeddings normalizados
def normalize(vecs):
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

load_dotenv()

model = config.MODEL_EMBEDDINGS
embeddings = HuggingFaceEmbeddings(model_name=model)
print("Embeddings carregadas com sucesso.")

all_docs = []

for folder in ['atividade_legislativa', 'leis', 'vetos'] :
    try:
        with open(f"../../data/chunkings/{folder}/chunkings.json", "r", encoding="utf-8") as f:
            all_docs.extend([
                Document(page_content=chunk["chunk"], metadata=chunk["metadata"])
                for chunk in json.load(f)
            ])
        print(f"Pasta {folder} processada com {len(all_docs)} documentos.")
    except Exception as e:
        print(f"Erro ao processar {folder}: {e}")

docsdb = FAISS.from_documents(all_docs, embeddings)
docsdb.save_local("../../data/embeddings/all/")
print("Índice FAISS criado e salvo com sucesso.")

# Teste de busca
sample_doc = docsdb.similarity_search("teste", k=1)
print(f"Resultado FAISS: {sample_doc[0].metadata if sample_doc else 'Nenhum resultado encontrado'}")
