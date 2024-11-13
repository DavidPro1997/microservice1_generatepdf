from flask import Flask, request, jsonify
from app.services import Switch

app = Flask(__name__)

@app.route('/')
def index():
    return "¡Bienvenido al generador de pdfs!"

@app.route('/ejemplo1', methods=['POST'])
def ejemplo1():
    data = request.json
    respuesta = Switch.verificar_tipo_doc(data)
    return jsonify(respuesta)
