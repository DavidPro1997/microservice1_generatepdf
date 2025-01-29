from flask import Flask, request, jsonify
from app.services import Switch
# from flask_cors import CORS

app = Flask(__name__)

# # Configuración de CORS específica con encabezados y métodos permitidos
# CORS(app, resources={r"/*": {"origins": ["http://dev.mvevip_cotizador.com","https://website.mvevip.com"]}}, 
#      supports_credentials=True, 
#      allow_headers=["Content-Type", "Authorization"],
#      methods=["POST", "OPTIONS", "GET", "DELETE"])


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



@app.route('/crearImagen', methods=['POST'])
def crear_imagen():
    data = request.json
    respuesta = Switch.verificar_tipo_doc(data)
    return jsonify(respuesta)
