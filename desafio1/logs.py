from flask import Flask, request, jsonify

app = Flask(__name__)

logs = []

@app.route('/receber_log', methods=['POST'])
def receber_log():
    log = request.get_json()
    logs.append(log)
    #print(log)
    return "Log recebido com sucesso!", 200

@app.route('/logs', methods=['GET'])
def listar_logs():
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True)
