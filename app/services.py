import os
from docx import Document # type: ignore
from docx.shared import Pt # type: ignore
from docx.shared import Cm # type: ignore
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT # type: ignore
import subprocess
import sys
import base64
from PIL import Image # type: ignore
import re, mimetypes
import logging
from PyPDF2 import PdfMerger # type: ignore
from io import BytesIO

logging.basicConfig(
    filename = os.path.abspath("logs/output.log"), 
    level=logging.DEBUG,  # Define el nivel de los logs (INFO, DEBUG, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Switch:
    @staticmethod
    def verificar_tipo_doc(data):
        logging.info("Realizando servicio de creacion de pdf")
        if data["tipo"] == "contrato":
            return Contrato.generar_contrato(data)
        elif data["tipo"] == "adendum":
            return Adendum.generar_adendum(data)
        else:
            return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}

    @staticmethod
    def verificar_tipo_doc_descarga(id):
        logging.info("Realizacion de servicio de descarga de plantilla")
        # 0 = contratos, 1 = adendum, 2 = declaraciones
        if id == 0:
            ruta = os.path.abspath("plantilla/plantilla_contratos.docx")
        elif id == 1:
            ruta = os.path.abspath("plantilla/plantilla_adendum.docx")
        elif id == 2:
            ruta = os.path.abspath("plantilla/plantilla_declaraciones.docx")
        else:
            return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}
        return Descarga.descargar_documento(ruta)

    @staticmethod
    def verificar_tipo_doc_plantilla(data,id):
        logging.info("Realizacion de servicio de actualizacion de plantilla")
        if data["archivo"]:
            # 0 = contratos, 1 = adendum, 2 = declaraciones
            if id == 0:
                ruta = os.path.abspath("plantilla/plantilla_contratos.docx")
            elif id == 1:
                ruta = os.path.abspath("plantilla/plantilla_adendum.docx")
            elif id == 2:
                ruta = os.path.abspath("plantilla/plantilla_declaraciones.docx")
            else:
                return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}
            log_guardar = Guardar.guardar_archivo(ruta,data["archivo"])
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
            ruta_plantilla_adendum = os.path.abspath("plantilla/plantilla_adendum.docx")
            ruta_plantilla_declaraciones = os.path.abspath("plantilla/plantilla_declaraciones.docx")
            ruta_docx_generado_adendum = os.path.abspath("plantilla/adendum.docx")
            ruta_docx_generado_declaraciones = os.path.abspath("plantilla/declaraciones.docx")
            log_reemplazar_adendum = GenerarPdf.reemplazar_texto_docx(ruta_plantilla_adendum, ruta_docx_generado_adendum, data)
            log_reemplazar_declaraciones = GenerarPdf.reemplazar_texto_docx(ruta_plantilla_declaraciones, ruta_docx_generado_declaraciones, data)
            if log_reemplazar_adendum and log_reemplazar_declaraciones:
                ruta_directorio_pdf = os.path.abspath("plantilla")
                ruta_pdf_adendum = GenerarPdf.convertir_docx_a_pdf(ruta_docx_generado_adendum, ruta_directorio_pdf)
                ruta_pdf_declaraciones = GenerarPdf.convertir_docx_a_pdf(ruta_docx_generado_declaraciones, ruta_directorio_pdf)
                if ruta_pdf_adendum and ruta_pdf_declaraciones:
                    log_imagenes = GenerarPdf.procesar_imagenes(data["recibos_pago"])
                    if log_imagenes["estado"] == True:
                        pdfs_unir = [ruta_pdf_adendum, ruta_pdf_declaraciones, log_imagenes["ruta"]]
                        ruta_pdf = os.path.abspath("plantilla/adendum_completo.pdf")
                        log_unir_pdf = GenerarPdf.unir_pdfs(pdfs_unir, ruta_pdf)
                        if log_unir_pdf:
                            docs_eliminar = [ruta_docx_generado_adendum, ruta_docx_generado_declaraciones, ruta_pdf_adendum, ruta_pdf_declaraciones, log_imagenes["ruta"]]
                            log_eliminar_data = GenerarPdf.eliminar_documentos(docs_eliminar)
                            if log_eliminar_data:
                                pdf_base64 = GenerarPdf.archivo_a_base64(ruta_pdf)
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
            ruta_plantilla_contratos = os.path.abspath("plantilla/plantilla_contratos.docx")
            ruta_plantilla_declaraciones = os.path.abspath("plantilla/plantilla_declaraciones.docx")
            ruta_docx_generado_contratos = os.path.abspath("plantilla/contratos.docx")
            ruta_docx_generado_declaraciones = os.path.abspath("plantilla/declaraciones.docx")
            log_reemplazar_contratos = GenerarPdf.reemplazar_texto_docx(ruta_plantilla_contratos, ruta_docx_generado_contratos, data)
            log_reemplazar_declaraciones = GenerarPdf.reemplazar_texto_docx(ruta_plantilla_declaraciones, ruta_docx_generado_declaraciones, data)
            if log_reemplazar_contratos and log_reemplazar_declaraciones:
                ruta_docx_generado_contratos_estilos = os.path.abspath("plantilla/contratos_estilo.docx")
                log_estilos = GenerarPdf.aplicar_estilos_especificos(ruta_docx_generado_contratos, ruta_docx_generado_contratos_estilos)
                if log_estilos:
                    ruta_directorio_pdf = os.path.abspath("plantilla")
                    ruta_pdf_contratos = GenerarPdf.convertir_docx_a_pdf(ruta_docx_generado_contratos_estilos, ruta_directorio_pdf)
                    ruta_pdf_declaraciones = GenerarPdf.convertir_docx_a_pdf(ruta_docx_generado_declaraciones, ruta_directorio_pdf)
                    if ruta_pdf_contratos and ruta_pdf_declaraciones:
                        log_imagenes = GenerarPdf.procesar_imagenes(data["recibos_pago"])
                        if log_imagenes["estado"] == True:
                            pdfs_unir = [ruta_pdf_contratos, ruta_pdf_declaraciones, log_imagenes["ruta"]]
                            ruta_pdf = os.path.abspath("plantilla/contrato_completo.pdf")
                            log_unir_pdf = GenerarPdf.unir_pdfs(pdfs_unir, ruta_pdf)
                            if log_unir_pdf:
                                docs_eliminar = [ruta_docx_generado_contratos, ruta_docx_generado_declaraciones, ruta_pdf_contratos, ruta_pdf_declaraciones, log_imagenes["ruta"], ruta_docx_generado_contratos_estilos]
                                log_eliminar_data = GenerarPdf.eliminar_documentos(docs_eliminar)
                                if log_eliminar_data:
                                    pdf_base64 = GenerarPdf.archivo_a_base64(ruta_pdf)
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

