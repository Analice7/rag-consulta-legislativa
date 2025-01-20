# main.py
import streamlit as st
import numpy as np
import faiss
from backend.retrieval import get_relevant_context
from backend.models import load_models, generate_response

@st.cache_resource
def load_faiss_index():
    index = faiss.read_index("../data/embeddings/index.faiss")
    texts = np.load("../data/embeddings/texts.npy", allow_pickle=True)
    return index, texts

if __name__ == "__main__":
    
    st.title("RAG para consulta de Atividade Legislativa")
    vectorstore, texts = load_faiss_index()
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Carregar os modelos
    embedding_model, tokenizer, model = load_models()

    if prompt := st.text_input("Digite sua pergunta:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        # Obter o contexto relevante
        relevant_context = get_relevant_context(prompt, vectorstore, texts, embedding_model)
        
        # Limitar o tamanho do contexto
        max_context_length = 300
        if len(relevant_context.split()) > max_context_length:
            relevant_context = " ".join(relevant_context.split()[:max_context_length])
        st.write(f"Contexto relevante ({len(relevant_context.split())} palavras): {relevant_context}")

        # Gerar a resposta
        response = generate_response(prompt, relevant_context, tokenizer, model)
        
        st.chat_message("assistant").markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
