# Testar a busca de similaridade
import os
import sys
import backend.config as config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sklearn.metrics.pairwise import cosine_similarity
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path

def calcular_similaridade(query, categorias, embedding_model):
    query_embedding = embedding_model.embed_query(query)
    similaridades = {}
    for categoria in categorias:
        categoria_embedding = embedding_model.embed_query(categoria)
        similaridade = cosine_similarity([query_embedding], [categoria_embedding])[0][0]
        similaridades[categoria] = similaridade
    return similaridades

def get_relevant_context(query, k=30):
    MODEL_EMBEDDINGS = config.MODEL_EMBEDDINGS
    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDINGS)

    index_path = "../data/embeddings_separados/"

    docsal = FAISS.load_local(index_path + "atividade_legislativa/", embedding_model, allow_dangerous_deserialization=True)
    docsl = FAISS.load_local(index_path + "leis/", embedding_model, allow_dangerous_deserialization=True)
    docsv = FAISS.load_local(index_path + "vetos/", embedding_model, allow_dangerous_deserialization=True)

    categorias = ['vetos', 'veto', 'leis', 'lei', 'atividade legislativa', 'projeto de lei', 'tramitação']
    similaridades = calcular_similaridade(query, categorias, embedding_model)
    
    total_score_al = (similaridades['atividade legislativa'] + similaridades['projeto de lei'] + similaridades['tramitação'])/3
    total_score_l = (similaridades['leis'] + similaridades['lei'])/2
    total_score_v = (similaridades['vetos'] + similaridades['veto'])/2
    
    total_score = total_score_al + total_score_l + total_score_v

    perc_atividade_legislativa = (total_score_al / total_score) if total_score else 1/3
    perc_leis = (total_score_l / total_score) if total_score else 1/3
    perc_vetos = (total_score_v / total_score) if total_score else 1/3
    
    print(f'porc. da al: {perc_atividade_legislativa}\nporc. da lei: {perc_leis}\nporc dos vetos: {perc_vetos}')

    # Calculando quantos documentos recuperar de cada categoria
    k_al = int(perc_atividade_legislativa * k)
    k_l = int(perc_leis * k)
    k_v = int(perc_vetos * k)

    # Recuperando os documentos conforme os valores calculados
    score_al = docsal.similarity_search_with_score(query, k=k_al) if k_al > 0 else []
    score_l = docsl.similarity_search_with_score(query, k=k_l) if k_l > 0 else []
    score_v = docsv.similarity_search_with_score(query, k=k_v )if k_v > 0 else []

    # Juntando os resultados
    results = score_al + score_l + score_v
    return results

def get_relevant_context_simplificado(query):

    MODEL_EMBEDDINGS = config.MODEL_EMBEDDINGS

    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDINGS)

    destino = Path(__file__).parent.parent.parent / "data" / "embeddings" / "all"
    index_path = os.path.relpath(destino, Path.cwd())

    docsdb = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)

    print(f"\nPergunta: {query}")
    
    docs_scores = docsdb.similarity_search_with_score(query, k=30)
    
    # Ordenar os resultados por score
    lista_docs_ordenada = sorted(docs_scores, key=lambda x: x[1], reverse=True)

    return lista_docs_ordenada