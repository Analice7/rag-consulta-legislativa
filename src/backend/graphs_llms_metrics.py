import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

arq = "avaliacao_geral_llms.csv"

try:
    df = pd.read_csv(arq, encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(arq, encoding="latin1", errors="replace")

df.columns = [
    "Modelo",
    "Tempo Médio de Resposta",
    "BERTScore Médio",
    "Precisão Média",
    "Relevância Média",
    "Clareza Média",
    "Completude Média"
]

# Gráfico de BERTScore médio
plt.figure(figsize=(8, 5))  # Deixando o gráfico um pouco mais estreito
sns.barplot(x="Modelo", y="BERTScore Médio", data=df, hue="Modelo", palette="viridis", dodge=False)
plt.xticks(rotation=0, ha='center')
plt.xlabel("Modelo")
plt.ylabel("BERTScore Médio")
plt.title("BERTScore Médio por Modelo")
plt.show()

# Gráfico de Tempo Médio de Resposta
plt.figure(figsize=(8, 5))  # Deixando o gráfico um pouco mais estreito
sns.barplot(x="Modelo", y="Tempo Médio de Resposta", data=df, hue="Modelo", palette="magma", dodge=False)
plt.xticks(rotation=0, ha='center')
plt.xlabel("Modelo")
plt.ylabel("Tempo Médio de Resposta (s)")
plt.title("Tempo Médio de Resposta por Modelo")
plt.show()

# Gráfico Radar para Precisão, Relevância, Clareza e Completude
labels = ["Precisão Média", "Relevância Média", "Clareza Média", "Completude Média"]
num_vars = len(labels)

def plot_radar_chart(df):
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Fechar o gráfico
    
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    
    # Para cada linha do DataFrame, pegar o maior valor de cada questão e marcar somente esses
    for i, row in df.iterrows():
        values = [row[label] for label in labels]
        values += values[:1]  # Fechar o gráfico
        ax.plot(angles, values, label=row["Modelo"], linewidth=2)
        ax.fill(angles, values, alpha=0.2)
        
        # Adicionando os valores máximos de cada categoria
        for j, label in enumerate(labels):
            if row[label] == max(df[label]):
                ax.text(angles[j], row[label] + 0.1, str(round(row[label], 2)), horizontalalignment='center', size=10)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12)
    
    # Marcas de 1 a 5
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([1, 2, 3, 4, 5])
    
    plt.title("Qualidade da Avaliação Humana dos Modelos", size=14, pad=20)
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.show()

plot_radar_chart(df)
