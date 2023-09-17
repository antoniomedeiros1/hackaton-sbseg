from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/logs', methods=['GET'])
def get_data():
    with open('Terra.json', 'r') as file:
        data = file.read()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
