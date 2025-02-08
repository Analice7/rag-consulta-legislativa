# Integração com LLMs
from backend.retrieval import get_relevant_context

def generate_response(query, client):
    
    # Recuperar documentos mais relevantes
    relevant_docs = get_relevant_context(query)

    for i, (doc, score) in enumerate(relevant_docs):
        print(f"\t{i+1}) Score: {score:.5f} - Source: {doc.metadata.get('nome_arquivo', 'Não disponível')} - Título: {doc.metadata.get('titulo', 'Não disponível')}")
        #print(f'\nConteúdo: {doc.page_content}\n')

    # Criar um contexto com os documentos encontrados
    context_text = "\n\n".join([doc.page_content for doc, score in relevant_docs])

    # Criar o prompt para a LLM
    prompt = f"""
    Você é um assistente especializado em atividade legislativa. Baseie-se nos documentos a seguir para responder à pergunta do usuário.
    
    Documentos:
    {context_text}
    
    Pergunta do usuário:
    {query}
    
    Responda de forma objetiva e técnica.
    """

    # Chamar a API Groq para gerar a resposta
    response = client.chat.completions.create(
        model="llama3-8b-8192",  
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500
    )

    return response.choices[0].message.content
