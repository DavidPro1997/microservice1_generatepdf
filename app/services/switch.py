import os
from app.services.contratos import Verificacion 
from app.services.voucher_hotel import Hotel 
from app.services.cotizacion import Cotizador 
from app.services.imagenes_vuelos import Img
from app.services.reservas import Reservas
from app.services.comun import Archivos 
from app import app
import uuid
import app.logger_config 




class Switch:
    @staticmethod
    def verificar_tipo_doc(data):
        unique_id = str(uuid.uuid4())[:8]
        if data["tipo"] == "contrato" or data["tipo"] == "adendum":
            print("Realizando servicio de creacion de contatos")
            return Verificacion.verificar_tipo_doc(data)
        elif data["tipo"] == "cotizar_vuelo_imagen":
            print("Realizando servicio de creacion de imagen")
            return Img.cotizar_vuelos(data)
        elif data["tipo"] == "voucher_hotel":
            print("Realizando servicio de creacion de voucher")
            return Hotel.generar_voucher(data)
        elif data["tipo"] == "cotizador_general":
            print("Realizando servicio de creacion de cotizacion completa")
            resultado = Cotizador.cotizar_completo(data, unique_id)
            ruta_temp_cotizacion = os.path.abspath(f"plantilla/cotizaciones/temp")
            log_temp = Archivos.eliminar_contenido_directorio(ruta_temp_cotizacion)
            if log_temp:
                return resultado
            else:
                return {"estado": False, "mensaje": "No se logro eliminar los archivos temporales"} 
        elif data["tipo"] == "pdf_reservas":
            print("Realizando servicio de creacion de confirmación de reservas")
            resultado = Reservas.pdf_reseva(data, unique_id)
            ruta_temp_reservas = os.path.abspath(f"plantilla/reservas/temp")
            log_temp = Archivos.eliminar_contenido_directorio(ruta_temp_reservas)
            if log_temp:
                return resultado
            else:
                return {"estado": False, "mensaje": "No se logro eliminar los archivos temporales"} 
            # return Reservas.pdf_reseva(data, unique_id)
        else:
            return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}
        

    @staticmethod
    def verificar_tipo_doc_descarga(id):
        return Verificacion.verificar_tipo_doc_descarga(id)


    @staticmethod
    def verificar_tipo_doc_plantilla(data,id):
        return Verificacion.verificar_tipo_doc_plantilla(data, id)

