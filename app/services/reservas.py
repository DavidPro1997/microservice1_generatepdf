import os, shutil
import locale
from app.services.comun import Archivos, Pdf, Docx, Imagen, Api  
import app.logger_config 

locale.setlocale(locale.LC_TIME, "es_ES.utf8")


class Reservas:
    @staticmethod
    def pdf_reseva(data, idUnico):
        docs_unir = []
        if "datos" in data and data["datos"]:
            # rutas_imgs = Reservas.descargar_imagenes(data["datos"],idUnico)
            # if rutas_imgs:
            portada = Reservas.generar_portada_pdf(data["datos"], idUnico)
            if portada["estado"]:
                ruta_portada = portada["ruta"]
                docs_unir.append(ruta_portada)
            cuerpo_hotel = Reservas.generar_pdf_datosHotel(data["datos"], idUnico)
            if cuerpo_hotel["estado"]:
                ruta_cuerpo_dataHotel = cuerpo_hotel["ruta"]
                rutas_imgs_hoteles = cuerpo_hotel["imagenes"]
                docs_unir.append(ruta_cuerpo_dataHotel)
            cuerpo_actividades = Reservas.generar_pdf_actividades(data["datos"], idUnico)
            if cuerpo_actividades["estado"]:
                ruta_actividades = cuerpo_actividades["ruta"]
                ruta_imagenes = cuerpo_actividades["imagenes"]
                docs_unir.append(ruta_actividades)
            imagenes_voucher = Reservas.generar_pdf_img_voucher(data["datos"], rutas_imgs_hoteles ,idUnico)
            if imagenes_voucher["estado"]:
                ruta_img_voucher = imagenes_voucher["ruta"]
                docs_unir.append(ruta_img_voucher)
            politicas = Reservas.generar_pdf_politicas(data["datos"], idUnico)
            if politicas["estado"]:
                ruta_politicas = politicas["ruta"]
                docs_unir.append(ruta_politicas)
            ruta_pdf_tutorial = os.path.abspath(f"plantilla/reservas/plantilla_tutorial.pdf")
            docs_unir.append(ruta_pdf_tutorial)
            ruta_pdf = os.path.abspath(f"plantilla/reservas/temp/reserva_{idUnico}.pdf")
            log_unir_pdf = Pdf.unir_pdfs(docs_unir, ruta_pdf)
            if log_unir_pdf:
                pdf_base64 = Archivos.archivo_a_base64(ruta_pdf)
                if pdf_base64:
                    return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": pdf_base64}    
                else:
                    return {"estado": False, "mensaje": "No se logro eliminar los docs"} 
            else:
                return {"estado": False, "mensaje": "No se logro unir los docs generales"}
            # else:
            #     return {"estado": False, "mensaje": "No se logro descargar las imagenes del cuerpo del pdf"}
            
    
    @staticmethod
    def generar_portada_pdf(datos, idUnico):
        if datos["hoteles"]:
            
            plantilla_portada_original = os.path.abspath(f"plantilla/reservas/destinos/plantilla_portada_destino_{datos['hoteles'][0]['idDestino']}.pdf")
            if os.path.exists(plantilla_portada_original):
                plantilla_portada = os.path.abspath(f"plantilla/reservas/temp/portada_{idUnico}.pdf")
                plantilla_portada_editada = os.path.abspath(f"plantilla/reservas/temp/portada_editada_{idUnico}.pdf")
                shutil.copy(plantilla_portada_original, plantilla_portada)
                estilos = ["helv", 18, (255, 255, 255)]
                x, texto = Pdf.centrar_texto(datos["cliente"], "helv",18)
                log_nombre_portada = Pdf.editar_pdf(plantilla_portada,plantilla_portada_editada, texto.upper(), x, 800, estilos) 
                if log_nombre_portada:
                    return{"estado": True, "mensaje": "Portada creada correctamente", "ruta": plantilla_portada_editada}
                else:
                    return {"estado": False, "mensaje": "No se ha podido ingresar el nombre en el pdf de la portada"}
            else:
                return {"estado": False, "mensaje": "La plantilla de portada no existe"}
        else:
                return {"estado": False, "mensaje": "No hay hoteles"}
    

    @staticmethod
    def generar_portada_img(datos, idUnico):
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
    def generar_pdf_datosHotel(datos ,idUnico):    
        docx_original = os.path.abspath("plantilla/reservas/plantilla_reserva_datoshotel.docx")
        docs_unir = []
        for index, dataHotel in enumerate(datos["hoteles"]):
            docx_datahotel = os.path.abspath(f"plantilla/reservas/temp/plantilla_reserva_datoshotel_{index}_{idUnico}.docx")
            shutil.copy(docx_original, docx_datahotel)
            url = (f"https://apirest.mvevip.com/api/hotelbeds/booking/hotel-info/{dataHotel['idHotel']}")
            hotel = Api.llamar_api_get(url)
            if hotel["consulta"]:
                url_imgs = []
                for index, img in enumerate(hotel["consulta"]["images"]):
                    url_imgs.append(img[len(img)-1])
                    if len(url_imgs) >= 4:
                        break
                img_rutas = Reservas.descargar_imagenes(url_imgs, idUnico)
                metadatos = [
                    {"x":1100,"y":180},
                    {"x":1950,"y":170},
                    {"x":1550,"y":195},
                    {"x":1550,"y":220},
                ]
                log_imgs = Reservas.generar_docx_imgs(docx_datahotel,img_rutas, metadatos)
                if log_imgs:
                    telefonos = ""
                    if hotel["consulta"]["phones"]:
                        telefonos = " - ".join([phone["phone_number"] for phone in hotel["consulta"]["phones"][:2]])
                    data = {
                        "idReserva": datos["idReserva"],
                        "cliente": datos["cliente"],
                        "reservado": datos["reservado"],
                        "nombre_hotel": hotel["consulta"].get("name", ""),
                        "ciudad": hotel["consulta"]["location"].get("city", "").capitalize() if "location" in hotel["consulta"] else "",
                        "telefonos": telefonos,
                        "location": (f"{hotel['consulta']['location'].get('address', '').capitalize()}"),
                    }
                    google_maps = (f"https://www.google.com/maps?q={hotel['consulta']['location'].get('latitude', '')},{hotel['consulta']['location'].get('longitude', '')}") if "location" in hotel["consulta"] else ""
                    dataHotel.update(data)
                    dataHotel["comentarios"] = Archivos.truncar_texto(dataHotel["comentarios"], 80) 
                    ruta_directorio_pdf = os.path.abspath("plantilla/reservas/temp")
                    estilos_tabla = {"fuente": "Helvetica", "numero":10, "color": "#404040"}
                    log_reemplazar_dataHotel = Docx.reemplazar_texto_tablas(docx_datahotel, docx_datahotel, dataHotel, estilos_tabla, alineacion="JUSTIFY")
                    if log_reemplazar_dataHotel:
                        estilos_hipervinvulo = {"fuente": "Helvetica", "numero":10, "color": "#4472C4"}
                        log_hiperviculo = Docx.reemplazar_con_hipervinculo(docx_datahotel, docx_datahotel, "[google_maps]", google_maps, "Ver ubicación en google mapas", estilos_hipervinvulo, alineacion="JUSTIFY")
                        if log_hiperviculo:
                            ruta_pdf_generado = Pdf.convertir_docx_a_pdf(docx_datahotel, ruta_directorio_pdf)
                            if ruta_pdf_generado:
                                paginas = Pdf.contar_paginas(ruta_pdf_generado)
                                if paginas and paginas>1:
                                    Pdf.eliminar_pagina(ruta_pdf_generado, paginas, output_path=ruta_pdf_generado)
                                docs_unir.append(ruta_pdf_generado)
                            else:
                                return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"}
                        else:
                            return {"estado": False, "mensaje": "No se ha podido añadir el hipervinculo"}
                    else:
                            return {"estado": False, "mensaje": "No se ha podido reemplazar los datos"}
                else:
                    return {"estado": False, "mensaje": "No se ha logrado añadir las imagenes seleccionadas"}
            else:
                return {"estado": False, "mensaje": "La api no ha respondido correctamente"}
        ruta_pdf = os.path.abspath(f"plantilla/reservas/temp/reserva_datoshotel_{idUnico}.pdf")
        log_unir_pdf = Pdf.unir_pdfs(docs_unir, ruta_pdf)
        if log_unir_pdf:
            return{"estado": True, "mensaje": "PDF creados correctamente", "ruta": ruta_pdf, "imagenes": img_rutas}
        else:
            return {"estado": False, "mensaje": "No se ha podido unir los pdfs"}
        
       
    @staticmethod
    def generar_pdf_rooms(datos, ruta_imgs, idUnico):
        docx_original = os.path.abspath("plantilla/reservas/plantilla_reservas_rooms.docx")
        docs_unir = []
        for index, room in enumerate(datos["reserva"]["rooms"]):
            docx_rooms = os.path.abspath(f"plantilla/reservas/temp/plantilla_reservas_rooms_{index}_{idUnico}.docx")
            shutil.copy(docx_original, docx_rooms)
            metadatos = [
            {"x":1100,"y":160},
            {"x":1950,"y":235},
            {"x":1550,"y":310},
        ]
            log_imgs = Reservas.generar_docx_imgs(docx_rooms,ruta_imgs, metadatos)
            if log_imgs:
                ruta_directorio_pdf = os.path.abspath("plantilla/reservas/temp")
                estilos_tabla = {"fuente": "Helvetica", "numero":10}
                log_reemplazar_dataHotel = Docx.reemplazar_texto_tablas(docx_rooms, docx_rooms, room, estilos_tabla)
                if log_reemplazar_dataHotel:
                    ruta_pdf_generado = Pdf.convertir_docx_a_pdf(docx_rooms, ruta_directorio_pdf)
                    if ruta_pdf_generado:
                        paginas = Pdf.contar_paginas(ruta_pdf_generado)
                        if paginas and paginas>1:
                            log_pagina_eliminar = Pdf.eliminar_pagina(ruta_pdf_generado, paginas, output_path=ruta_pdf_generado)
                            if log_pagina_eliminar:
                                docs_unir.append(ruta_pdf_generado)
                            else:
                                return {"estado": False, "mensaje": "No se ha podido eliminar la pagina extra del documento rooms"}
                        else:
                            return {"estado": False, "mensaje": "No se ha podido contar las paginas del documento rooms"}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido reemplazar los datos del documento rooms"}
                else:
                    return {"estado": False, "mensaje": "No se ha podido reemplazar los datos"}
            else:
                    return {"estado": False, "mensaje": "No se ha podido añadir las imagenes en el documeto rooms"}
            
        ruta_pdf = os.path.abspath(f"plantilla/reservas/temp/reserva_rooms_{idUnico}.pdf")
        log_unir_pdf = Pdf.unir_pdfs(docs_unir, ruta_pdf)
        if log_unir_pdf:
            return{"estado": True, "mensaje": "PDF creados correctamente", "ruta": ruta_pdf}
        else:
            return {"estado": False, "mensaje": "No se ha podido unir los pdfs"}


    @staticmethod
    def generar_pdf_actividades(datos,idUnico):
        if "actividades" in datos and datos["actividades"]:
            resultado = {}
            images_url = []
            url = (f"https://apirest.mvevip.com/api/civitatis/actividades/{datos['actividades'][0]['idDestino']}")
            actividades = Api.llamar_api_get(url)
            if actividades["consulta"]:
                for acti in actividades["consulta"]:
                    if "photos" in acti and "header" in acti["photos"] and acti["photos"]["gallery"]:
                        images_url.append(acti["photos"]["gallery"][0]["paths"]["original"])
                        if len(images_url) >= 4:
                            break
                imagenes_actividades = Reservas.descargar_imagenes(images_url, idUnico)
            for index, act in enumerate(datos["actividades"]):
                data = {
                    f"destino_{index}": act["destino"],
                    f"actividad_{index}": act["nombre"],
                    f"fecha_{index}": act["fecha"],
                    # f"hora_{index}": act["hora"]
                }
                resultado.update(data)
            docx_original = os.path.abspath("plantilla/reservas/plantilla_reserva_servicios.docx")
            docx_actividades = os.path.abspath(f"plantilla/reservas/temp/plantilla_reserva_servicios_{idUnico}.docx")
            shutil.copy(docx_original, docx_actividades)
            estilos_tabla = {"fuente": "Helvetica", "numero":10, "color": "#404040"}
            log_reemplazar_act = Docx.reemplazar_texto_tabla_anidada(docx_actividades, docx_actividades, resultado, estilos_tabla, 0, 9, 0, alineacion="JUSTIFY")
            if log_reemplazar_act:
                info = {
                    "cliente": datos["cliente"],
                    "idReserva": datos["idReserva"]
                }
                log_reemplazar_actividad = Docx.reemplazar_texto_tablas(docx_actividades, docx_actividades, info, estilos_tabla, alineacion="JUSTIFY")
                if log_reemplazar_actividad:
                    filas = list(range(len(datos["actividades"]) + 1, 12))
                    log_elminar_filas = Docx.eliminar_filas_docx(docx_actividades, docx_actividades, filas, 0, numero_fila = 9, numero_celda = 0, numero_tabla_anidada = 0)
                    if log_elminar_filas:
                        metadatos = [
                            {"x":1000,"y":165},
                            {"x":1000,"y":175},
                            {"x":1000,"y":197},
                            {"x":1000,"y":240},
                        ]
                        log_imgs = Reservas.generar_docx_imgs(docx_actividades, imagenes_actividades, metadatos)
                        if log_imgs:
                            ruta_directorio_pdf = os.path.abspath("plantilla/reservas/temp")
                            ruta_pdf_generado = Pdf.convertir_docx_a_pdf(docx_actividades, ruta_directorio_pdf)
                            if ruta_pdf_generado:
                                paginas = Pdf.contar_paginas(ruta_pdf_generado)
                                if paginas and paginas>1:
                                    Pdf.eliminar_pagina(ruta_pdf_generado, paginas, output_path=ruta_pdf_generado)
                                return{"estado": True, "mensaje": "PDF creados correctamente", "ruta": ruta_pdf_generado, "imagenes": imagenes_actividades}
                            else:
                                return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"}
                        else:
                            return {"estado": False, "mensaje": "No se ha podido colocar las imagenes en el documento itinerario"}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido eiminar las filas del docx de servicios adicionales"}
                else:
                        return {"estado": False, "mensaje": "No se ha podido reemplazar texto en docs actividades"}
            else:
                return {"estado": False, "mensaje": "No se ha podido reemplazar los datos"}
        else:
            return {"estado": False, "mensaje": "No hay actividades"} 
        

    @staticmethod
    def generar_pdf_img_voucher(datos, rutas_imgs ,idUnico):
        if "imgBase64" in datos and datos["imgBase64"]:
            rutas_imagenes_pdf = []
            ruta_plantilla_imagen = os.path.abspath("plantilla/reservas/plantilla_reserva_vouchers.docx")
            for indice, recibo in enumerate(datos["imgBase64"]):
                ruta_imagen_docx = os.path.abspath(f"plantilla/reservas/temp/plantilla_reserva_vouchers_{indice}_{idUnico}.docx")
                shutil.copy(ruta_plantilla_imagen, ruta_imagen_docx)
                metadatos = [
                    {"x":1100,"y":180},
                    {"x":1950,"y":188},
                    {"x":1550,"y":185},
                    {"x":1550,"y":220},
                ]
                log_imgs = Reservas.generar_docx_imgs(ruta_imagen_docx,rutas_imgs, metadatos)
                if log_imgs:
                    data = {
                        "cliente": datos["cliente"],
                        "idReserva": datos["idReserva"],
                        "reservado": datos["reservado"]
                    }
                    estilos_tabla = {"fuente": "Helvetica", "numero":10, "color": "#404040"}
                    log_reemplazar_dataHotel = Docx.reemplazar_texto_tablas(ruta_imagen_docx, ruta_imagen_docx, data, estilos_tabla, alineacion="JUSTIFY")
                    if log_reemplazar_dataHotel:
                        ruta_imagen_aux = os.path.abspath(f"plantilla/reservas/temp/recibo_{indice}_{idUnico}")
                        ruta_imagen = Imagen.guardar_imagen_base64(recibo, ruta_imagen_aux)
                        if ruta_imagen:
                            log_imagen_docs = Docx.imagen_en_docx(ruta_imagen, ruta_imagen_docx,"[imagen_voucher]" , 450)
                            if log_imagen_docs:
                                ruta_directorio_pdf_imagen = os.path.abspath("plantilla/reservas/temp")
                                ruta_imagen_pdf = Pdf.convertir_docx_a_pdf(ruta_imagen_docx,ruta_directorio_pdf_imagen)
                                if ruta_imagen_pdf:
                                    paginas = Pdf.contar_paginas(ruta_imagen_pdf)
                                    if paginas and paginas>1:
                                        Pdf.eliminar_pagina(ruta_imagen_pdf, paginas, output_path=ruta_imagen_pdf)
                                    rutas_imagenes_pdf.append(ruta_imagen_pdf)
                                else:
                                    return {"estado": False, "mensaje": "Hubo un error al tranformar imagenes a pdf"}  
                            else:
                                return {"estado": False, "mensaje": "Hubo un error al insertar las imagenes en el documento"}
                        else:
                            return {"estado": False, "mensaje": "Hubo un error con las imagenes adjuntadas"}
                    else:
                        return {"estado": False, "mensaje": "Hubo un error insertar textos en el pdf de recibo"}
                else:
                    return {"estado": False, "mensaje": "Hubo un error al insertar imagenes laterales en el pdf de recibos"}
            ruta_imagenes_unidas_pdf = os.path.abspath(f"plantilla/reservas/temp/imagenes_{idUnico}.pdf")
            log_unir_imagenes = Pdf.unir_pdfs(rutas_imagenes_pdf, ruta_imagenes_unidas_pdf)
            if log_unir_imagenes:
                return {"estado": True, "mensaje": "Se proceso bien las imagenes", "ruta":ruta_imagenes_unidas_pdf}
            else:
                return {"estado": False, "mensaje": "Hubo un error al unir las imagenes"}
        else:
            return {"estado": False, "mensaje": "No hay recibos de pago"}



    @staticmethod
    def generar_pdf_politicas(datos, idUnico):
        ruta_plantilla_politicas = os.path.abspath("plantilla/reservas/plantilla_reservas_politicas.docx")
        docx_unidos = []
        for index, destino in enumerate(datos["politicas"]):
            ruta_politicas_docx = os.path.abspath(f"plantilla/reservas/temp/plantilla_reservas_politicas_{index}_{idUnico}.docx")
            shutil.copy(ruta_plantilla_politicas, ruta_politicas_docx)
            aux = {}
            for indice, politica in enumerate(destino["politicas"]):
                data = {
                    (f"politicas_{indice+1}"): politica
                    }
                aux.update(data)
            estilos_tabla = {"fuente": "Helvetica", "numero":10, "color": "#404040"}
            estilos_titulo = {"fuente": "Helvetica", "numero":50, "color": "#404040"}
            info = {
                "destino": destino["destino"],
            }
            log_reemplazar_titulo = Docx.reemplazar_texto_parrafos(ruta_politicas_docx, ruta_politicas_docx, info, estilos_titulo, alineacion="CENTER")
            if log_reemplazar_titulo:
                log_reemplazar_politicas = Docx.reemplazar_texto_tablas(ruta_politicas_docx, ruta_politicas_docx, aux, estilos_tabla, alineacion="JUSTIFY")
                if log_reemplazar_politicas:
                    filas = list(range(len(destino["politicas"]) + 0, 15))
                    log_elminar_filas = Docx.eliminar_filas_docx(ruta_politicas_docx, ruta_politicas_docx, filas, 0)
                    if log_elminar_filas:
                        ruta_directorio_pdf = os.path.abspath("plantilla/reservas/temp")
                        ruta_pdf_generado = Pdf.convertir_docx_a_pdf(ruta_politicas_docx, ruta_directorio_pdf)
                        if ruta_pdf_generado:
                            docx_unidos.append(ruta_pdf_generado)
                        else:
                            return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf en el doc de politicas"}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido eliminar las filas extra del docx de politicas"}
                else:
                    return {"estado": False, "mensaje": "No se ha podido reemplazar los dartos en el docx de politicas"}
            else:
                    return {"estado": False, "mensaje": "No se ha podido reemplazar el titulo en el docx de politicas"}
        ruta_pdf = os.path.abspath(f"plantilla/reservas/temp/reserva_politicas_{idUnico}.pdf")
        log_unir_pdf = Pdf.unir_pdfs(docx_unidos, ruta_pdf)
        if log_unir_pdf:
            return{"estado": True, "mensaje": "PDF creados correctamente", "ruta": ruta_pdf}
        else:
            return {"estado": False, "mensaje": "No se ha podido unir los pdfs"}



    @staticmethod
    def generar_docx_imgs(docx_fotos, ruta_imgs, metadatos):
        for index,imagen in enumerate(ruta_imgs):
            x = metadatos[index % len(metadatos)]["x"]
            y = metadatos[index % len(metadatos)]["y"]
            # log_cortar_imagen = Imagen.resize_and_crop(imagen, height_pt=y, output_path=imagen)
            # if log_cortar_imagen:
            log_imagen_docx = Docx.imagen_en_docx(imagen, docx_fotos, (f"[imagen_{index+1}]"),alto_en_pt=y, alineacion="LEFT")
            if not log_imagen_docx:
                return False
        return True
       

    @staticmethod
    def descargar_imagenes(imagenes, idUnico):
        imagenPredefinida1 = os.path.abspath(f"img/hoteles/imagen_hotel_1.jpeg")
        imagenPredefinida2 = os.path.abspath(f"img/hoteles/imagen_hotel_2.jpeg")
        imagenPredefinida3 = os.path.abspath(f"img/hoteles/imagen_hotel_3.jpeg")
        imagenPredefinida4 = os.path.abspath(f"img/hoteles/imagen_hotel_4.jpeg")
        ruta_imgs = [imagenPredefinida1,imagenPredefinida2,imagenPredefinida3,imagenPredefinida4]
        for index,imagen in enumerate(imagenes):
            ruta_imagen_descargada = os.path.abspath(f"plantilla/reservas/temp/imagen_hotel_{index}_{idUnico}.jpeg")
            log_imagen_download = Imagen.download_image(imagen, ruta_imagen_descargada)
            if log_imagen_download:
                ruta_imgs[index] = ruta_imagen_descargada
        return ruta_imgs
