from flask import Flask, request, jsonify
from app.services import Switch

app = Flask(__name__)

@app.route('/')
def index():
    return "¡Bienvenido al generador de pdfs!"


@app.route('/crearpdf', methods=['POST'])
def crear_pdf():
    data = request.json
    respuesta = Switch.verificar_tipo_doc(data)
    return jsonify(respuesta)


@app.route('/descargarPlantilla/<int:id>', methods=['GET'])
def descargar_plantilla(id):
    respuesta = Switch.verificar_tipo_doc_descarga(id)
    return jsonify(respuesta)


@app.route('/subirPlantilla/<int:id>', methods=['POST'])
def subir_plantilla(id):
    data = request.json
    respuesta = Switch.verificar_tipo_doc_plantilla(data,id)
    return jsonify(respuesta)
