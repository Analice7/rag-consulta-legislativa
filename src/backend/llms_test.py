import time
import pandas as pd
import groq
from dotenv import load_dotenv
import os
from bert_score import score
from models import generate_response
import config
import csv

# Carregar variáveis do .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Criar o cliente da API Groq
client = groq.Client(api_key=GROQ_API_KEY)

# Conjunto de perguntas para teste
test_questions = [
    # Arquivos de Leis
    # Consultas diretas
    "O que diz a lei nº 15051 de 2024?",
    "Qual é o artigo 1º da lei nº 15051 de 2024?",
    "Qual a data de publicação da lei nº 15051 de 2024?",
    # Perguntas interpretativas
    "O que a lei nº 15022 diz sobre a realização de testes em animais?",
    "Como a Lei nº 15.022 de 2024 define o objetivo principal do Inventário Nacional de Substâncias Químicas?",
    # Perguntas contextuais
    "Como a lei 15081 de 2024 se relaciona com a lei 11977 de 2009?",
    "Qual a relação da lei 15080 de 2024 com a lei complementar nº 210 de 2024?",

    # Arquivos de Atividade Legislativa
    # Consultas diretas
    "Qual a ementa do Projeto de Lei n° 5021, de 2019?",
    "Em que ano o Projeto de Lei n° 5021 foi apresentado e por quem?",
    "O Projeto de Lei nº 5021, de 2019, foi convertido em qual lei?",
    # Perguntas interpretativas
    "Quais foram as etapas de tramitação do Projeto de Lei nº 3.793, de 2021, no Senado Federal até sua sanção?",
    # Perguntas contextuais
    "Qual a relação do projeto de lei n° 5637 de 2020 com a lei 11.771 de 2008?",
    "O projeto de lei n° 5637 de 2020 foi vetado?",

    # Arquivos de Vetos
    # Consultas diretas
    "Qual a ementa do Veto número 44, de 2024?",
    "Quais os dispositivos vetados pelo veto número 44, de 2024?",
    "Qual a razão do veto do dispositivo vetado pelo veto número 44, de 2024?",
    # Perguntas interpretativas
    "Do que se trata o veto número 39 de 2024?",
    "O governo apresentou justificativas técnicas ou políticas para o veto número 39 de 2024?",
    # Perguntas contextuais
    "O veto ao PL nº 2230, de 2022 alterou significativamente o objetivo do projeto?",
    "O que o veto número 40 de 2024 mudou em relação ao projeto de lei vetado por ele?"
]

# Precisão	    A resposta contém informações corretas?	            1 (errado) - 5 (completamente correto)
# Relevância	A resposta está relacionada à pergunta?	            1 (não relevante) - 5 (totalmente relevante)
# Clareza	    A resposta é clara e compreensível?	                1 (confusa) - 5 (muito clara)
# Completude	A resposta cobre todos os aspectos necessários?	    1 (incompleta) - 5 (abrangente)

