import os, shutil
from datetime import datetime
import locale
from app.services.comun import Archivos, Pdf, Docx, Imagen, Api  

locale.setlocale(locale.LC_TIME, "es_ES.utf8")



class Cotizador:
    @staticmethod
    def cotizar_completo(data, idUnico):
        docs_eliminar = []
        incluye = []
        if "hotel" in data and data["hotel"]:
            ciudad = "\n".join(set(item["city"] for item in data["hotel"]))
            # opcion1
            if "vuelo" in data and data["vuelo"]:
                ticket = "Si incluye ticket aéreo"
                portada = Cotizador.generarPDFPortada(ciudad, idUnico)
                if portada["estado"]:
                    ruta_portada = portada["ruta"]
                    docs_eliminar.append(ruta_portada)
                log_paquete = Hotel.generar_pdf_paquete(data["hotel"], data["actividades"], ticket, idUnico)
                if log_paquete["estado"]:
                    ruta_paquete = log_paquete["ruta"]
                    docs_eliminar.append(ruta_paquete)
                vuelos = Cotizador.cotizar_vuelos(data["vuelo"], idUnico)
                if vuelos["estado"]:
                    incluye.append("tickets aéreos")
                    ruta_vuelos = vuelos["ruta"]
                    docs_eliminar.append(ruta_vuelos)
                log_hotel = Hotel.generar_pdf_hotel(data["hotel"], idUnico)
                if log_hotel["estado"]:
                    incluye.append("hospedaje")
                    ruta_hotel = log_hotel["ruta"]
                    docs_eliminar.append(ruta_hotel)
                if "actividades" in data and data["actividades"]:
                    log_actividades = Actividad.generarPdfActividades(data["actividades"], idUnico)
                    if log_actividades["estado"]:
                        incluye.append("actividades")
                        ruta_actividades = log_actividades["ruta"]
                        docs_eliminar.append(ruta_actividades)
                if "costos" in data and data["costos"]:
                    costos = Costos.generarPdfCostos(data["costos"], incluye, idUnico)
                    if costos["estado"]:
                        ruta_costos = costos["ruta"]
                        docs_eliminar.append(ruta_costos)
                
            # opcion2
            else:
                ticket = "No incluye ticket aéreo"
                portada = Cotizador.generarPDFPortada(ciudad, idUnico)
                if portada["estado"]:
                    ruta_portada = portada["ruta"]
                    docs_eliminar.insert(0, ruta_portada)
                log_paquete = Hotel.generar_pdf_paquete(data["hotel"], data["actividades"] ,ticket, idUnico)
                if log_paquete["estado"]:
                    ruta_paquete = log_paquete["ruta"]
                    docs_eliminar.append(ruta_paquete)
                log_hotel = Hotel.generar_pdf_hotel(data["hotel"], idUnico)
                if log_hotel["estado"]:
                    incluye.append("hospedaje")
                    ruta_hotel = log_hotel["ruta"]
                    docs_eliminar.append(ruta_hotel)
                if "actividades" in data and data["actividades"]:
                    log_actividades = Actividad.generarPdfActividades(data["actividades"], idUnico)
                    if log_actividades["estado"]:
                        incluye.append("actividades")
                        ruta_actividades = log_actividades["ruta"]
                        docs_eliminar.append(ruta_actividades)
                if "costos" in data and data["costos"]:
                    costos = Costos.generarPdfCostos(data["costos"], incluye, idUnico)
                    if costos["estado"]:
                        ruta_costos = costos["ruta"]
                        docs_eliminar.append(ruta_costos)

        else:
            # opcion3
            if "vuelo" in data and data["vuelo"]:
                personas = {"pasajeros": data["vuelo"]["personas"].replace(",", "\n")}
                ticket = "Si incluye ticket(s) aéreo(s)"
                ciudad = "\n".join(item[f"ciudad_destino{index}"].split(",")[0] for index, item in enumerate(data["vuelo"]["segmentos"]) if index < len(data["vuelo"]["segmentos"]) - 1)
                portada = Cotizador.generarPDFPortada(ciudad, idUnico)
                if portada["estado"]:
                    ruta_portada = portada["ruta"]
                    docs_eliminar.append(ruta_portada)
                log_paquete = Hotel.generar_pdf_paquete(data["hotel"], data["actividades"], ticket,idUnico, ciudad, personas)
                if log_paquete["estado"]:
                    ruta_paquete = log_paquete["ruta"]
                    docs_eliminar.append(ruta_paquete)
                vuelos = Cotizador.cotizar_vuelos(data["vuelo"], idUnico)
                if vuelos["estado"]:
                    incluye.append("tickets aéreos")
                    ruta_vuelos = vuelos["ruta"]
                    docs_eliminar.append(ruta_vuelos)
                if "actividades" in data and data["actividades"]:
                    log_actividades = Actividad.generarPdfActividades(data["actividades"], idUnico)
                    if log_actividades["estado"]:
                        incluye.append("actividades")
                        ruta_actividades = log_actividades["ruta"]
                        docs_eliminar.append(ruta_actividades)
                if "costos" in data and data["costos"]:
                    costos = Costos.generarPdfCostos(data["costos"], incluye, idUnico)
                    if costos["estado"]:
                        ruta_costos = costos["ruta"]
                        docs_eliminar.append(ruta_costos)
            # opcion4
            else:
                return{"estado": False, "mensaje": "No hay datos de vuelos ni paquetes"}
        
        ruta_pdf = os.path.abspath(f"plantilla/cotizaciones/temp/cotizacion_completo_{idUnico}.pdf")
        log_unir_pdf = Pdf.unir_pdfs(docs_eliminar, ruta_pdf)
        if log_unir_pdf:
            pdf_base64 = Archivos.archivo_a_base64(ruta_pdf)
            if pdf_base64:
                docs_eliminar.append(ruta_pdf)
                log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                if log_eliminar_data:
                    return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": pdf_base64}    
                else:
                    return {"estado": False, "mensaje": "No se logro crear base64"} 
            else:
                return {"estado": False, "mensaje": "No se logro eliminar los docs"} 
        else:
            return {"estado": False, "mensaje": "No se logro unir los docs generales"}
    

    
    @staticmethod
    def generarPDFPortada(ciudad, idUnico):
        if ciudad:
            datos={
                "city": ciudad.upper()
            }
            docs_eliminar = []
            ruta_plantilla_portada_original = os.path.abspath("plantilla/cotizaciones/plantilla_cotizar_portada.docx")
            ruta_plantilla_portada = os.path.abspath(f"plantilla/cotizaciones/temp/plantilla_cotizar_portada_{idUnico}.docx")
            docs_eliminar.append(ruta_plantilla_portada)
            shutil.copy(ruta_plantilla_portada_original, ruta_plantilla_portada)
            ruta_docx_generado_portada = os.path.abspath(f"plantilla/cotizaciones/temp/portada_{idUnico}.docx")
            docs_eliminar.append(ruta_docx_generado_portada)
            longitud = len(ciudad)
            if longitud < 10:
                estilos = {"fuente": "Helvetica", "numero":60, "color": "#FFFFFF"}
            else:
                estilos = {"fuente": "Helvetica", "numero":40, "color": "#FFFFFF"}
            log_reemplazar_cotitazion = Docx.reemplazar_texto_parrafos(ruta_plantilla_portada, ruta_docx_generado_portada, datos, estilos, "CENTER")
            if log_reemplazar_cotitazion:
                ruta_directorio_pdf = os.path.abspath("plantilla/cotizaciones/temp")
                ruta_pdf_generado = Pdf.convertir_docx_a_pdf(ruta_docx_generado_portada, ruta_directorio_pdf)
                if ruta_pdf_generado:
                    log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                    if log_eliminar_data:
                        return{"estado": True, "mensaje": "Costos creados correctamente", "ruta": ruta_pdf_generado}
                else:
                    return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"} 
            else:
                return {"estado": False, "mensaje": "No se ha podido reemplazar docx"} 
        else:
            return {"estado": False, "mensaje": "No hay datos de ciudad"} 



    @staticmethod
    def cotizar_vuelos(data, idUnico):
        if data:
            docs_eliminar = []
            numero_segmentos = len(data["segmentos"])
            ruta_plantilla_cotizador_vuelos = os.path.abspath(f"plantilla/cotizaciones/plantilla_cotizar_vuelos_{numero_segmentos}.docx")
            ruta_docx_generado_cotizacion_vuelos_segmento = os.path.abspath(f"plantilla/cotizaciones/temp/cotizacion_vuelos_seg_{idUnico}.docx")
            docs_eliminar.append(ruta_docx_generado_cotizacion_vuelos_segmento)
            shutil.copy(ruta_plantilla_cotizador_vuelos, ruta_docx_generado_cotizacion_vuelos_segmento)
            if numero_segmentos <= 2:
                estilos_tabla = {"fuente": "Helvetica", "numero":10}
            else:
                estilos_tabla = {"fuente": "Helvetica", "numero":7}
            aux = True
            resultado = {}
            for index, segmento in enumerate(data["segmentos"]):
                variable = (f"[detalle_vuelo{index}]")
                detalle_vuelo = segmento[f"detalle_vuelo{index}"]
                log_vuelos_legs = Docx.armar_tabla_vuelos(ruta_docx_generado_cotizacion_vuelos_segmento, ruta_docx_generado_cotizacion_vuelos_segmento,variable,detalle_vuelo ,estilos_tabla)
                if not log_vuelos_legs:
                    aux = False
                if variable in segmento:  # Verifica si la clave existe en el diccionario
                    segmento.pop(variable)
                resultado.update(segmento)
            if aux:
                data.pop("segmentos")
                resultado.update(data)
                ruta_aereolina_imagen = os.path.abspath(f"img/aereolinas_logos/{data['aereolina'].lower()}.png")
                if os.path.exists(ruta_aereolina_imagen):
                    Docx.imagen_en_docx(ruta_aereolina_imagen, ruta_docx_generado_cotizacion_vuelos_segmento, "[imagen_aereolina]", alto_en_pt=17)
                else:
                    resultado["imagen_aereolina"] = ""
                log_reemplazar_cotitazion = Docx.reemplazar_texto_tablas(ruta_docx_generado_cotizacion_vuelos_segmento, ruta_docx_generado_cotizacion_vuelos_segmento, resultado, estilos_tabla)
                if log_reemplazar_cotitazion:
                    ruta_directorio_pdf = os.path.abspath("plantilla/cotizaciones/temp")
                    ruta_pdf_cotizacion_vuelos = Pdf.convertir_docx_a_pdf(ruta_docx_generado_cotizacion_vuelos_segmento, ruta_directorio_pdf)
                    if ruta_pdf_cotizacion_vuelos:
                        log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                        if log_eliminar_data:
                            return {"estado": True, "mensaje": "Documento creado exitosamente", "ruta": ruta_pdf_cotizacion_vuelos}    
                        else:
                            return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares al crear los vuelos"}
                    else:
                        return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"} 
                else:
                    return {"estado": False, "mensaje": "No se ha posido reemplazar los datos en la plantilla"}
            else:
                return {"estado": False, "mensaje": "No se ha posido reemplazar las escalas en la plantilla"}   
        else:
            return {"estado": False, "mensaje": "No hay datos en el body"}  
      
      

