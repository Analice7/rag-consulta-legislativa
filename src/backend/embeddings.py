from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import numpy as np
import json

def concatenar(dados, nivel=0):

    texto = ""
    indentacao = "  " * nivel

    if isinstance(dados, dict):
        for chave, valor in dados.items():
            texto += f"{indentacao}{chave.capitalize()}: "
            if isinstance(valor, (dict, list)):
                texto += "\n" + concatenar(valor, nivel + 1)
            else:
                texto += f"{valor}\n"
    elif isinstance(dados, list):
        for item in dados:
            texto += concatenar(item, nivel + 1)
    else:
        texto += f"{indentacao}{dados}\n"

    return texto

def embeddings(sentences):
    #Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

    print("Sentence embeddings:")
    print(sentence_embeddings)

    return sentence_embeddings

if __name__ == '__main__':
    with open('../../data/extracted/atividade_legislativa/PLN-15-2024-ATIVIDADE.json', 'r', encoding='utf-8') as file:
        dados = json.load(file)

        # Concatenar
        texto_concatenado = concatenar(dados)

        print(f'{texto_concatenado}')

        sentences = texto_concatenado.split("\n")

        # Gerar embeddings
        embedding = embeddings(sentences)

        # Salvar embeddings
        np.save('../../data/embeddings/embedding.npy', embedding.numpy())

        print("Embeddings gerados e salvos em 'embedding.npy'.")