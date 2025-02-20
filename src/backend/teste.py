import os
import groq
from dotenv import load_dotenv
from models import generate_response

# Carregar variáveis do .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Criar o cliente da API Groq
client = groq.Client(api_key=GROQ_API_KEY)

# Inicializar histórico de mensagens
test_historico = [
    {"role": "user", "content": "Qual é a ementa da PLN 3?"}
]

# Teste de consulta
response = generate_response(test_historico, client)

print("\n🔍 Resposta da IA:\n", response)