class Hotel:    
    @staticmethod
    def generar_pdf_paquete(dataHotel, actividades, ticket, idUnico, ciudad=None, personas = None):        
        docs_eliminar = []
        if dataHotel:
            numero_hoteles = len(dataHotel)
            if numero_hoteles <= 2:
                estilos = {"fuente": "Helvetica", "numero":12}
            elif numero_hoteles == 3:
                estilos = {"fuente": "Helvetica", "numero":9}
            elif numero_hoteles == 4:
                estilos = {"fuente": "Helvetica", "numero":7}
            else:
                return {"estado": False, "mensaje": "Ha excedido el numero de hoteles"}
            ruta_plantilla_paquete = os.path.abspath(f"plantilla/cotizaciones/plantilla_cotizar_paquete_{numero_hoteles}.docx")
            ruta_docx_generado_paquete = os.path.abspath(f"plantilla/cotizaciones/temp/cotizacion_paquete_{idUnico}.docx")
            shutil.copy(ruta_plantilla_paquete, ruta_docx_generado_paquete)
            docs_eliminar.append(ruta_docx_generado_paquete)
            resultado = {}
            for index, hotel in enumerate(dataHotel):
                role = (f"Eres un extractor de información. Devuelve solo las instalaciones y servicios de un hotel en formato JSON, sin explicaciones adicionales.")
                mensaje = (f"Texto del hotel: {hotel['descripcion']}. Devuelve las facilities en array de un solo nievel, con la primera letra en mayusculas, llamado instalaciones_y_servicios, si no encuentras devuelve vacio. Si encuentas muchas facilities saca solo las 15 mas relevantes.")
                facilities = Api.open_ai(role, mensaje)
                facilities_text = "\n".join(f"•  {item}" for item in facilities["instalaciones_y_servicios"])
                habitaciones = ""
                act = ""
                adultos = 0
                ninos = 0
                dias = Hotel.calcular_dias_noches(hotel["check_in"], hotel["check_out"])
                for room in hotel["rooms"]:
                    role = (f"Eres un traductor de información de habitaciones. Devuelve la traducción en formato JSON, sin explicaciones adicionales.")
                    mensaje = (f"Texto a traducion: {room['board_basis']}. Devuelve lo que incluye la habitacion en español y en JSON asi: habitacion: (lo que incluye), con la primera letra en mayusculas, no aumentes mas informacion de la que esta.")
                    pension = Api.open_ai(role, mensaje)
                    adultos = adultos + (int(room["adults"])*int(room["room_number"]))
                    ninos = ninos + (int(room["children"])*int(room["room_number"]))
                    if 'habitacion' in pension:
                        detalle_habitacion = (f"•  {room['room_number']} habitacion(es) {room['acomodation'].lower()}\n•  {pension['habitacion']}.")
                    else:
                        detalle_habitacion = (f"•  {room['room_number']} habitacion(es) {room['acomodation'].lower()}.")
                    habitaciones += detalle_habitacion
                    if room != hotel["rooms"][-1]:
                        habitaciones += "\n"
                for item in actividades:
                    if item["codigo"] == hotel["city_code"]:
                        act = "\n".join(f"•  {tour['nombre']}" if tour['nombre'] != "Transfer" else "•  Transfer - in\n•  Transfer - out" for tour in item["tours"])
                        break  # Romper el ciclo si ya se encuentra el id
                if not act:  # Verifica si está vacío
                    act = "•  No incluye actividades"
                pax = "" 
                if adultos>=1: pax += (f"{adultos} adulto(s)")
                if ninos>=1: pax += (f"\n{ninos} niños(s)")
                detalle = (f"•  {dias['dias']} dias y {dias['noches']} noches\n•  Check-in: {hotel['check_in']}\n•  Check-out: {hotel['check_out']}")
                datos = {
                    f"pasajeros{index}": pax,
                    f"city{index}": (f"•  {hotel['city']}"),
                    f"detalle{index}": detalle,
                    f"ticket{index}": (f"•  {ticket}"),
                    f"actividades{index}": act,
                    f"habitacion{index}": habitaciones,
                    f"facilities{index}": facilities_text
                }
                resultado.update(datos)
        else:
            ruta_plantilla_paquete = os.path.abspath(f"plantilla/cotizaciones/plantilla_cotizar_paquete_0.docx")
            ruta_docx_generado_paquete = os.path.abspath(f"plantilla/cotizaciones/temp/cotizacion_paquete_{idUnico}.docx")
            shutil.copy(ruta_plantilla_paquete, ruta_docx_generado_paquete)
            estilos = {"fuente": "Helvetica", "numero":12}
            docs_eliminar.append(ruta_docx_generado_paquete)
            act = ""
            if actividades:
                act = "\n".join(f"{tour['nombre']} - {item['ciudad']}" for item in actividades for tour in item["tours"])
            else:
                act = "No incluye actividades" 
            resultado = {
                "city": ciudad,
                "ticket": ticket,
                "actividades": act
            }
            resultado.update(personas)
        log_reemplazar_paquete = Docx.reemplazar_texto_tablas(ruta_docx_generado_paquete,ruta_docx_generado_paquete, resultado, estilos)
        if log_reemplazar_paquete:
            ruta_directorio_pdf = os.path.abspath("plantilla/cotizaciones/temp")
            ruta_pdf_cotizacion_paquete = Pdf.convertir_docx_a_pdf(ruta_docx_generado_paquete, ruta_directorio_pdf)
            if ruta_pdf_cotizacion_paquete:
                log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                if log_eliminar_data:
                    return {"estado": True, "mensaje": "Documento creado exitosamente", "ruta": ruta_pdf_cotizacion_paquete} 
            else:
                return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"}                     
        else:
            return {"estado": False, "mensaje": "No se ha podido reemplazar docx"}

            
        

    @staticmethod
    def generar_pdf_hotel(dataHotel, idUnico):
        if dataHotel:
            docs_eliminar = []
            docs_unir = []
            ruta_plantilla_hotel_original = os.path.abspath("plantilla/cotizaciones/plantilla_cotizar_hoteles.docx")
            ruta_plantilla_hotel = os.path.abspath(f"plantilla/cotizaciones/temp/plantilla_cotizar_hoteles_{idUnico}.docx")
            shutil.copy(ruta_plantilla_hotel_original, ruta_plantilla_hotel)
            docs_eliminar.append(ruta_plantilla_hotel)
            estilos = {"fuente": "Helvetica", "numero":12}
            aux = True
            for index, hotel in enumerate(dataHotel):
                ruta_docx_generado_hotel = os.path.abspath(f"plantilla/cotizaciones/temp/cotizacion_hotel_{index}_{idUnico}.docx")
                facilidades = ", ".join(hotel["facilities"]) + "."
                datos = {
                    "nombre_hotel": hotel["hotel_name"],
                    "descripcion": Archivos.truncar_texto(hotel["descripcion"],175),
                    "ciudad_hotel": hotel["city"],
                    "facilities": facilidades
                }
                log_reemplazar_paquete = Docx.reemplazar_texto_parrafos(ruta_plantilla_hotel,ruta_docx_generado_hotel, datos, estilos)
                docs_eliminar.append(ruta_docx_generado_hotel)
                if log_reemplazar_paquete:
                    ruta_imagen_descargada = os.path.abspath(f"plantilla/cotizaciones/temp/imagen_hotel_{index}_{idUnico}.jpeg")
                    ruta_imagen = hotel["imagen"]
                    log_descargar_imagen = Imagen.download_image(ruta_imagen, ruta_imagen_descargada)
                    if not log_descargar_imagen:
                        ruta_imagen_descargada = os.path.abspath(f"img/mkv.jpg")
                    else:
                        docs_eliminar.append(ruta_imagen_descargada)
                    log_imagen_docx = Docx.imagen_en_docx(ruta_imagen_descargada, ruta_docx_generado_hotel, "[imagen_hotel]", alto_en_pt=230)
                    if log_imagen_docx:
                        ruta_directorio_pdf = os.path.abspath("plantilla/cotizaciones/temp")
                        ruta_pdf_cotizacion_hotel = Pdf.convertir_docx_a_pdf(ruta_docx_generado_hotel, ruta_directorio_pdf)
                        if ruta_pdf_cotizacion_hotel:
                            docs_eliminar.append(ruta_pdf_cotizacion_hotel)
                            docs_unir.append(ruta_pdf_cotizacion_hotel)
                    else:
                        aux = False
                        return {"estado": False, "mensaje": "No se ha podido añadir imagen a docx"}  
                else:
                    aux = False
                    return {"estado": False, "mensaje": "No se ha podido reemplazar texto en plantilla hotel"}
            if aux:
                ruta_hoteles_unidos = os.path.abspath(f"plantilla/cotizaciones/temp/hoteles_{idUnico}.pdf")
                log_unir_hoteles = Pdf.unir_pdfs(docs_unir, ruta_hoteles_unidos)
                if log_unir_hoteles:
                    log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                    if log_eliminar_data:
                        return {"estado": True, "mensaje": "Documento creado exitosamente", "ruta": ruta_hoteles_unidos}    
                else:
                    return {"estado": False, "mensaje": "No se logro unir los pdfs de hoteles"}    
            else:
                return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"}
        else:
            return {"estado": False, "mensaje": "No hay datos del hotel"}

        

    @staticmethod
    def calcular_dias_noches(check_in, check_out):
        # Convertir las fechas de string a objetos datetime
        formato = "%Y-%m-%d"  # Formato de la fecha (yyyy-mm-dd)
        fecha_in = datetime.strptime(check_in, formato)
        fecha_out = datetime.strptime(check_out, formato)
        
        # Incluir el día del check-out en el cálculo
        diferencia = (fecha_out - fecha_in).days + 1  # Sumar 1 para incluir el día de salida
        
        # Días y noches
        dias = diferencia
        noches = dias - 1  # Las noches son un día menos que los días de estancia
        
        # Devolver un diccionario con los resultados
        return {
            "dias": dias,
            "noches": noches
        }
    
        
