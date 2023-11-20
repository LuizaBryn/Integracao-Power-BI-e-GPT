
import openai
import dotenv
import os
import time

dotenv.load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://ciasc-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r", encoding="utf-8") as arquivo:
            dados = arquivo.read()
            return dados
    except IOError as e:
        print(f"Erro: {e}")

def salva(nome_do_arquivo, conteudo):
    try:
        with open(nome_do_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")


def extrai_dados(prompt_usuario):
    
    tentativa = 0
    eng = "ia_ciasc_16k"  #modelo gpt-3.5-turbo
    tempo_de_tentativa = 10

    while tentativa <= 3:
        tentativa += 1
        try: 
            resposta = openai.ChatCompletion.create(
            engine=eng,
            messages=[
                {
                "role": "system",
                "content":  f"""
                Você é um gerador de dados csv.
                Você recebe como entrada o relato uma ou mais pessoas e coleta os dados de importancia sobre o ocorrido.
                Caso você não tenha muita certeza se existe o dado solicitado no relato, coloque como "None".
                A saída é apenas e somente o csv.

                ##Exemplo de entrada:

                Arquivo: "Meu nome é Marina, tenho 3 filhos... Moro em Copacabana. Nasci no dia 23/09/1988. Não entendo o motivo de estar aqui não, mas gosto muito de paçoca
                Tenho experiencia em vender roupas e faxina. Estou a procura de emprego. Meu sonho é ser aeromoça."
                Dados de interesse: Nome, Data de Nascimento, Cidade, Estado, País, Experiencia profissinal.

                ##Saída(csv): 
                Nome do relator, Data de Nascimento, Cidade, Estado, País, Experiência profissional
                Marina, 23/09/1988, Copacabana, Rio de Janeiro, Brasil, "Vendedora e Serviços de limpeza"

                """
                },
                {
                "role": "user",
                "content": prompt_usuario
                }
            ],
            temperature=0.5,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            )
            resultado = resposta.choices[0].message.content
            print("Resultado criado com sucesso!")
            
            return resultado

        # Tratamento de ERROS:
        except openai.error.AuthenticationError as e:
            print("Erro de Autenticação:", e)
        except openai.error.APIError as e:
            print("Erro de API:", e)
            if tentativa != 3:
                print("Aguarde. Tentando requisição novamente...")
            time.sleep(30)
        except openai.error.RateLimitError as e:
            print("Erro de taxa limite de requisição:", e)
            tempo_de_tentativa *= 2 #tecnica usada para não exagerar nas requisições
            time.sleep(tempo_de_tentativa)



#nesta requisição há problema pois muitos tokens estão sendo enviados
produtos_site_ciasc = f"""
Arquivo: {carrega("site.html")}
Dados de interesse: PRODUTO, CATEGORIA, PRINCIPAIS BENEFÍCIOS<no máximo 3>
"""
for i in range(5):

    relato = carrega(f"./transcricao_chamadas/relato{i+1}.txt")
    csv = extrai_dados(f"""              
    Arquivo: {relato}
    Dados para extração: LOCAL, DATA, NUMERO DE VITIMAS, NUMERO DE SUSPEITOS, CATEGORIA DE CRIME, ARMA DO CRIME, MOTIVO DO CRIME
    """)
    
    tempo_local = time.localtime()

    # Obtendo o dia, mês, ano, hora, minuto e segundo
    dia = tempo_local.tm_mday
    mes = tempo_local.tm_mon
    ano = tempo_local.tm_year
    hora = tempo_local.tm_hour
    minuto = tempo_local.tm_min
    segundo = tempo_local.tm_sec

    print(csv)
    salva(f"./boletins_de_ocorrencia/bo_{i+1}_{dia}_{mes}_{ano}_{hora}_{minuto}_{segundo}.csv", csv)
