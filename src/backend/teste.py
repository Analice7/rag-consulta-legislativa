from retrieval import get_relevant_context
import os
import groq
from dotenv import load_dotenv
from models import generate_response

# Carregar variáveis do .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Criar o cliente da API Groq
client = groq.Client(api_key=GROQ_API_KEY)

# Teste de consulta
query = "Fale sobre a Lei 15082?"
response = generate_response(query, client)

print("\n🔍 Resposta da IA:\n", response)
