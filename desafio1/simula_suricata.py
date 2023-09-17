import json
import random
import pandas as pd
import requests

# Carregar os logs do arquivo JSON
with open('Terra.json', 'r') as json_file:
    logs_data = json.load(json_file)

# Converter os dados em um DataFrame pandas
logs_df = pd.DataFrame(logs_data)

def convert_to_json_safe(log):
    # Converte os valores numéricos para tipos de dados Python
    log['timestamp'] = str(log['timestamp'])
    log['src_ip'] = str(log['src_ip'])
    
    # Converter valores numéricos com tratamento especial
    try:
        log['flow_id'] = int(float(log['flow_id'].replace(',', '')))
    except (ValueError, AttributeError):
        log['flow_id'] = None

    log['src_port'] = int(log['src_port'])
    log['dest_port'] = int(log['dest_port'])
    
    try:
        log['tx_id'] = int(float(log['tx_id'].replace(',', '')))
    except (ValueError, AttributeError):
        log['tx_id'] = None
    
    try:
        log['icmp_type'] = int(log['icmp_type'])
    except (ValueError, TypeError):
        log['icmp_type'] = None
    
    try:
        log['icmp_code'] = int(log['icmp_code'])
    except (ValueError, TypeError):
        log['icmp_code'] = None
    
    try:
        log['alert.severity'] = int(float(log['alert.severity']))
    except (ValueError, KeyError, TypeError):
        log['alert.severity'] = None
    
    # Adicione conversões para outros campos numéricos, se necessário
    return log

def enviar_log_aleatorio():
    log = logs_df.sample(n=1).to_dict(orient='records')[0]
    #print(log['payload'])
    log = convert_to_json_safe(log)
    response = requests.post('http://localhost:5000/receber_log', json=log)
    print(f"Enviado: {log}")
    return response.text

while True:
    entrada = input("Digite 1 para enviar um log, ou 'q' para sair: ")
    if entrada == '1':
        enviar_log_aleatorio()
    elif entrada == 'q':
        break
