import streamlit as st
import os
from dotenv import load_dotenv
import groq
from backend.models import generate_response

# Carregar variáveis do .env
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)
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

    # Criar o histórico formatado para a LLM
    historico = [
        {"role": "user" if m["tipo"] == "user" else "assistant", "content": m["conteudo"]}
        for m in st.session_state.mensagens
    ]

    # Exibir indicador de carregamento
    with st.spinner("Buscando informações legislativas..."):
        # Obter resposta da RAG considerando o histórico
        resposta = generate_response(historico, client)

    # Exibir a resposta na interface
    with st.chat_message("assistant"):
        st.markdown(resposta)

    st.session_state.mensagens.append({"tipo": "assistant", "conteudo": resposta})

# Separador
st.markdown("---")

# Layout com duas colunas para o texto e o botão
col1, col2 = st.columns([6, 1])

with col1:
    st.caption("Desenvolvido para o projeto de RAG da disciplina de Tópicos Especiais em Inteligência Artificial.")

with col2:
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.mensagens = []
        st.rerun()
