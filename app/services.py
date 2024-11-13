import os
from docx import Document # type: ignore
from docx.shared import Pt # type: ignore
from docx.shared import Inches # type: ignore
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT # type: ignore
import subprocess
import sys
import base64
from PIL import Image # type: ignore
import re
import logging

logging.basicConfig(
    filename = os.path.abspath("logs/output.log"), 
    level=logging.DEBUG,  # Define el nivel de los logs (INFO, DEBUG, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Switch:
    @staticmethod
    def verificar_tipo_doc(data):
        logging.info("Este es un mensaje informativo.")
        if data["tipo"] == "contrato":
            return Contrato.generar_contrato(data)
        elif data["tipo"] == "adendum":
            return Adendum.generar_adendum(data)
        else:
            return {"estado": False, "mensaje": "No se reconoce el tipo de archivo"}

class Adendum:
    @staticmethod
    def generar_adendum(data):
        if data:
            ruta_plantilla = os.path.abspath("plantilla/plantilla_adendum.docx")
            ruta_docx_generado = os.path.abspath("plantilla/adendum.docx")
            log_reemplazar = GenerarPdf.reemplazar_texto_docx(ruta_plantilla, ruta_docx_generado, data)
            if log_reemplazar:
                ruta_pdf_generado = os.path.abspath("plantilla")
                log_pdf = GenerarPdf.convertir_docx_a_pdf(ruta_docx_generado, ruta_pdf_generado)
                if log_pdf:
                    docs_eliminar = [ruta_docx_generado]
                    log_eliminar_data = GenerarPdf.eliminar_documentos(docs_eliminar)
                    if log_eliminar_data:
                        ruta_pdf = os.path.abspath("plantilla/adendum.pdf")
                        log_base64 = GenerarPdf.pdf_a_base64(ruta_pdf)
                        if log_base64:
                            return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": log_base64}    
                        else:
                            return {"estado": False, "mensaje": "No se logro crear base64"}    
                    else:
                        return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares"}    
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
            #Guardamos imagen
            ruta_imagen = os.path.abspath("plantilla/recibo")
            ruta_imagen_guardada = GenerarPdf.guardar_imagen_base64(data["recibo_pago"], ruta_imagen)
            if ruta_imagen_guardada is not None:
                data.pop("recibo_pago", None)
                ruta_plantilla = os.path.abspath("plantilla/plantilla_contratos.docx")
                ruta_docx_generado = os.path.abspath("plantilla/contrato_generado.docx")
                log_reemplazar = GenerarPdf.reemplazar_texto_docx(ruta_plantilla, ruta_docx_generado, data)
                if log_reemplazar:
                    ruta_docx_estilos= os.path.abspath("plantilla/contrato_generado_con_estilos.docx")
                    log_estilos = GenerarPdf.aplicar_estilos_especificos(ruta_docx_generado,ruta_docx_estilos)
                    if log_estilos:
                        ruta_docx_imagen = os.path.abspath("plantilla/contrato.docx")
                        log_imagen = GenerarPdf.agregar_imagen_al_final_docx(ruta_imagen_guardada,ruta_docx_estilos,ruta_docx_imagen)
                        if log_imagen:
                            ruta_pdf_generado = os.path.abspath("plantilla")
                            log_pdf = GenerarPdf.convertir_docx_a_pdf(ruta_docx_imagen, ruta_pdf_generado)
                            if log_pdf:
                                docs_eliminar = [ruta_docx_generado,ruta_docx_estilos, ruta_docx_imagen]
                                log_eliminar_data = GenerarPdf.eliminar_documentos(docs_eliminar)
                                if log_eliminar_data:
                                    ruta_pdf = os.path.abspath("plantilla/contrato.pdf")
                                    log_base64 = GenerarPdf.pdf_a_base64(ruta_pdf)
                                    if log_base64:
                                        return {"estado": True, "mensaje": "Documento creado exitosamente", "pdf": log_base64}    
                                    else:
                                        return {"estado": False, "mensaje": "No se logro crear base64"}    
                                else:
                                    return {"estado": False, "mensaje": "No se logro eliminar los documentos auxiliares"}    
                            else:
                                return {"estado": False, "mensaje": "Documento PDF no se puede crear"}    
                        else:
                            return {"estado": False, "mensaje": "No se ha podido insertar la imagen al doc"}    
                    else:
                        return {"estado": False, "mensaje": "No se ha podido aplicar estilos al doc generado"}    
                else:
                    return {"estado": False, "mensaje": "No se ha podido reemplazar el texto de la plantilla"}    
            else:
                return {"estado": False, "mensaje": "No se guardo el recibo correctamente"}   
        else:
            return {"estado": False, "mensaje": "No hay campos"}

class GenerarPdf:
    @staticmethod
    def pdf_a_base64(ruta_pdf):
        try:
            with open(ruta_pdf, "rb") as archivo_pdf:
                contenido_pdf = archivo_pdf.read()
                contenido_base64 = base64.b64encode(contenido_pdf).decode('utf-8')
                return contenido_base64
        except FileNotFoundError:
            logging.error(f"El archivo {ruta_pdf} no se encuentra.")
            print(f"El archivo {ruta_pdf} no se encuentra.")
            return False
        except Exception as e:
            logging.error(f"Error al convertir el PDF a base64: {e}")
            print(f"Error al convertir el PDF a base64: {e}")
            return False



    @staticmethod
    def eliminar_documentos(rutas_documentos):
        for ruta in rutas_documentos:
            try:
                # Verificar si el archivo existe
                if os.path.exists(ruta):
                    os.remove(ruta)  # Eliminar el archivo
                    logging.error(f"El archivo {ruta} ha sido eliminado.")
                    print(f"El archivo {ruta} ha sido eliminado.")
                else:
                    logging.error(f"El archivo {ruta} ha sido eliminado.")
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
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")  # Imprime el error si ocurre
            return False  # En caso de error, devolver False


    @staticmethod
    def guardar_imagen_base64(imagen_base64, ruta_salida):
        match = re.match(r"data:image/(\w+);base64,(.*)", imagen_base64)
        if not match:
            return None
        formato_imagen = match.group(1)
        imagen_base64_data = match.group(2)
        imagen_bytes = base64.b64decode(imagen_base64_data)
        
        with open(f"{ruta_salida}.{formato_imagen}", "wb") as f:
            f.write(imagen_bytes)
        ruta_imagen = f"{ruta_salida}.{formato_imagen}"
        return ruta_imagen


    @staticmethod
    def agregar_imagen_al_final_docx(ruta_imagen_guardada, ruta_docx_estilos, ruta_docx_imagen):
        try:
            doc = Document(ruta_docx_estilos)
            with Image.open(ruta_imagen_guardada) as img:
                width, height = img.size
                if height > width:  # Si la imagen es más alta que ancha
                    alto = Inches(9)
                    ancho = (width / height) * alto
                else:  # Si la imagen es más ancha que alta
                    ancho = Inches(6)
                    alto = (height / width) * ancho
                paragraph = doc.add_paragraph()  # Crear un nuevo párrafo
                run = paragraph.add_run()  # Crear un "run" en el párrafo
                run.add_picture(ruta_imagen_guardada, width=ancho, height=alto)  # Ajustar el tamaño proporcional de la imagen
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            doc.save(ruta_docx_imagen)
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")  # Imprime el error si ocurre
            return False  # En caso de error, devolver False