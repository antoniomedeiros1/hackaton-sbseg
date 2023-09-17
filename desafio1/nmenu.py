import pandas as pd
from flask import Flask, request, jsonify
import json
from sympy import symbols, Eq, And
import threading
from flask import Flask
import requests
import os

app = Flask(__name__)
regras = []
aviso = "Bem vindo ao sistema."

def carregar_dataframe(caminho_arquivo_json):
    """Carrega um arquivo JSON em um DataFrame."""
    df = pd.read_json(caminho_arquivo_json)
    return df

def carregar_regras():
    """Carrega as regras a partir do arquivo JSON fixo."""
    try:
        with open("rules.json", 'r') as arquivo:
            regras = json.load(arquivo)
        return regras
    except FileNotFoundError:
        print(f"O arquivo não foi encontrado.")
        return []
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar o arquivo JSON: {str(e)}")
        return []

def salvar_regras_em_json(regras):
    """Salva a lista de regras em um arquivo JSON, sem funções lambda."""
    regras_sem_lambda = []

    for regra in regras:
        condicoes, nova_severidade = regra
        condicoes_sem_lambda = []

        for condicao in condicoes:
            coluna, operador, valor = condicao
            condicoes_sem_lambda.append([coluna, operador, valor])

        regras_sem_lambda.append([condicoes_sem_lambda, nova_severidade])

    with open("rules.json", 'w') as arquivo:
        json.dump(regras_sem_lambda, arquivo, indent=4)

def criar_regra(condicoes, nova_severidade):
    """Cria uma regra no formato [condicoes, nova_severidade]."""
    return [condicoes, nova_severidade]

def aplicar_regra(row, regra):
    """Aplica uma regra a uma linha e atualiza a severidade, se necessário."""
    condicoes, nova_severidade = regra

    # Converter as condições em equações
    equacoes = []
    for coluna, operador, valor in condicoes:
        if operador == '=':
            if str(valor).isnumeric():  # Check if the value is numeric
                valor = float(valor)
                equacoes.append(Eq(row[coluna], valor))
            else:
                equacoes.append(Eq(symbols(row[coluna]), symbols(valor)))
        elif operador == '>':
            if str(valor).isnumeric():  # Check if the value is numeric
                valor = float(valor)
                equacoes.append(row[coluna] > valor)
            else:
                equacoes.append(row[coluna] > valor)

    # Verificar se todas as equações são verdadeiras
    todas_verdadeiras = all(equacao == True for equacao in equacoes)

    if todas_verdadeiras:
        row['alert.severity'] = nova_severidade
    return row

def criar_fila_com_regras(df, regras):
    """Cria uma fila ordenada com base nas regras especificadas."""
    fila = []
    for index, row in df.iterrows():
        for regra in regras:
            row = aplicar_regra(row, regra)
        fila.append(row)
    fila.sort(key=lambda x: x['severidade'])
    return fila

def aplicar_condicao(row, coluna, operador, valor):
    """Aplica uma única condição a uma linha do DataFrame."""
    if operador == '=':
        if isinstance(valor, str):
            return row[coluna] == valor
        elif isinstance(valor, (int, float)):
            return row[coluna] == float(valor)
    elif operador == '>':
        if isinstance(valor, str):
            return row[coluna] > float(valor)
        elif isinstance(valor, (int, float)):
            return row[coluna] > float(valor)
    return False

def listar_logs():
    response = requests.get('http://localhost:5000/logs')
    return response.json()

app = Flask(__name__)

def criar_condicao(coluna, operador, valor):
    """Cria uma condição para a regra."""
    try:
        valor_input = input(f"O valor '{valor}' é string? (S/N): ")
        if valor_input.lower() == 's':
            return [coluna, operador, str(valor)]  # Convert the value to a string
        elif valor_input.lower() == 'n':
            valor = float(valor)  # Convert the value to a float
            return [coluna, operador, valor]
        else:
            print("Escolha inválida. A condição não foi criada.")
            return None
    except ValueError:
        print(f"Erro: O valor '{valor}' não é numérico.")
        return None

def criar_regras_especiais(df, campo, min_repeticoes):
    if df.shape != 0:
        regras_especiais = []

        # Agrupar o DataFrame pelo campo e contar as ocorrências
        print(df)
        contagem = df[campo].value_counts()

        # Filtrar valores que atendam ao critério mínimo de repetições
        valores_validos = contagem[contagem >= min_repeticoes].index

        for valor in valores_validos:
            categorias = df.loc[df[campo] == valor, 'alert.category'].tolist()
            regra_especial = {'valor': valor, 'categorias': categorias}
            regras_especiais.append(regra_especial)

        return regras_especiais
    else:
        print("O DataFrame está vazio.")

