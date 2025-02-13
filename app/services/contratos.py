import os
import logging
from app.services.comun import Archivos, Pdf, Docx, Imagen  
import app.logger_config 


class Verificacion:
    @staticmethod
    def verificar_tipo_doc(data):
        if data["tipo"] == "contrato":
            logging.info("Realizando servicio de creacion de pdf")
            return Contrato.generar_contrato(data)
        elif data["tipo"] == "adendum":
            logging.info("Realizando servicio de creacion de pdf")
            return Adendum.generar_adendum(data)
        else:
            return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}


    @staticmethod
    def verificar_tipo_doc_descarga(id):
        logging.info("Realizacion de servicio de descarga de plantilla")
        # 0 = contratos, 1 = adendum, 2 = declaraciones
        if id == 0:
            ruta = os.path.abspath("plantilla/contratos/plantilla_contratos.docx")
        elif id == 1:
            ruta = os.path.abspath("plantilla/contratos/plantilla_adendum.docx")
        elif id == 2:
            ruta = os.path.abspath("plantilla/contratos/plantilla_declaraciones.docx")
        else:
            return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}
        base64 = Archivos.archivo_a_base64(ruta)
        if base64:
            return {"estado": True, "mensaje": "Archivo encontrado", "datos": base64}
        return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}


    @staticmethod
    def verificar_tipo_doc_plantilla(data,id):
        logging.info("Realizacion de servicio de actualizacion de plantilla")
        if data["archivo"]:
            # 0 = contratos, 1 = adendum, 2 = declaraciones
            if id == 0:
                ruta = os.path.abspath("plantilla/contratos/plantilla_contratos.docx")
            elif id == 1:
                ruta = os.path.abspath("plantilla/contratos/plantilla_adendum.docx")
            elif id == 2:
                ruta = os.path.abspath("plantilla/contratos/plantilla_declaraciones.docx")
            else:
                return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}
            log_guardar = Archivos.guardar_archivo_base64(ruta,data["archivo"])
            if log_guardar:
                return {"estado": True, "mensaje": "Se ha modificado la plantilla correctamente"}
            else:
                return {"estado": False, "mensaje": "No se ha podido guardar el archivo"}
        else:
           return {"estado": False, "mensaje": "No se envio ningun archivo"} 



class Adendum:
    @staticmethod
    def generar_adendum(data):
        if data:
            ruta_plantilla_adendum = os.path.abspath("plantilla/contratos/plantilla_adendum.docx")
            ruta_plantilla_declaraciones = os.path.abspath("plantilla/contratos/plantilla_declaraciones.docx")
            ruta_docx_generado_adendum = os.path.abspath("plantilla/contratos/temp/adendum.docx")
            ruta_docx_generado_declaraciones = os.path.abspath("plantilla/contratos/temp/declaraciones.docx")
            estilos = {"fuente": "Helvetica", "numero":10}
            log_reemplazar_adendum = Docx.reemplazar_texto_docx(ruta_plantilla_adendum, ruta_docx_generado_adendum, data, estilos)
            log_reemplazar_declaraciones = Docx.reemplazar_texto_docx(ruta_plantilla_declaraciones, ruta_docx_generado_declaraciones, data, estilos)
            if log_reemplazar_adendum and log_reemplazar_declaraciones:
                ruta_directorio_pdf = os.path.abspath("plantilla/contratos/temp/")
                ruta_pdf_adendum = Pdf.convertir_docx_a_pdf(ruta_docx_generado_adendum, ruta_directorio_pdf)
                ruta_pdf_declaraciones = Pdf.convertir_docx_a_pdf(ruta_docx_generado_declaraciones, ruta_directorio_pdf)
                if ruta_pdf_adendum and ruta_pdf_declaraciones:
                    log_imagenes = Imagenes.procesar_imagenes(data["recibos_pago"])
                    if log_imagenes["estado"] == True:
                        pdfs_unir = [ruta_pdf_adendum, ruta_pdf_declaraciones, log_imagenes["ruta"]]
                        ruta_pdf = os.path.abspath("plantilla/contratos/temp/adendum_completo.pdf")
                        log_unir_pdf = Pdf.unir_pdfs(pdfs_unir, ruta_pdf)
                        if log_unir_pdf:
                            docs_eliminar = [ruta_docx_generado_adendum, ruta_docx_generado_declaraciones, ruta_pdf_adendum, ruta_pdf_declaraciones, log_imagenes["ruta"]]
                            log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                            if log_eliminar_data:
                                pdf_base64 = Archivos.archivo_a_base64(ruta_pdf)
                                if pdf_base64:
                                    return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": pdf_base64}    
                                else:
                                    return {"estado": False, "mensaje": "No se logro crear base64"}    
                            else:
                                return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares"}
                        else:
                            return {"estado": False, "mensaje": "No se ha podido unir Adendum con Declaraciones"}    
                    else:
                        return log_imagenes
                else:
                    return {"estado": False, "mensaje": "Documento PDF no se puede crear"}    
            else:
                    return {"estado": False, "mensaje": "No se ha posido reemplazar los datos en la plantilla"}   
        else:
            return {"estado": False, "mensaje": "No hay datos en el body"}   


