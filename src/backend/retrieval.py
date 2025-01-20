# Funções de recuperação de informações
import numpy as np

def get_relevant_context(query, index, texts, embedding_model, k=5):
    query_embedding = np.array(embedding_model.embed_query(query)).astype('float32').reshape(1, -1)
    D, I = index.search(query_embedding, k=10)

    relevant_texts = [texts[i] for i in I[0]]
    unique_texts = list(dict.fromkeys(relevant_texts))  
    return " ".join(unique_texts[:k]) 