# Respostas esperadas
test_answers = [
    # Arquivos de Leis
    # Consultas diretas
    "A lei confere o título de capital Nacional da Farinha de Mandioca ao Município de cruzeiro do Sul, no Estado do Acre.",
    "É conferido o título de Capital Nacional da Farinha de Mandioca ao Município de Cruzeiro do Sul, no Estado do Acre.",
    "A Lei nº 15.051 foi sancionada em 20 de dezembro de 2024.",
    # Perguntas interpretativas
    "A Lei nº 15.022, estabelece que a realização de testes em animais deve ser considerada apenas como último recurso para determinar o perigo de uma substância química, sendo permitida somente após esgotadas todas as possibilidades de métodos alternativos. Esses métodos alternativos devem ser cientificamente reconhecidos e apresentar um grau de confiabilidade adequado, conforme avaliação do Comitê Técnico de Avaliação de Substâncias Químicas. Além disso, a lei determina que o poder público designe um órgão fiscalizador para, em conjunto com instituições pertinentes, elaborar um plano estratégico que promova a utilização de métodos alternativos à experimentação com animais.",
    "O objetivo principal do Inventário Nacional de Substâncias Químicas, conforme estabelecido no Artigo 1º da Lei nº 15.022/2024, é minimizar os impactos adversos à saúde e ao meio ambiente por meio da avaliação e controle de risco das substâncias químicas utilizadas, produzidas ou importadas no território nacional.",
    # Perguntas contextuais
    "A Lei nº 15.081, de 30 de dezembro de 2024, altera a Lei nº 11977, de 7 de julho de 2009, que dispõe sobre o Programa Minha Casa, Minha Vida (PMCMV) e a regularização fundiária de assentamentos localizados em áreas urbanas, para assegurar o apoio técnico e financeiro às iniciativas de regularização fundiária de assentamentos urbanos.",
    "A relação entre essas duas normas reside no fato de que a Lei nº 15.080/2024 deve ser elaborada em conformidade com as diretrizes estabelecidas pela Lei Complementar nº 210/2024. Ou seja, a Lei nº 15.080/2024 incorpora as disposições da Lei Complementar nº 210/2024, garantindo que a elaboração e execução da Lei Orçamentária de 2025 estejam alinhadas às regras imperativas definidas para as leis orçamentárias da União. Em resumo, a Lei Complementar nº 210/2024 estabelece normas gerais para as leis orçamentárias da União, e a Lei nº 15.080/2024 detalha as diretrizes específicas para o orçamento de 2025, respeitando as disposições da lei complementar.",
    
    # Arquivos de Atividade Legislativa
    # Consultas diretas
    "O Projeto de Lei n° 5021, de 2019, reconhece o artesanato em capim dourado como manifestação da cultura nacional.",
    "O Projeto de Lei nº 5021, de 2019 foi apresentado na Câmara dos Deputados em 2019 pelo Deputado Federal Vicentinho Júnior (do PL-TO).",
    "O Projeto de Lei nº 5021, de 2019 foi convertido na Lei nº 15.005, sancionada em 17 de outubro de 2024.",
    # Perguntas interpretativas
    """O Projeto de Lei nº 3.793, de 2021, seguiu as seguintes etapas de tramitação no Senado Federal até sua sanção: 
    Recebimento e Autuação no Senado Federal: Em 13 de maio de 2024, o projeto, originário da Câmara dos Deputados, foi recebido e autuado no Senado Federal, sendo encaminhado para publicação.
    Análise na Comissão de Serviços de Infraestrutura (CI): O projeto foi encaminhado à Comissão de Serviços de Infraestrutura, onde o Senador Eduardo Braga (MDB/AM) foi designado relator. Em 3 de dezembro de 2024, a comissão aprovou o projeto em decisão terminativa. 
    Comunicação ao Plenário: Após a aprovação na comissão, o Presidente da CI, Senador Confúcio Moura, comunicou ao Presidente do Senado, Senador Rodrigo Pacheco, sobre a aprovação terminativa do projeto.
    Sanção Presidencial: O projeto foi encaminhado para sanção presidencial e transformado na Lei Ordinária nº 15.085, de 2 de janeiro de 2025, publicada no Diário Oficial da União em 3 de janeiro de 2025. 
    Essas etapas refletem o processo legislativo desde a apresentação do projeto no Senado até sua sanção e publicação como lei.""",
    # Perguntas contextuais
    "O Projeto de Lei nº 5.637, de 2020, altera a Lei nº 11.771, de 17 de setembro de 2008, para prever sanções aos prestadores de serviços turísticos que cometerem infrações associadas à facilitação do turismo sexual.",
    "O Projeto de Lei nº 5.637, de 2020, foi vetado parcialmente pelo Presidente da República.",

    # Arquivos de Vetos
    # Consultas diretas
    "Veto parcial aposto ao Projeto de Lei nº 5637, de 2020, que \"Altera a Lei nº 11771, de 17 de setembro de 2008 (Lei Geral do Turismo), para prever sanções aos prestadores de serviços turísticos que cometerem infrações associadas à facilitação do turismo sexual.",
    "O veto contém um único dispositivo vetado, sendo ele o artigo 2º do Projeto de Lei nº 5637, de 2020, na parte em que acrescenta o artigo 43-A à Lei nº 11771, de 17 de setembro de 2008",
    "A proposição contrariaria o interesse público ao estabelecer sanções que implicariam em risco de penalização de vítimas sob coação ou que estejam à mercê de práticas que violem a sua autonomia ou a sua liberdade de locomoção, ao prever pena para quem conceda alojamento ou acolhimento a pessoas que venham a exercer a prostituição, e não somente àqueles que praticam atos que visam à exploração sexual de terceiros.",
    # Perguntas interpretativas
    "O Veto nº 39, de 2024, refere-se ao Projeto de Lei nº 1.205, de 2024, que propõe alterações na Lei nº 14.597, de 14 de junho de 2023 (Lei Geral do Esporte), visando regulamentar os subsistemas esportivos privados e revogar dispositivos da Lei nº 9.615, de 24 de março de 1998 (Lei Pelé).",
    "A proposição legislativa contraria o interesse público ao revogar dispositivos que estabelecem critérios para que organizações esportivas sejam beneficiadas com isenções fiscais, o que pode comprometer a seleção adequada das entidades beneficiárias e prejudicar a gestão dos benefícios fiscais, com potencial renúncia de receita e possível conflito com a legislação fiscal. Além disso, o dispositivo incorre em vício de inconstitucionalidade uma vez que, por estar desacompanhada de estimativa de impacto orçamentário e financeiro, a potencial renúncia de receita viola o artigo 113 dos Atos das Disposições Constitucionais Transitórias.",
    # Perguntas contextuais
    "O Veto nº 40, de 2024, ao Projeto de Lei nº 2.230, de 2022, que trata da criação do Cadastro Nacional de Animais Domésticos, não alterou de forma significativa o objetivo principal do projeto, mas sim ajustou um detalhe importante relacionado à categorização dos animais. O veto foi dirigido ao dispositivo que incluía a categoria \"entretenimento\" na definição das funções dos animais domésticos. O governo argumentou que essa categoria não se alinha com o escopo do projeto, que se limita a animais de companhia ou de estimação. A justificativa foi de que a categoria \"entretenimento\" não tem respaldo no texto do projeto, o que poderia prejudicar o entendimento e a aplicação da lei.",
    "O Veto nº 40 de 2024 alterou o Projeto de Lei nº 2.230, de 2022, ao vetar dispositivos relacionados à categorização dos animais domésticos no cadastro proposto pela lei. Especificamente, o veto atingiu a seguinte parte do projeto: Alínea \"e\" do inciso IV do parágrafo único do artigo 2º do Projeto de Lei nº 2230, de 2022"
]
# Nome do arquivo para armazenar os resultados gerais
csv_filename = "avaliacao_geral_llms.csv"

