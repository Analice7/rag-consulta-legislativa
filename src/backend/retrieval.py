# Testar a busca de similaridade
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend import config
from pathlib import Path

def get_relevant_context(query):

    MODEL_EMBEDDINGS = config.MODEL_EMBEDDINGS

    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDINGS)

    destino = Path(__file__).parent.parent.parent / "data" / "embeddings" / "all"
    index_path = os.path.relpath(destino, Path.cwd())

    docsdb = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)

    print(f"\nPergunta: {query}")
    
    docs_scores = docsdb.similarity_search_with_score(query, k=20)
    
    # Ordenar os resultados por score
    lista_docs_ordenada = sorted(docs_scores, key=lambda x: x[1], reverse=True)

    return lista_docs_ordenada
    