class GenerarPdf:
    @staticmethod
    def procesar_imagenes(imagenesBase64):
        if imagenesBase64:
            rutas_imagenes_pdf = []
            rutas_a_eliminar = []
            for indice, recibo in enumerate(imagenesBase64):
                ruta_imagen_aux = os.path.abspath("plantilla/recibo"+str(indice))
                ruta_imagen = GenerarPdf.guardar_imagen_base64(recibo, ruta_imagen_aux)
                rutas_a_eliminar.append(ruta_imagen)
                if ruta_imagen:
                    ruta_plantilla_imagen = os.path.abspath("plantilla/plantilla_imagenes.docx")
                    ruta_docx_imagen = os.path.abspath("plantilla/recibo"+str(indice)+".docx")
                    rutas_a_eliminar.append(ruta_docx_imagen)
                    log_imagen_docs = GenerarPdf.agregar_imagen_docx(ruta_imagen, ruta_plantilla_imagen,ruta_docx_imagen)
                    if log_imagen_docs:
                        ruta_directorio_pdf_imagen = os.path.abspath("plantilla")
                        ruta_imagen_pdf = GenerarPdf.convertir_docx_a_pdf(ruta_docx_imagen,ruta_directorio_pdf_imagen)
                        rutas_a_eliminar.append(ruta_imagen_pdf)
                        if ruta_imagen_pdf:
                            rutas_imagenes_pdf.append(ruta_imagen_pdf)
                        else:
                            return {"estado": False, "mensaje": "Hubo un error al tranformar imagenes a pdf"}  
                    else:
                        return {"estado": False, "mensaje": "Hubo un error al insertar las imagenes en el documento"}
                else:
                    return {"estado": False, "mensaje": "Hubo un error con las imagenes adjuntadas"}
            ruta_imagenes_unidas_pdf = os.path.abspath("plantilla/imagenes.pdf")
            print(rutas_imagenes_pdf)
            log_unir_imagenes = GenerarPdf.unir_pdfs(rutas_imagenes_pdf, ruta_imagenes_unidas_pdf)
            if log_unir_imagenes:
                GenerarPdf.eliminar_documentos(rutas_a_eliminar)
                return {"estado": True, "mensaje": "Se proceso bien las imagenes", "ruta":ruta_imagenes_unidas_pdf}
            else:
                return {"estado": False, "mensaje": "Hubo un error al unir las imagenes"}
        else:
            return {"estado": False, "mensaje": "No hay recibos de pago"}

    @staticmethod
    def archivo_a_base64(ruta_archivo):
        try:
            with open(ruta_archivo, "rb") as archivo:
                contenido = archivo.read()
                contenido_base64 = base64.b64encode(contenido).decode('utf-8')
                return contenido_base64
        except FileNotFoundError:
            logging.error(f"El archivo {ruta_archivo} no se encuentra.")
            print(f"El archivo {ruta_archivo} no se encuentra.")
            return False
        except Exception as e:
            logging.error(f"Error al convertir el PDF a base64: {e}")
            print(f"Error al convertir el PDF a base64: {e}")
            return False

    @staticmethod
    def unir_pdfs(rutas, ruta_resultado):
        try:
            merger = PdfMerger()
            for ruta in rutas:
                merger.append(ruta)
            merger.write(ruta_resultado)
            merger.close()
            return True
        except Exception as e:
            logging.error(f"Error al combinar los PDFs: {e}")
            print(f"Error al combinar los PDFs: {e}")
            return False

    @staticmethod
    def eliminar_documentos(rutas_documentos):
        for ruta in rutas_documentos:
            try:
                # Verificar si el archivo existe
                if os.path.exists(ruta):
                    os.remove(ruta)  # Eliminar el archivo
                else:
                    logging.error(f"El archivo {ruta} no existe.")
                    print(f"El archivo {ruta} no existe.")
            except Exception as e:
                logging.error(f"Error al intentar eliminar el archivo {ruta}: {e}")
                print(f"Error al intentar eliminar el archivo {ruta}: {e}")
                return False
        return True

    @staticmethod
    def reemplazar_texto_docx(archivo_entrada, archivo_salida, variables):
        try:
            doc = Document(archivo_entrada)
            for para in doc.paragraphs:
                for var, valor in variables.items():
                    if isinstance(valor, list):  # Si el valor es una lista (como paquete_incluye)
                        valor = "\n".join(valor)  # Une los elementos de la lista con saltos de línea
                    marcador = f"[{var}]"
                    if marcador in para.text:
                        para.text = para.text.replace(marcador, str(valor))
                        for run in para.runs:
                            run.font.name = 'Helvetica'
                            run.font.size = Pt(10)

            #Recorrer las tablas del documento
            for tabla in doc.tables:
                for fila in tabla.rows:
                    for celda in fila.cells:
                        for para in celda.paragraphs:
                            for var, valor in variables.items():
                                if isinstance(valor, list):  # Si el valor es una lista
                                    valor = "\n".join(valor)  # Une los elementos de la lista con saltos de línea
                                
                                marcador = f"[{var}]"
                                if marcador in para.text:
                                    para.text = para.text.replace(marcador, str(valor))
                                    for run in para.runs:
                                        run.font.name = 'Helvetica'
                                        run.font.size = Pt(10)
            doc.save(archivo_salida)
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")  # Imprime el error si ocurre
            return False  # En caso de error, devolver False
        
    @staticmethod
    def aplicar_estilos_especificos(archivo_entrada, archivo_salida):
        textos_objetivo = {
            'COMPAÑÍA TURISTICA "MARKETING VIP S.A" COMTUMARK',
            'EL CLIENTE',
            'SEGUNDA',
            'TERCERA'
            'LA OPERADORA TURISTICA',
            'Lugar y fecha'
        }
        try:
            doc = Document(archivo_entrada)
            for para in doc.paragraphs:
                nuevo_runs = []
                for run in para.runs:
                    texto = run.text
                    i = 0
                    while i < len(texto):
                        texto_encontrado = False
                        for palabra in textos_objetivo:
                            if texto[i:i+len(palabra)] == palabra:
                                # Crear un nuevo run con negrita para el texto objetivo
                                nuevo_run = para.add_run(palabra)
                                nuevo_run.bold = True
                                nuevo_run.font.name = 'Helvetica'
                                nuevo_run.font.size = Pt(10)
                                nuevo_runs.append(nuevo_run)
                                i += len(palabra)
                                texto_encontrado = True
                                break
                        if not texto_encontrado:
                            # Crear un run normal para el texto que no coincide
                            nuevo_run = para.add_run(texto[i])
                            nuevo_run.font.name = run.font.name or 'Helvetica'
                            nuevo_run.font.size = run.font.size or Pt(10)
                            nuevo_run.bold = run.bold
                            nuevo_runs.append(nuevo_run)
                            i += 1
                    run._element.getparent().remove(run._element)
            doc.save(archivo_salida)
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")  # Imprime el error si ocurre
            return False  # En caso de error, devolver False

    @staticmethod
    def convertir_docx_a_pdf(archivo_entrada, archivo_salida):
        try:
            if not os.path.exists(archivo_entrada):
                raise FileNotFoundError(f"El archivo {archivo_entrada} no se encuentra.")
            if sys.platform == "win32":  # Windows
                libreoffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
            elif sys.platform == "linux" or sys.platform == "linux2":  # Linux
                libreoffice_path = "/usr/bin/libreoffice"  # Asegúrate de que esté en esa ubicación
            else:
                raise EnvironmentError("Sistema operativo no soportado")
            subprocess.run([libreoffice_path, '--headless', '--convert-to', 'pdf', archivo_entrada, '--outdir', archivo_salida])
            nombre_pdf = os.path.splitext(os.path.basename(archivo_entrada))[0] + ".pdf"
            ruta_pdf_salida = os.path.join(archivo_salida, nombre_pdf)
            if not os.path.exists(ruta_pdf_salida):
                logging.error(f"No se pudo crear el archivo PDF en {ruta_pdf_salida}.")
                return False
            return ruta_pdf_salida
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")  # Imprime el error si ocurre
            return False  # En caso de error, devolver False

    @staticmethod
    def guardar_imagen_base64(imagen_base64, ruta_salida):
        try:
            match = re.match(r"data:image/(\w+);base64,(.*)", imagen_base64)
            if not match:
                return False
            formato_imagen = match.group(1)
            imagen_base64_data = match.group(2)
            imagen_bytes = base64.b64decode(imagen_base64_data)
            ruta_imagen = f"{ruta_salida}.{formato_imagen}"
            with open(f"{ruta_salida}.{formato_imagen}", "wb") as f:
                f.write(imagen_bytes)
            return ruta_imagen
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error al guardar la imagen: {e}")
            return False  

    @staticmethod
    def agregar_imagen_docx(ruta_imagen, ruta_plantilla, ruta_salida):
        try:
            # Cargar la plantilla del documento
            doc = Document(ruta_plantilla)
            
            # Abrir la imagen y obtener sus dimensiones
            with Image.open(ruta_imagen) as img:
                width, height = img.size
                
                # Ajustar dimensiones de la imagen
                if height > width:  # Si la imagen es más alta que ancha
                    alto = Cm(19)
                    ancho = (width / height) * alto
                else:  # Si la imagen es más ancha que alta
                    ancho = Cm(13)
                    alto = (height / width) * ancho
                
                # Insertar la imagen al principio del documento
                paragraph = doc.add_paragraph()  # Crear un nuevo párrafo al inicio
                run = paragraph.add_run()  # Crear un "run" en el párrafo
                run.add_picture(ruta_imagen, width=ancho, height=alto)  # Insertar la imagen con tamaño ajustado
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Centrar el párrafo
            
            # Guardar el documento con la imagen añadida al principio
            doc.save(ruta_salida)
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")  # Imprime el error si ocurre
            return False  # En caso de error, devolver False
        
class Descarga:
    @staticmethod
    def descargar_documento(ruta):
        base64 = GenerarPdf.archivo_a_base64(ruta)
        if base64:
            return {"estado": True, "mensaje": "Archivo obtenido con exito", "archivo": base64}   
        else:
            return {"estado": False, "mensaje": "No se ha podido codificar el archivo"}   
        
class Guardar:
    @staticmethod
    def guardar_archivo(ruta_guardar, base64_string):
        try:
            contenido_binario = base64.b64decode(base64_string)
            archivo_docx = BytesIO(contenido_binario)
            doc = Document(archivo_docx)
            directorio = os.path.dirname(ruta_guardar)
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            doc.save(ruta_guardar)
            return True
        except Exception as e:
            logging.error(f"Error al guardar el archivo: {e}")
            print(f"Error al guardar el archivo: {e}")
            return False     