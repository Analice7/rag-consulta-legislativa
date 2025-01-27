import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sklearn.metrics.pairwise import cosine_similarity
import json
from transformers import AutoModel, AutoTokenizer

model_name = "nlpaueb/legal-bert-base-uncased"
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Função de recuperação de contexto
def rerank_documents(question, retrieved_docs, top_n=5):
    """
    Reordena os documentos recuperados com base na similaridade com a questão.

    Parâmetros:
    - question (str): A questão feita pelo usuário.
    - retrieved_docs (list): Lista de documentos recuperados.
    - top_n (int): Número de documentos mais relevantes a retornar.

    Retorna:
    - list: Lista com os documentos reordenados por relevância.
    """
    # Gerando embedding para a questão
    inputs = tokenizer(question, return_tensors='pt', truncation=True, padding=True)
    question_embedding = model(**inputs).last_hidden_state.mean(dim=1).detach().numpy()

    # Acessando o conteúdo dos documentos diretamente
    doc_contents = [doc.page_content for doc in retrieved_docs]
    
    # Gerando embeddings para os documentos
    doc_embeddings = [model(**tokenizer(content, return_tensors='pt', truncation=True, padding=True)).last_hidden_state.mean(dim=1).detach().numpy() for content in doc_contents]
    
    # Calculando similaridade entre a questão e os documentos
    similarities = cosine_similarity(question_embedding, np.array(doc_embeddings).squeeze())[0]
    
    ranked_indices = np.argsort(similarities)[::-1]  # Ordena pela similaridade em ordem decrescente
    ranked_docs = [retrieved_docs[i] for i in ranked_indices[:top_n]]
    return ranked_docs

# Caminhos para os arquivos necessários
index_path = "../../data/embeddings/atividade_legislativa/index.faiss"
chunking_file = "../../data/chunkings/atividade_legislativa/chunkings.json"

# Carregar os textos do arquivo de chunkings
with open(chunking_file, "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [chunk["chunk"] for chunk in chunks]

# Carregar o modelo de embeddings
embedding_model = HuggingFaceEmbeddings(model_name="nlpaueb/legal-bert-base-uncased")

# Carregar o índice FAISS
docsdb = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)

query = "Qual é a explicação da ementa da Medida Provisória n° 1243, de 2024"

# Recuperar os documentos do índice usando o retriever
retriever = docsdb.as_retriever(search_type="similarity", search_kwargs={"k": 10})
retrieved_docs = retriever.invoke(query)

# Reordenar os documentos recuperados
ranked_docs = rerank_documents(query, retrieved_docs, top_n=5)

# Exibir o contexto relevante
print("Contexto relevante:")
for doc in ranked_docs:
    print(doc.page_content)

