# 📜 Sistema RAG para Consulta de Atividade Legislativa Brasileira

Este projeto implementa um sistema baseado em **RAG (Retrieval-Augmented Generation)** para permitir consultas inteligentes e atualizadas sobre projetos de lei do Congresso Nacional, utilizando LLMs e técnicas modernas de recuperação semântica de informações.

## 👨‍💻 Desenvolvido por
- Analice da Silva Nascimento  
- José Matheus Nogueira Luciano
- Luís Filipe de Barros Ferreira

## 🎯 Objetivo

Fornecer uma ferramenta capaz de responder a perguntas sobre projetos de lei recentes no Brasil, superando as limitações de LLMs quanto à atualização de dados, por meio da combinação de embeddings semânticos e geração de texto baseada em contexto.

---

## 🧠 Tecnologias e Métodos

- **Embeddings semânticos** via [Hugging Face Transformers](https://huggingface.co)
- **Base vetorial** para recuperação eficiente de documentos relevantes
- **Engenharia de prompts** para melhorar a precisão das respostas
- **LLMs da Groq** para comparação de desempenho
- **Testes metodológicos de chunking**, com variações de tamanho e sobreposição
- **Streamlit** para interface web simples e interativa
- **Framework de avaliação** com métricas para análise da qualidade das respostas

---

## 🚀 Como executar

### 1. Clone o repositório
```bash
https://github.com/Analice7/rag-consulta-legislativa.git
cd rag-consulta-legislativa/src
```

### 2. Instale as dependências
Utilize um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Execute a aplicação
```bash
streamlit run app.py
```

---

## 🧪 Avaliação

Implementamos um framework de avaliação baseado em:
- Precisão das respostas
- Relevância dos documentos recuperados
- Comparação entre diferentes LLMs
- Testes A/B com diferentes estratégias de chunking

---

## 🗂 Fontes dos Dados

Os projetos de lei são extraídos diretamente da base oficial:  
🔗 [https://www.congressonacional.leg.br/materias/ultimas-leis-publicadas](https://www.congressonacional.leg.br/materias/ultimas-leis-publicadas)

---

## 📌 Resultados

- Sistema funcional e preciso, com dados atualizados
- Superação das limitações típicas de LLMs quanto à atualidade das informações
- Identificação de melhores práticas de chunking e recuperação
- Cumprimento dos requisitos técnicos e metodológicos propostos

---

Este projeto foi desenvolvido como parte da disciplina *Tópicos Especiais em Inteligência Artificial*.  
Fique à vontade para abrir issues ou sugestões!

---