class Actividad:
    @staticmethod
    def generarPdfActividades(dataActividades, idUnico):
        # return{"estado": True}
        if dataActividades:
            pdfs_unir = []
            docs_eliminar = []
            aux = True
            ruta_plantilla_actividad_original = os.path.abspath("plantilla/cotizaciones/plantilla_cotizar_actividades.docx")
            ruta_plantilla_actividad = os.path.abspath(f"plantilla/cotizaciones/temp/plantilla_cotizar_actividades_{idUnico}.docx")
            shutil.copy(ruta_plantilla_actividad_original, ruta_plantilla_actividad)
            docs_eliminar.append(ruta_plantilla_actividad)
            for indice, actividad in enumerate(dataActividades):
                for index, act in enumerate(actividad["tours"]):
                    if act['nombre'] != "Transfer":
                        act["ciudad"] = actividad["ciudad"]
                        ruta_docx_generado_actividad = os.path.abspath(f"plantilla/cotizaciones/temp/actividad_{indice}_{index}_{idUnico}.docx")
                        docs_eliminar.append(ruta_docx_generado_actividad)
                        estilos = {"fuente": "Helvetica", "numero":12}
                        log_reemplazar_cotitazion = Docx.reemplazar_texto_parrafos(ruta_plantilla_actividad, ruta_docx_generado_actividad, act, estilos)
                        if log_reemplazar_cotitazion:
                            ruta_imagen_descargada = os.path.abspath(f"plantilla/cotizaciones/temp/imagen_actividad_{indice}_{index}_{idUnico}.jpeg")
                            ruta_imagen = (f"https://cotizador.mvevip.com/img/actividades_internas/{actividad['codigo']}/{act['id']}.jpg")
                            log_download = Imagen.download_image(ruta_imagen, ruta_imagen_descargada)
                            if not log_download:
                                ruta_imagen_descargada = os.path.abspath(f"img/mkv.jpg")
                            else:
                                docs_eliminar.append(ruta_imagen_descargada)
                            Docx.imagen_en_docx(ruta_imagen_descargada, ruta_docx_generado_actividad, "[imagen_actividad]", ancho_en_pt=400)
                            ruta_directorio_pdf = os.path.abspath("plantilla/cotizaciones/temp")
                            ruta_pdf_generado = Pdf.convertir_docx_a_pdf(ruta_docx_generado_actividad, ruta_directorio_pdf)
                            if ruta_pdf_generado:
                                pdfs_unir.append(ruta_pdf_generado)
                                docs_eliminar.append(ruta_pdf_generado)
                                aux = True
                            else:
                                aux = False 
                        else:
                            aux = False 
        if aux is True:
            ruta_pdf = os.path.abspath(f"plantilla/cotizaciones/temp/cotizar_actividades_{idUnico}.pdf")
            log_unir = Pdf.unir_pdfs(pdfs_unir, ruta_pdf)
            if log_unir:
                log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                if log_eliminar_data:
                    return {"estado": True, "mensaje": "Actividades creadas correctamente", "ruta": ruta_pdf}  
                else:
                    return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares"}
            else:
                return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"} 
        else:
            return {"estado": False, "mensaje": "Hubo un error con las actividades"} 
        

