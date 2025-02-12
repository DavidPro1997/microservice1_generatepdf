import os
from app.services.comun import Archivos, Pdf, Docx  


class Hotel:
    @staticmethod
    def generar_voucher(data):
        if data:
            rooms = data["rooms"]
            data.pop("rooms")
            ruta_plantilla_voucher = os.path.abspath("plantilla/voucher_hotel/plantilla_voucher_hotel.docx")
            ruta_docx_generado_tabla = os.path.abspath("plantilla/voucher_hotel/temp/voucher_tabla.docx")
            estilos = {"fuente": "Helvetica", "numero":10}
            log_tabla_rooms = Docx.crear_tabla_rooms(ruta_plantilla_voucher,ruta_docx_generado_tabla,"[rooms]", rooms, estilos)
            if log_tabla_rooms:
                ruta_docx_generado_voucher = os.path.abspath("plantilla/voucher_hotel/temp/voucher.docx")
                log_reemplazar_cotitazion = Docx.reemplazar_texto_docx(ruta_docx_generado_tabla, ruta_docx_generado_voucher, data, estilos)
                if log_reemplazar_cotitazion:
                    ruta_directorio_pdf = os.path.abspath("plantilla/voucher_hotel/temp")
                    ruta_pdf_cotizacion_vuelos = Pdf.convertir_docx_a_pdf(ruta_docx_generado_voucher, ruta_directorio_pdf)
                    if ruta_pdf_cotizacion_vuelos:
                        docs_eliminar = [ruta_docx_generado_voucher,ruta_docx_generado_tabla]
                        log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                        if log_eliminar_data:
                            pdf_base64 = Archivos.archivo_a_base64(ruta_pdf_cotizacion_vuelos)
                            if pdf_base64:
                                return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": pdf_base64}    
                            else:
                                return {"estado": False, "mensaje": "No se logro crear base64"}    
                        else:
                            return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares"}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"}   
                else:
                    return {"estado": False, "mensaje": "No se ha posido reemplazar los datos en la plantilla"}
            else:
                return {"estado": False, "mensaje": "No se logro armar la tabla"} 
        else:
            return {"estado": False, "mensaje": "No hay datos en el body"}


    