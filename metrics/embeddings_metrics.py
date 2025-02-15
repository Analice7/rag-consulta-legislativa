from langchain_community.vectorstores import FAISS
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from langchain_huggingface import HuggingFaceEmbeddings
import config

# Precisão@K
def precisao_at_k(query_embedding, ground_truth_index, k=5):
    _, indices_pred = docsdb.index.search(np.array([query_embedding]), k)
    return np.mean([1 if i in ground_truth_index else 0 for i in indices_pred[0]])

# Recall@K
def recall_at_k(query_embedding, ground_truth_index, k=5):
    _, indices_pred = docsdb.index.search(np.array([query_embedding]), k)
    return len(set(indices_pred[0]) & set(ground_truth_index)) / len(ground_truth_index)

# MRR (Mean Reciprocal Rank)
def mean_reciprocal_rank(query_embedding, ground_truth_index, k=10):
    _, indices_pred = docsdb.index.search(np.array([query_embedding]), k)
    for rank, idx in enumerate(indices_pred[0], start=1):
        if idx in ground_truth_index:
            return 1 / rank
    return 0 

# NDCG (Normalized Discounted Cumulative Gain)
def dcg_at_k(relevances, k):
    relevances = np.array(relevances)[:k]
    return np.sum(relevances / np.log2(np.arange(2, len(relevances) + 2)))

def ndcg_at_k(query_embedding, ground_truth_index, k=10):
    _, indices_pred = docsdb.index.search(np.array([query_embedding]), k)
    
    # Criar vetor de relevância (1 se relevante, 0 se irrelevante)
    relevances = [1 if idx in ground_truth_index else 0 for idx in indices_pred[0]]
    
    dcg = dcg_at_k(relevances, k)
    ideal_relevances = sorted(relevances, reverse=True)  # Ideal DCG (IDCG)
    idcg = dcg_at_k(ideal_relevances, k)
    
    return dcg / idcg if idcg > 0 else 0

# Main:

embedding_model = config.MODEL_EMBEDDINGS
embedding_model = HuggingFaceEmbeddings(model_name=embedding_model)

docsdb = FAISS.load_local("../data/embeddings/all/", embedding_model, allow_dangerous_deserialization=True) 

d = docsdb.index.d 
print(f'\nDimensão dos embeddings: {d}')

n_vetores = docsdb.index.ntotal
print(f'\nNúmero de vetores: {n_vetores}')

# Amostrar embeddings
indices_amostra = np.random.choice(n_vetores, n_vetores, replace=False)
embeddings_amostra = np.array([docsdb.index.reconstruct(int(i)) for i in indices_amostra])

# Medir Similaridade Cosseno
similaridades = cosine_similarity(embeddings_amostra)
media_similaridade = np.mean(similaridades)

print(f"\nSimilaridade Cosseno: {media_similaridade:.4f}")

# Medir Distância Euclidiana Média
pares = np.random.choice(n_vetores, (n_vetores, 2), replace=True)
distancias = np.linalg.norm(embeddings_amostra[pares[:, 0]] - embeddings_amostra[pares[:, 1]], axis=1)
media_distancia = np.mean(distancias)

print(f"\nDistância Euclidiana Média: {media_distancia:.4f}")

# Selecionar um vetor de consulta aleatório
query_idx = np.random.randint(0, docsdb.index.ntotal)
query_embedding = docsdb.index.reconstruct(query_idx)

# Buscar os 5 documentos mais próximos do vetor de consulta (ground truth)
_, ground_truth = docsdb.index.search(np.array([query_embedding]), 5)
ground_truth = ground_truth[0] 

# Remover o índice do vetor de consulta de ground_truth (para evitar coincidência)
ground_truth = [idx for idx in ground_truth if idx != query_idx]

# Caso o número de documentos relevantes para ground_truth seja menor que 5,
# selecionar outros índices aleatórios do banco de dados
# while len(ground_truth) < 5:
#     random_idx = np.random.randint(0, docsdb.index.ntotal)
#     if random_idx != query_idx and random_idx not in ground_truth:
#         ground_truth.append(random_idx)

# Calcular as métricas
precisao = precisao_at_k(query_embedding, ground_truth, k=5)
print(f"\nPrecisão@5: {precisao:.4f}")

recall = recall_at_k(query_embedding, ground_truth, k=5)
print(f"\nRecall@5: {recall:.4f}")

mrr = mean_reciprocal_rank(query_embedding, ground_truth, k=10)
print(f"\nMRR@10: {mrr:.4f}")

ndcg = ndcg_at_k(query_embedding, ground_truth, k=10)
print(f"\nNDCG@10: {ndcg:.4f}")

# t-SNE para Visualização dos Embeddings
# tsne = TSNE(n_components=2, perplexity=30, random_state=42)
# embeddings_2d = tsne.fit_transform(embeddings_amostra)

# # Clusterização para verificar agrupamentos naturais
# num_clusters = 10
# kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
# labels = kmeans.fit_predict(embeddings_amostra)

# plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], c=labels, cmap='tab10', alpha=0.7)
# plt.title(f"Clusterização dos Embeddings ({num_clusters} Clusters)")
# plt.show()