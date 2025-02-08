import streamlit as st
import os
from dotenv import load_dotenv
import groq
from retrieval import get_relevant_context
from models import generate_response

# Carregar variáveis do .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Criar o cliente da API Groq
client = groq.Client(api_key=GROQ_API_KEY)

# Configuração da página
st.set_page_config(page_title="Atividade Legislativa - RAG", layout="wide")
st.title("⚖️ Chat Atividade Legislativa")

st.markdown("Este chatbot foi desenvolvido para auxiliar na consulta de atividades legislativas. Pergunte sobre as últimas leis aprovadas, ementas e outras informações jurídicas.")

# Inicializar histórico de mensagens
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibir mensagens anteriores
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["tipo"]):
        st.markdown(mensagem["conteudo"])

# Campo de entrada do usuário
pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    # Exibir a pergunta na interface
    st.chat_message("user").markdown(pergunta)
    st.session_state.mensagens.append({"tipo": "user", "conteudo": pergunta})

    # Obter resposta da RAG
    resposta = generate_response(pergunta, client)

    # Exibir a resposta na interface
    with st.chat_message("assistant"):
        st.markdown(resposta)

    st.session_state.mensagens.append({"tipo": "assistant", "conteudo": resposta})

st.markdown("---")
st.caption("Desenvolvido para o projeto de RAG da disciplina de Tópicos Especiais em Inteligência Artificial.")