def aplicar_regras_especiais(df, regras_especiais):
    #print(regras_especiais)
    if regras_especiais != []:
        resultados = []

        for _, row in df.iterrows():
            valor = row[valor]
            categorias = []

            for regra in regras_especiais:
                if valor == regra['valor']:
                    categorias.extend(regra['categorias'])

            resultados.append({'Chave': valor, 'Categorias': categorias})

        return resultados
    else:
        print("Não existem regras especiais para aplicar.")
    

def exibir_menu():
    """Exibe um menu de opções."""
    print("MENU:")
    print("1. Criar Regra")
    print("2. Criar Regras Especiais")
    print("3. Atualizar logs")
    print("4. Exibir agrupamento por campo")
    print("5. Exibir agrupamento por severidade")
    print("6. Exibir fila de prioridade")
    print("9. Sair")

def main():
    df = pd.DataFrame()
    regras = carregar_regras()
    regras_especiais = []
    logs = []
    print("Regras carregadas:", regras)

    while True:
        os.system('clear')
        print(aviso)
        exibir_menu()
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            num_condicoes = int(input("Quantas condições você deseja adicionar à regra? "))
            condicoes = []
            for _ in range(num_condicoes):
                coluna = input("Digite a coluna: ")
                operador = input("Digite o operador (=, >, <): ")
                valor = input("Digite o valor: ")
                condicao = criar_condicao(coluna, operador, valor)
                if condicao is not None:
                    condicoes.append(condicao)
            if len(condicoes) > 0:
                nova_severidade = int(input("Digite a nova severidade: "))
                regra = criar_regra(condicoes, nova_severidade)
                regras.append(regra)
                salvar_regras_em_json(regras)  # Salvar as regras atualizadas
                print("Regra criada com sucesso!")
                input("Pressiona qualquer tecla para continuar...")
            else:
                print("Regra não criada devido a erro nas condições ou escolha inválida.")
        
        elif escolha == '2':
            campo = input("Escolha qual o campo deverá ser agrupado: ")
            rep = input("Quantas vezes esse campo deve aparecer para gerar o alerta: ")
            regras_especiais_novas = criar_regras_especiais(df,campo,int(rep))
            for x in regras_especiais_novas:
                regras_especiais.append(x)
            print("Regras especiais criadas com sucesso!")
            for x in regras_especiais:
                print("Chave:", x['valor'], "Categorias:", x['categorias'])
            input("Pressiona qualquer tecla para continuar...")

        elif escolha == '3':
            if len(regras) > 0:
                print("Aguardando log: ")
                logs = listar_logs()
                print("Logs recebidos com sucesso!")

                df_result = pd.DataFrame(logs)
                #print(df_result)
                for regra in regras:
                    df_result = df_result.apply(lambda row: aplicar_regra(row, regra), axis=1)

                df = pd.concat([df, df_result])

                df = df.sort_values(by='alert.severity', ascending=True)

                res = aplicar_regras_especiais(df, regras_especiais)
                print("ALERTA DE URGENCIA: ")
                df_urgencia = df.loc[df['alert.severity'] == 1]
                print(df_urgencia)
                input("Pressiona qualquer tecla para continuar...")

            else:
                print("Por favor, crie pelo menos uma regra.")
        
        elif escolha == "4":
            try:
                campo = input("Qual o campo a ser agrupado? ")
                df_grupos = df.groupby(campo)
                for categoria, grupo in df_grupos:
                    print(f'Grupo para a Categoria "{categoria}":')
                    print(grupo)
                    print()
                input("Pressiona qualquer tecla para continuar...")
            except:
                print("Erro ao agrupar os dados.")
                input("Pressiona qualquer tecla para continuar...")

        elif escolha == "5":
            severity = input("Qual a severidade? ")
            df_result = df.loc[df['alert.severity'] == int(severity)]
            print(df_result)
            input("Pressiona qualquer tecla para continuar...")

        elif escolha == "6":
            print(df)
            input("Pressiona qualquer tecla para continuar...")

        elif escolha == '9':
            print("Saindo do programa.")
            break

        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