class Costos:
    @staticmethod
    def generarPdfCostos(dataCostos, incluye, idUnico):
        if dataCostos:
            docs_eliminar = []
            filas = []
            incluye_paquete = ", ".join(incluye) + "."
            datos = {
                "fecha": datetime.now().strftime("%d de %B de %Y a las %H:%M horas"),
                "incluye": incluye_paquete,
            }
            if dataCostos["tipo"] == "0":
                ruta_plantilla_costos_original = os.path.abspath("plantilla/cotizaciones/plantilla_cotizar_costos_detallado.docx")
                if dataCostos["detallado"]["adultos"]["numero"]>0:
                    data = {
                        "numA": dataCostos["detallado"]["adultos"]["numero"],
                        "precioAdulto_u": round(float(dataCostos["detallado"]["adultos"]["precio"]) / float(dataCostos["detallado"]["adultos"]["numero"]), 2) if float(dataCostos["detallado"]["adultos"]["numero"]) > 0 else 0,
                        "precioAdulto": round(float(dataCostos["detallado"]["adultos"]["precio"]), 2),
                    }
                    datos.update(data)
                else:
                    filas.append(1)
                if dataCostos["detallado"]["ninos"]["numero"]>0:
                    data = {
                        "numN": dataCostos["detallado"]["ninos"]["numero"],
                        "precioNino_u": round(float(dataCostos["detallado"]["ninos"]["precio"]) / float(dataCostos["detallado"]["ninos"]["numero"]), 2) if float(dataCostos["detallado"]["ninos"]["numero"]) > 0 else 0,
                        "precioNino": round(float(dataCostos["detallado"]["ninos"]["precio"]), 2),
                    }
                    datos.update(data)
                else:
                    filas.append(2)
                if dataCostos["detallado"]["infantes"]["numero"]>0:
                    data = {
                        "numI": dataCostos["detallado"]["infantes"]["numero"],
                        "precioInf_u": round(float(dataCostos["detallado"]["infantes"]["precio"]) / float(dataCostos["detallado"]["infantes"]["numero"]), 2) if float(dataCostos["detallado"]["infantes"]["numero"]) > 0 else 0,
                        "precioInf": round(float(dataCostos["detallado"]["infantes"]["precio"]), 2),
                    }
                    datos.update(data)
                else:
                    filas.append(3)
                if dataCostos["detallado"]["terceraEdad"]["numero"]>0:
                    data = {
                        "numT": dataCostos["detallado"]["terceraEdad"]["numero"],
                        "precioTer_u": round(float(dataCostos["detallado"]["terceraEdad"]["precio"]) / float(dataCostos["detallado"]["terceraEdad"]["numero"]), 2) if float(dataCostos["detallado"]["terceraEdad"]["numero"]) > 0 else 0,
                        "precioTer": round(float(dataCostos["detallado"]["terceraEdad"]["precio"]), 2),
                    }
                    datos.update(data)
                else:
                    filas.append(4)
                if dataCostos["detallado"]["discapacitados"]["numero"]>0:
                    data = {
                        "numD": dataCostos["detallado"]["discapacitados"]["numero"],
                        "precioDis_u": round(float(dataCostos["detallado"]["discapacitados"]["precio"]) / float(dataCostos["detallado"]["discapacitados"]["numero"]), 2) if float(dataCostos["detallado"]["discapacitados"]["numero"]) > 0 else 0,
                        "precioDis": round(float(dataCostos["detallado"]["discapacitados"]["precio"]), 2),
                    }
                    datos.update(data)
                else:
                    filas.append(5)
                data = {"total": round(dataCostos["detallado"]["total"] , 2)}
                datos.update(data)

            elif dataCostos["tipo"] == "1":
                ruta_plantilla_costos_original = os.path.abspath("plantilla/cotizaciones/plantilla_cotizar_costos_no_detallado.docx")
                data = {
                    "paquete": round(float(dataCostos["noDetallado"]["paquete"]),2),
                    "vuelo": round(float(dataCostos["noDetallado"]["vuelo"]),2),
                    "total": round(float(dataCostos["noDetallado"]["paquete"]) + float(dataCostos["noDetallado"]["vuelo"]), 2)
                }
                datos.update(data)
            else:
                return {"estado": False, "mensaje": "No se logro identificar el tipo de costos"}
            
            ruta_plantilla_costos = os.path.abspath(f"plantilla/cotizaciones/temp/plantilla_cotizar_costos_{idUnico}.docx")
            shutil.copy(ruta_plantilla_costos_original, ruta_plantilla_costos)
            ruta_docx_generado_costos = os.path.abspath(f"plantilla/cotizaciones/temp/costos_{idUnico}.docx")
            docs_eliminar.append(ruta_plantilla_costos)
            docs_eliminar.append(ruta_docx_generado_costos)
            estilos = {"fuente": "Helvetica", "numero":12}
            if len(filas) > 0:
                log_tabla_emiminar_fila = Docx.eliminar_filas_docx(ruta_plantilla_costos,ruta_plantilla_costos,filas)
                if not log_tabla_emiminar_fila:
                    return {"estado": False, "mensaje": "No se logro eliminar las filas de costos"} 
            log_reemplazar_cotitazion = Docx.reemplazar_texto_tabla_parrafo(ruta_plantilla_costos, ruta_docx_generado_costos, datos, estilos)
            if log_reemplazar_cotitazion:
                ruta_directorio_pdf = os.path.abspath("plantilla/cotizaciones/temp")
                ruta_pdf_generado = Pdf.convertir_docx_a_pdf(ruta_docx_generado_costos, ruta_directorio_pdf)
                if ruta_pdf_generado:
                    log_eliminar_data = Archivos.eliminar_documentos(docs_eliminar)
                    if log_eliminar_data:
                        return{"estado": True, "mensaje": "Costos creados correctamente", "ruta": ruta_pdf_generado}
                else:
                    return {"estado": False, "mensaje": "No se ha podido convertir docx a pdf"} 
            else:
                return {"estado": False, "mensaje": "No se ha podido reemplazar docx"} 
        else:
            return {"estado": False, "mensaje": "No hay datos de costos"} 

                