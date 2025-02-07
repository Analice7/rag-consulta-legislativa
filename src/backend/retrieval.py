# Testar a busca de similaridade
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import config

MODEL_EMBEDDINGS = config.MODEL_EMBEDDINGS

embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDINGS)

index_path = "../../data/embeddings/all/"

lista_query = [
    "Qual é a ementa do Projeto de Lei n° 4614?",
    "Qual é a ementa do Projeto de Lei n° 2750?",
    "Qual é a ementa Projeto de Lei do Congresso Nacional n° 3?",
    "Fale sobre a Lei nº 14995",
]

lista_query_prefix = ["query: " + query for query in lista_query]

docsdb = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)

for query in lista_query_prefix:
    #print("--" * 50)
    print(f"\nPergunta: {query}")
    
    docs_scores = docsdb.similarity_search_with_score(query, k=10)
    
    # Ordenar os resultados por score
    lista_docs_ordenada = sorted(docs_scores, key=lambda x: x[1], reverse=True)
    
    for i, (doc, score) in enumerate(lista_docs_ordenada):
        print(f"\t{i+1}) Score: {score:.5f} - Source: {doc.metadata.get('nome_arquivo', 'Não disponível')} - Título: {doc.metadata.get('titulo', 'Não disponível')}")
        #print(f'\nConteúdo: {doc.page_content}\n')