# Variáveis para armazenar métricas
total_time = 0
bertscores = []
results = []
avaliacoes = {"Precisão": [], "Relevância": [], "Clareza": [], "Completude": []}

# Obtém o modelo usado do config.py
modelo_utilizado = getattr(config, "MODEL", "Desconhecido")

# Histórico da conversa
historico = []

# Teste das perguntas
for question, expected_answer in zip(test_questions, test_answers):
    historico.append({"role": "user", "content": question})
    
    start_time = time.time()
    llm_answer = generate_response(historico, client)
    response_time = time.time() - start_time
    total_time += response_time
    
    historico.append({"role": "assistant", "content": llm_answer})

    # Calcula BERTScore
    P, R, F1 = score([llm_answer], [expected_answer], lang="pt", verbose=True)
    bertscore_f1 = F1.item()
    bertscores.append(bertscore_f1)
    
    print(f"\nPergunta: {question}")
    print(f"Resposta do LLM: {llm_answer}")
    
    # Avaliação Manual
    precisao = int(input("Precisão (1-5): "))
    relevancia = int(input("Relevância (1-5): "))
    clareza = int(input("Clareza (1-5): "))
    completude = int(input("Completude (1-5): "))
    
    avaliacoes["Precisão"].append(precisao)
    avaliacoes["Relevância"].append(relevancia)
    avaliacoes["Clareza"].append(clareza)
    avaliacoes["Completude"].append(completude)
    
    results.append({
        "Modelo": modelo_utilizado,
        "Pergunta": question,
        "Resposta do LLM": llm_answer,
        "Tempo de Resposta (s)": response_time,
        "BERTScore (F1)": bertscore_f1,
        "Precisão": precisao,
        "Relevância": relevancia,
        "Clareza": clareza,
        "Completude": completude
    })

# Calcular médias
tempo_medio = total_time / len(test_questions)
bertscore_medio = sum(bertscores) / len(bertscores)

precisao_media = sum(avaliacoes["Precisão"]) / len(avaliacoes["Precisão"])
relevancia_media = sum(avaliacoes["Relevância"]) / len(avaliacoes["Relevância"])
clareza_media = sum(avaliacoes["Clareza"]) / len(avaliacoes["Clareza"])
completude_media = sum(avaliacoes["Completude"]) / len(avaliacoes["Completude"])

# Dados para avaliação geral
avaliacao_geral = [
    modelo_utilizado,
    tempo_medio,
    bertscore_medio,
    precisao_media,
    relevancia_media,
    clareza_media,
    completude_media
]

# Cabeçalhos do CSV
headers = [
    "Modelo", "Tempo Médio de Resposta", "BERTScore Médio", 
    "Precisão Média", "Relevância Média", "Clareza Média", "Completude Média"
]

# Salvar avaliação geral no CSV sem sobrescrever os dados anteriores
file_exists = os.path.exists(csv_filename)
with open(csv_filename, mode="a", newline="") as file:
    writer = csv.writer(file)
    
    # Se o arquivo for novo, escreve os cabeçalhos
    if not file_exists:
        writer.writerow(headers)
    
    # Escreve os dados
    writer.writerow(avaliacao_geral)

# Exibir avaliação geral
print("=== Avaliação Geral da LLM ===")
print(f"Modelo: {modelo_utilizado}")
print(f"Tempo Médio de Resposta: {tempo_medio:.2f} segundos")
print(f"BERTScore Médio (F1): {bertscore_medio:.4f}")
print(f"Precisão Média: {precisao_media:.2f}")
print(f"Relevância Média: {relevancia_media:.2f}")
print(f"Clareza Média: {clareza_media:.2f}")
print(f"Completude Média: {completude_media:.2f}")
print(f"Os resultados foram armazenados em '{csv_filename}'.")