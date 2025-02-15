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

# Consulta
query = "Qual é a ementa do Projeto de Lei do Congresso Nacional n° 3, de 2024?"

# Embedding da consulta
query_embedding = embedding_model.embed_query(query)

# Documentos relevantes (ground_truth)
documentos = [
    {
        "chunk": "Atividade legislativa: Projeto de Lei do Congresso Nacional n° 3, de 2024 Autoria: Presidência da República Ementa: Dispõe sobre as diretrizes para a elaboração e a execução da Lei Orçamentária de 2025 e dá outras providências (alteração proposta pela Mensagem presidencial nº 983/2024).",
        "metadata": {
            "titulo": "Projeto de Lei do Congresso Nacional n° 3, de 2024",
            "nome_arquivo": "PLN-3-2024-ATIVIDADE",
            "tipo": "Atividade legislativa"
        }
    },
    {
        "chunk": "Documento: EMENDA 10 - PLN 3/2024     Data: 13/06/2024     Autor: Atividade Legislativa     Local: Comissão Mista de Planos, Orçamentos Públicos e Fiscalização     Ação legislativa: Não disponível     Descrição/ementa: Na Parte Especial do Parecer Preliminar ao PL nº 3/2024, no item 2.2.2, dê-se a seguinte alteração para a seguinte redação: Para a elaboração do Anexo de Prioridades e Metas, serão incluídas pela Relatoria, em decorrência da aprovação de emendas: a) até 3 (três) ações por bancada estadual; b) até 3 (três) ações de interesse nacional por comissão permanente indicada no item 2.3.1 que apresentar emenda; c) até 20 (quinze) ações de interesse nacional propostas por autores individuais, considerando o mérito e a frequência de apresentação; d) até 1(uma) ação por relator setorial.",
        "metadata": {
            "titulo": "Projeto de Lei do Congresso Nacional n° 3, de 2024",
            "nome_arquivo": "PLN-3-2024-ATIVIDADE",
            "tipo": "Atividade legislativa"
        }
    },
    {
        "chunk": "Documento: EMENDA 11 - PLN 3/2024     Data: 13/06/2024     Autor: Deputado Federal Yury do Paredão (MDB/CE)     Local: Comissão Mista de Planos, Orçamentos Públicos e Fiscalização     Ação legislativa: Não disponível     Descrição/ementa: Na Parte Especial do Parecer Preliminar ao PL nº 3/2024, no item 2.2.2, dê-se a seguinte alteração para a seguinte redação: A apresentação de emendas para inclusão de ações orçamentárias no Anexo de Prioridades e Metas deve observar os seguintes limites: a) até 03 (três) emendas por bancada estadual; b) até 03 (três) emendas por comissão permanente do Senado Federal e da Câmara dos Deputados; c) até 03 (três) emendas por parlamentar; d) até 01 (uma) emenda por relator setorial",
        "metadata": {
            "titulo": "Projeto de Lei do Congresso Nacional n° 3, de 2024",
            "nome_arquivo": "PLN-3-2024-ATIVIDADE",
            "tipo": "Atividade legislativa"
        }
    },{
        "chunk": "Documento: EMENDA 24 - PLN 3/2024     Data: 14/06/2024     Autor: Deputado Federal Domingos Sávio (PL/MG)     Local: Comissão Mista de Planos, Orçamentos Públicos e Fiscalização     Ação legislativa: Não disponível     Descrição/ementa: Texto da emenda Altere-se item 2.2.2 da Parte Especial do Relatório Preliminar ao Projeto de Lei do Congresso Nacional nº 03/2024 (PLDO 2025): 2.2.2. A apresentação de emendas para inclusão de ações orçamentárias no Anexo de Prioridades e Metas deve observar os seguintes limites: a) até 3 (três) emendas por bancada estadual; b) até 3 (três) emendas por comissão permanente do Congresso Nacional e de suas Casas; e c) até 3 (três) emendas por parlamentar.",
        "metadata": {
            "titulo": "Projeto de Lei do Congresso Nacional n° 3, de 2024",
            "nome_arquivo": "PLN-3-2024-ATIVIDADE",
            "tipo": "Atividade legislativa"
        }
    }
]

# Mapear documentos para índices no banco de dados FAISS
ground_truth_indices = []
for doc in documentos:
    # Gerar embedding do documento
    doc_embedding = embedding_model.embed_query(doc["chunk"])
    # Buscar o índice do documento no banco de dados FAISS
    _, idx = docsdb.index.search(np.array([doc_embedding]), 1)
    ground_truth_indices.append(idx[0][0])

# Calcular as métricas
precisao = precisao_at_k(query_embedding, ground_truth_indices, k=5)
print(f"\nPrecisão@5: {precisao:.4f}")

recall = recall_at_k(query_embedding, ground_truth_indices, k=5)
print(f"\nRecall@5: {recall:.4f}")

mrr = mean_reciprocal_rank(query_embedding, ground_truth_indices, k=10)
print(f"\nMRR@10: {mrr:.4f}")

ndcg = ndcg_at_k(query_embedding, ground_truth_indices, k=10)
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
