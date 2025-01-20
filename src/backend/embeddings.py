#from transformers import AutoTokenizer, AutoModel
from transformers import RobertaTokenizer, RobertaModel
import torch
import torch.nn.functional as F
import numpy as np
import json
import faiss

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
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    model = RobertaModel.from_pretrained('roberta-base')
    
    # Tokenize sentences
    encoded_input = tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=512)

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

        #print(f'{texto_concatenado}')

        sentences = texto_concatenado.split("\n")
        np.save("../../data/embeddings/texts.npy", sentences)

        # Gerar embeddings
        embedding = embeddings(sentences)

        # Salvar embeddings
        np.save('../../data/embeddings/embedding.npy', embedding.numpy())

        print("Embeddings gerados e salvos em 'embedding.npy'.")

        # Crie um novo índice FAISS
        dim = embedding.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embedding)

        # Salve o índice
        faiss.write_index(index, "../../data/embeddings/index.faiss")