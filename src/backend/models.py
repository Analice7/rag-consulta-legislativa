# Integração com LLMs
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_huggingface import HuggingFaceEmbeddings

def load_models():
    """
    Carrega os modelos de embeddings e de linguagem natural.
    """
    embedding_model = HuggingFaceEmbeddings(model_name="FacebookAI/roberta-base")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    return embedding_model, tokenizer, model

def generate_response(prompt, relevant_context, tokenizer, model):
    """
    Gera uma resposta para o prompt com base no contexto relevante.
    """
    final_prompt = (
        f"Você é um assistente jurídico especializado em atividade legislativa.\n\n"
        f"Com base no contexto abaixo, responda de forma objetiva e clara à pergunta do usuário.\n\n"
        f"Contexto relevante: {relevant_context}\n\n"
        f"Pergunta: {prompt}\n\n"
        f"Resposta:"
    )
    inputs = tokenizer(final_prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=512,
        num_beams=5,
        early_stopping=True,
        no_repeat_ngram_size=2,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

