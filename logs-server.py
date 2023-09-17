from flask import Flask, jsonify, request
import random
import json
import threading
import time

app = Flask(__name__)

logs = {}
counter = 0

with open('Terra.json', 'r') as file:
    data = json.load(file)

indexes = list(data["timestamp"].keys())

def get_random_key():
    return random.choice(indexes)

def get_top(dictionary, n=5):
    # Sort the dictionary by values in descending order
    sorted_dict = {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)}
    
    # Take the top 5 items
    top_5 = dict(list(sorted_dict.items())[:n])
    return top_5


def serve_random_key():

    global logs, counter
    
    while True:
        index = get_random_key()

        log = {}

        for key in data:
            if key == 'alert':
                log[key] = json.loads(data[key][index].replace("'","\""))
            else:
                log[key] = data[key][index]

        logs[counter] = log
        counter = counter + 1

        print(f"Serving random key: {index}")
        time.sleep(5)

@app.route('/logs')
def logs_endpoint():
    global logs
    return jsonify(logs)


@app.route('/filtered_logs')
def filtered_logs():
    global logs

    ip = request.args.get('ip')

    filtered_logs = {}

    for key in logs:
        if ip == logs[key]['dest_ip'] or ip == logs[key]['src_ip']:
            filtered_logs[key] = logs[key]

    return jsonify(filtered_logs)


@app.route('/categories')
def categories():
    global logs

    categories = {}

    for key in logs:
        if logs[key]['alert']['category'] not in categories.keys():
            categories[logs[key]['alert']['category']] = 1
        else:
            categories[logs[key]['alert']['category']] = categories[logs[key]['alert']['category']] + 1
        
    return jsonify(categories)


@app.route('/signature')
def signature():
    global logs

    signatures = {}

    for key in logs:
        if logs[key]['alert']['signature'] not in signatures.keys():
            signatures[logs[key]['alert']['signature']] = 1
        else:
            signatures[logs[key]['alert']['signature']] = signatures[logs[key]['alert']['signature']] + 1
        
    return jsonify(get_top(signatures, 10))


@app.route('/severity')
def severities():
    global logs
    
    severities = {}

    for key in logs:
        index = logs[key]['alert']['severity']
        if index not in severities.keys():
            severities[index] = 1
        else: 
            severities[index] = severities[index] + 1
        
    return jsonify(severities)


@app.route('/protocol')
def protocols():
    global logs
    
    protos = {}

    for key in logs:
        index = logs[key]['proto']
        if index not in protos.keys():
            protos[index] = 1
        else: 
            protos[index] = protos[index] + 1
        
    return jsonify(protos)


@app.route('/src_ip')
def src_ip():
    global logs
    
    src_ips = {}

    for key in logs:
        index = logs[key]['dest_ip']
        if index not in src_ips.keys():
            src_ips[index] = 1
        else: 
            src_ips[index] = src_ips[index] + 1
        
    return jsonify(get_top(src_ips, 5))


@app.route('/dest_ip')
def dest_ip():
    global logs
    
    dest_ips = {}

    for key in logs:
        index = logs[key]['dest_ip']
        if index not in dest_ips.keys():
            dest_ips[index] = 1
        else: 
            dest_ips[index] = dest_ips[index] + 1
        
    return jsonify(get_top(dest_ips, 5))


@app.route('/src_port')
def src_port():
    global logs
    
    src_ports = {}

    for key in logs:
        index = logs[key]['src_port']
        if index not in src_ports.keys():
            src_ports[index] = 1
        else: 
            src_ports[index] = src_ports[index] + 1
        
    return jsonify(get_top(src_ports, 5))


@app.route('/dest_port')
def dest_ports():
    global logs
    
    dest_ports = {}

    for key in logs:
        index = logs[key]['dest_port']
        if index not in dest_ports.keys():
            dest_ports[index] = 1
        else: 
            dest_ports[index] = dest_ports[index] + 1
        
    return jsonify(get_top(dest_ports, 5))


@app.route('/')
def home():
    return "home"

if __name__ == '__main__':
    random_key_thread = threading.Thread(target=serve_random_key)
    random_key_thread.daemon = True
    random_key_thread.start()
    app.run(host='0.0.0.0', port=5000)
