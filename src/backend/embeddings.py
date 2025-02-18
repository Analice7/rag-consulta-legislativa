import json
import numpy as np
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.preprocessing import normalize
from dotenv import load_dotenv
import config
import os

load_dotenv()

model = config.MODEL_EMBEDDINGS
embeddings = HuggingFaceEmbeddings(model_name=model)
print("Embeddings carregadas com sucesso.")

all_docs = []  

for folder in ['atividade_legislativa', 'leis', 'vetos']:
    try:
        with open(f"../../data/chunkings/{folder}/chunkings.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)

        total_docs = len(chunks)
        print(f"Pasta {folder} contém {total_docs} documentos.")

        all_docs.extend([
            Document(page_content=chunk["chunk"], metadata=chunk["metadata"])
            for chunk in chunks
        ])

    except Exception as e:
        print(f"Erro ao processar {folder}: {e}")

if all_docs:
    print(f"Total de documentos carregados: {len(all_docs)}")
    
    # Gera embeddings uma única vez
    embeddings_matrix = np.array(embeddings.embed_documents([doc.page_content for doc in all_docs]))
    normalized_embeddings = normalize(embeddings_matrix, axis=1, norm='l2')

    # Prepara textos e metadados
    texts = [doc.page_content for doc in all_docs]
    metadatas = [doc.metadata for doc in all_docs]

    # Converte embeddings para listas de floats
    normalized_embeddings_list = normalized_embeddings.tolist()

    # Cria o índice FAISS
    docsdb = FAISS.from_embeddings(
        text_embeddings=list(zip(texts, normalized_embeddings_list)),
        embedding=embeddings,
        metadatas=metadatas
    )

    # Garante que o diretório existe antes de salvar
    save_path = "../../data/embeddings/all/"
    os.makedirs(save_path, exist_ok=True)
    docsdb.save_local(save_path)
    print("Índice FAISS criado e salvo com sucesso.")

    sample_doc = docsdb.similarity_search("teste", k=1)
    print(f"Resultado FAISS: {sample_doc[0].metadata if sample_doc else 'Nenhum resultado encontrado'}")

else:
    print("Nenhum documento foi processado.")
