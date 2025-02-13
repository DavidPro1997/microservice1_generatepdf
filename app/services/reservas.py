import os, shutil
import locale
from app.services.comun import Archivos, Pdf, Docx, Imagen, Api  
import app.logger_config 

locale.setlocale(locale.LC_TIME, "es_ES.utf8")


class Reservas:
    @staticmethod
    def pdf_reseva(data, idUnico):
        docs_eliminar = []
        if "datos" in data and data["datos"]:

            # url = (f"https://apirest.mvevip.com/api/hotelbeds/booking/hotel-info/{data['datos']['idHotel']}")
            # hotel = Api.llamar_api_get(url)
            # imagenes = hotel["consulta"]["images"]
            # print(json.dumps(imagenes, indent=4))
            portada = Reservas.generar_portada(data["datos"], idUnico)
            if portada["estado"]:
                ruta_portada = portada["ruta"]
                docs_eliminar.append(ruta_portada)
            cuerpo = Reservas.generar_pdf_imgs(data["datos"], idUnico)
            if cuerpo["estado"]:
                ruta_imgs = cuerpo["ruta"]
                docs_eliminar.append(ruta_imgs)

            ruta_pdf = os.path.abspath(f"plantilla/reservas/temp/reserva_{idUnico}.pdf")
            log_unir_pdf = Pdf.unir_pdfs(docs_eliminar, ruta_pdf)
            if log_unir_pdf:
                pdf_base64 = Archivos.archivo_a_base64(ruta_pdf)
                if pdf_base64:
                    # docs_eliminar.append(ruta_pdf)
                    # log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                    # if log_eliminar_data:
                        return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": pdf_base64}    
                    # else:
                    #     return {"estado": False, "mensaje": "No se logro crear base64"} 
                else:
                    return {"estado": False, "mensaje": "No se logro eliminar los docs"} 
            else:
                return {"estado": False, "mensaje": "No se logro unir los docs generales"}

    
    @staticmethod
    def generar_portada(datos, idUnico):
        docs_eliminar = []
        if "imagenes" in datos and datos["imagenes"]:
            plantilla_portada = os.path.abspath("plantilla/reservas/plantilla_portada.png")
            portada_original = os.path.abspath("plantilla/reservas/portada.png")
            portada = os.path.abspath(f"plantilla/reservas/temp/portada_{idUnico}.png")
            shutil.copy(portada_original, portada)
            docs_eliminar.append(portada)
            ruta_imagen_descargada = os.path.abspath(f"plantilla/reservas/temp/imagen_portada_{idUnico}.jpeg")
            log_imagen_download = Imagen.download_image(datos["imagenes"]["portada"], ruta_imagen_descargada)
            if log_imagen_download:
                docs_eliminar.append(ruta_imagen_descargada)
                log_imagen = Imagen.colocar_imagen_pequena(ruta_imagen_descargada, (0,500), portada, portada, alto_en_pt=980)
                if log_imagen:
                    log_plantilla = Imagen.colocar_imagen_pequena(plantilla_portada, (0,0), portada, portada)
                    if log_plantilla:
                        log_titulo = Imagen.colocar_texto_a_imagen(
                                        texto=datos["destino"], 
                                        coordenadas=(500, 1550), 
                                        ruta_imagen=portada, 
                                        ruta_salida=portada, 
                                        fuente="BERNHC.TTF", 
                                        tamano=80, 
                                        color="white", 
                                        negrita=True
                                    )
                        log_titulo2 = Imagen.colocar_texto_a_imagen(
                                        texto=datos["pais"], 
                                        coordenadas=(595, 1630), 
                                        ruta_imagen=portada, 
                                        ruta_salida=portada, 
                                        fuente="INFROMAN.TTF", 
                                        tamano=50, 
                                        color="white", 
                                        negrita=True
                                    )
                        if log_titulo and log_titulo2:
                            log_img_pdf = Imagen.resize_image_for_pdf(portada,portada, 596, 841)
                            if log_img_pdf:
                                ruta_portada_pdf = os.path.abspath(f"plantilla/reservas/temp/portada_{idUnico}.pdf")
                                log_pdf = Pdf.imagen_a_pdf(portada,ruta_portada_pdf)
                                if log_pdf:
                                    log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                                    if log_eliminar_data:
                                        return{"estado": True, "mensaje": "Portada creada correctamente", "ruta": ruta_portada_pdf}
                                    else:
                                        return{"estado": False, "mensaje": "No se pudo eliminar los archivos temp de portada"}
                                else:
                                    return {"estado": False, "mensaje": "No se ha podido tranformar de png a pdf."} 
                            else:
                                return {"estado": False, "mensaje": "No se ha podido redimencionar el PNG."} 
                        else:
                            return {"estado": False, "mensaje": "No se ha podido añadir el titulo a la portada."}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido añadir la plantilla del uvas al png general."}
                else:
                    return {"estado": False, "mensaje": "No se ha podido agregar la imagen de portada a la plantilla."} 
            else:
                return {"estado": False, "mensaje": "No se ha podido descargar imagen de portada."} 
        else:
            return {"estado": False, "mensaje": "No hay imagenes"} 




    @staticmethod
    def generar_pdf_imgs(datos, idUnico):
        docs_eliminar = []
        if "imagenes" in datos and datos["imagenes"]:
            docx_original = os.path.abspath("plantilla/reservas/informacion_reservas_fotos.docx")
            docx_fotos = os.path.abspath(f"plantilla/reservas/temp/informacion_reserva_fotos_{idUnico}.docx")
            docs_eliminar.append(docx_fotos)
            shutil.copy(docx_original, docx_fotos)
            metadatos = [
                {"x":1000,"y":170},
                {"x":1800,"y":225},
                {"x":1500,"y":290},
            ]
            for index,imagen in enumerate(datos["imagenes"]["imagenes"]):
                ruta_imagen_descargada = os.path.abspath(f"plantilla/reservas/temp/imagen_hotel_{index}_{idUnico}.jpeg")
                log_imagen_download = Imagen.download_image(imagen, ruta_imagen_descargada)
                if log_imagen_download:
                    docs_eliminar.append(ruta_imagen_descargada)
                    x = metadatos[index % len(metadatos)]["x"]
                    y = metadatos[index % len(metadatos)]["y"]
                    log_cortar_imagen = Imagen.resize_and_crop(ruta_imagen_descargada, width_pt=x,output_path=ruta_imagen_descargada)
                    if log_cortar_imagen:
                        log_imagen_docx = Docx.imagen_en_docx(ruta_imagen_descargada, docx_fotos, (f"[imagen_{index+1}]"),alto_en_pt=y, alineacion="CENTER")
            ruta_directorio_pdf = os.path.abspath("plantilla/reservas/temp")
            ruta_pdf_generado = Pdf.convertir_docx_a_pdf(docx_fotos, ruta_directorio_pdf)
            if ruta_pdf_generado:
                log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                if log_eliminar_data:
                    paginas = Pdf.contar_paginas(ruta_pdf_generado)
                    if paginas and paginas>1:
                        log_pagina_eliminar = Pdf.eliminar_pagina(ruta_pdf_generado, paginas, output_path=ruta_pdf_generado)
                        if log_pagina_eliminar:
                            return{"estado": True, "mensaje": "PDF creados correctamente", "ruta": ruta_pdf_generado}
                        else:
                            return {"estado": False, "mensaje": "No se ha podido eliminar paginas"}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido contar paginas"}
                else:
                        return {"estado": False, "mensaje": "No se ha podido eliminar archivos temp"}
            else:
                return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"}
        else:
            return {"estado": False, "mensaje": "No hay imagenes"}
       
            



 