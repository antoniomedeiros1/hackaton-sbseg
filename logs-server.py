from flask import Flask, jsonify
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

@app.route('/')
def home():
    return "home"

if __name__ == '__main__':
    random_key_thread = threading.Thread(target=serve_random_key)
    random_key_thread.daemon = True
    random_key_thread.start()
    app.run(host='0.0.0.0', port=5000)