class Contrato:
    @staticmethod
    def generar_contrato(data):
        if data:
            ruta_plantilla_contratos = os.path.abspath("plantilla/contratos/plantilla_contratos.docx")
            ruta_plantilla_declaraciones = os.path.abspath("plantilla/contratos/plantilla_declaraciones.docx")
            ruta_docx_generado_contratos = os.path.abspath("plantilla/contratos/temp/contratos.docx")
            ruta_docx_generado_declaraciones = os.path.abspath("plantilla/contratos/temp/declaraciones.docx")
            estilos = {"fuente": "Helvetica", "numero":10}
            log_reemplazar_contratos = Docx.reemplazar_texto_docx(ruta_plantilla_contratos, ruta_docx_generado_contratos, data, estilos)
            log_reemplazar_declaraciones = Docx.reemplazar_texto_docx(ruta_plantilla_declaraciones, ruta_docx_generado_declaraciones, data, estilos)
            if log_reemplazar_contratos and log_reemplazar_declaraciones:
                ruta_docx_generado_contratos_estilos = os.path.abspath("plantilla/contratos/temp/contratos_estilo.docx")
                log_estilos = Docx.aplicar_estilos_especificos(ruta_docx_generado_contratos, ruta_docx_generado_contratos_estilos)
                if log_estilos:
                    ruta_directorio_pdf = os.path.abspath("plantilla/contratos/temp")
                    ruta_pdf_contratos = Pdf.convertir_docx_a_pdf(ruta_docx_generado_contratos_estilos, ruta_directorio_pdf)
                    ruta_pdf_declaraciones = Pdf.convertir_docx_a_pdf(ruta_docx_generado_declaraciones, ruta_directorio_pdf)
                    if ruta_pdf_contratos and ruta_pdf_declaraciones:
                        log_imagenes = Imagenes.procesar_imagenes(data["recibos_pago"])
                        if log_imagenes["estado"] == True:
                            pdfs_unir = [ruta_pdf_contratos, ruta_pdf_declaraciones, log_imagenes["ruta"]]
                            ruta_pdf = os.path.abspath("plantilla/contratos/temp/contrato_completo.pdf")
                            log_unir_pdf = Pdf.unir_pdfs(pdfs_unir, ruta_pdf)
                            if log_unir_pdf:
                                docs_eliminar = [ruta_docx_generado_contratos, ruta_docx_generado_declaraciones, ruta_pdf_contratos, ruta_pdf_declaraciones, log_imagenes["ruta"], ruta_docx_generado_contratos_estilos]
                                log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                                if log_eliminar_data:
                                    pdf_base64 = Archivos.archivo_a_base64(ruta_pdf)
                                    if pdf_base64:
                                        return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": pdf_base64}    
                                    else:
                                        return {"estado": False, "mensaje": "No se logro crear base64"}    
                                else:
                                    return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares"}
                            else:
                                return {"estado": False, "mensaje": "No se ha podido unir contratos con Declaraciones"}    
                        else:
                            return log_imagenes
                    else:
                        return {"estado": False, "mensaje": "Documento PDF no se puede crear"}
                else:
                    return {"estado": False, "mensaje": "No se ha podido aplicar estilos"}    
            else:
                    return {"estado": False, "mensaje": "No se ha posido reemplazar los datos en la plantilla"}   
        else:
            return {"estado": False, "mensaje": "No hay datos en el body"}  


class Imagenes:
    @staticmethod
    def procesar_imagenes(imagenesBase64):
        if imagenesBase64:
            rutas_imagenes_pdf = []
            rutas_a_eliminar = []
            for indice, recibo in enumerate(imagenesBase64):
                ruta_imagen_aux = os.path.abspath("plantilla/contratos/temp/recibo"+str(indice))
                ruta_imagen = Imagen.guardar_imagen_base64(recibo, ruta_imagen_aux)
                rutas_a_eliminar.append(ruta_imagen)
                if ruta_imagen:
                    ruta_plantilla_imagen = os.path.abspath("plantilla/contratos/plantilla_imagenes.docx")
                    ruta_docx_imagen = os.path.abspath("plantilla/contratos/temp/recibo"+str(indice)+".docx")
                    rutas_a_eliminar.append(ruta_docx_imagen)
                    log_imagen_docs = Docx.imagen_en_docx(ruta_imagen, ruta_plantilla_imagen,"algunaclave" , 450)
                    if log_imagen_docs:
                        ruta_directorio_pdf_imagen = os.path.abspath("plantilla/contratos/temp")
                        ruta_imagen_pdf = Pdf.convertir_docx_a_pdf(ruta_docx_imagen,ruta_directorio_pdf_imagen)
                        rutas_a_eliminar.append(ruta_imagen_pdf)
                        if ruta_imagen_pdf:
                            rutas_imagenes_pdf.append(ruta_imagen_pdf)
                        else:
                            return {"estado": False, "mensaje": "Hubo un error al tranformar imagenes a pdf"}  
                    else:
                        return {"estado": False, "mensaje": "Hubo un error al insertar las imagenes en el documento"}
                else:
                    return {"estado": False, "mensaje": "Hubo un error con las imagenes adjuntadas"}
            ruta_imagenes_unidas_pdf = os.path.abspath("plantilla/contratos/temp/imagenes.pdf")
            print(rutas_imagenes_pdf)
            log_unir_imagenes = Pdf.unir_pdfs(rutas_imagenes_pdf, ruta_imagenes_unidas_pdf)
            if log_unir_imagenes:
                Archivos.eliminar_documentos(rutas_a_eliminar)
                return {"estado": True, "mensaje": "Se proceso bien las imagenes", "ruta":ruta_imagenes_unidas_pdf}
            else:
                return {"estado": False, "mensaje": "Hubo un error al unir las imagenes"}
        else:
            return {"estado": False, "mensaje": "No hay recibos de pago"}



    