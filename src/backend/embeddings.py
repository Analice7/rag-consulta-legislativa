import json
import numpy as np
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.preprocessing import normalize
from dotenv import load_dotenv
import config

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
    
    embeddings_matrix = np.array(embeddings.embed_documents([doc.page_content for doc in all_docs]))
    normalized_embeddings = normalize(embeddings_matrix, axis=1, norm='l2')

    docsdb = FAISS.from_documents(all_docs, embeddings)

    docsdb.save_local("../../data/embeddings/all/")
    print("Índice FAISS criado e salvo com sucesso.")

    sample_doc = docsdb.similarity_search("teste", k=1)
    print(f"Resultado FAISS: {sample_doc[0].metadata if sample_doc else 'Nenhum resultado encontrado'}")

else:
    print("Nenhum documento foi processado.")
