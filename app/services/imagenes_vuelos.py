import os
from PIL import Image # type: ignore
from app.services.comun import Imagen 
import app.logger_config 


class Img:
    @staticmethod
    def cotizar_vuelos(data):
        if data:
            ruta_plantilla = os.path.abspath("plantilla/imagenes_vuelos/plantilla.jpg")
            ruta_imagen_generada = os.path.abspath("plantilla/imagenes_vuelos/temp/vuelos.jpg")
            imagen_original = Image.open(ruta_plantilla)
            imagen_copia = imagen_original.copy()
            imagen_copia.save(ruta_imagen_generada)
            Imagen.colocar_texto_a_imagen(data["ida_fecha"],(170,110),ruta_imagen_generada,ruta_imagen_generada,15)
            imagen_pequena = Img.sacar_logo_aereolina(data["aereolina_codigo"])
            Imagen.colocar_imagen_pequena(imagen_pequena, (33,20), ruta_imagen_generada, ruta_imagen_generada,90,40)
            Imagen.colocar_texto_a_imagen(data["aereolina_nombre"],(120,30),ruta_imagen_generada,ruta_imagen_generada,15)
            Imagen.colocar_texto_a_imagen(data["vuelta_fecha"],(170,320),ruta_imagen_generada,ruta_imagen_generada,15)
            texto_ida = data["codigo_salida"] + "-" + data["codigo_destino"]
            Imagen.colocar_texto_a_imagen(texto_ida,(700,20),ruta_imagen_generada,ruta_imagen_generada,15)
            texto_vuelta = data["codigo_destino"] + "-" + data["codigo_salida"]
            Imagen.colocar_texto_a_imagen(texto_vuelta,(700,35),ruta_imagen_generada,ruta_imagen_generada,15)
            altura = 149
            for index, vuelo in enumerate(data["vuelos_ida"]):
                if index<3:
                    idVuelo = "I"+str(index+1)
                    Imagen.colocar_texto_a_imagen(idVuelo,(96,altura),ruta_imagen_generada,ruta_imagen_generada,13)
                    texto_horas = data["codigo_salida"]+": "+vuelo["hora_salida"]+" ---> "+data["codigo_destino"]+": "+vuelo["hora_llegada"]
                    Imagen.colocar_texto_a_imagen(texto_horas,(144,altura),ruta_imagen_generada,ruta_imagen_generada,15)
                    Imagen.colocar_texto_a_imagen(vuelo["duracion"],(400,altura),ruta_imagen_generada,ruta_imagen_generada,15)
                    escalas = str(vuelo["numero_escalas"])+ " Escala(s)"
                    Imagen.colocar_texto_a_imagen(escalas,(500,altura),ruta_imagen_generada,ruta_imagen_generada,15)
                    ruta_personal = Img.sacar_equipaje("personal",int(vuelo["equipaje_personal"]))
                    ruta_carry = Img.sacar_equipaje("carry",int(vuelo["equipaje_carry"]))
                    ruta_bodega = Img.sacar_equipaje("bodega",int(vuelo["equipaje_bodega"]))
                    Imagen.colocar_imagen_pequena(ruta_personal, (700,altura-3), ruta_imagen_generada, ruta_imagen_generada,18,18)
                    Imagen.colocar_imagen_pequena(ruta_carry, (720,altura-4), ruta_imagen_generada, ruta_imagen_generada,20,20)
                    Imagen.colocar_imagen_pequena(ruta_bodega, (740,altura-4), ruta_imagen_generada, ruta_imagen_generada,20,20)
                    altura = altura +52
            altura = 358
            for index, vuelo in enumerate(data["vuelos_vuelta"]):
                if index<3:
                    idVuelo = "v"+str(index+1)
                    Imagen.colocar_texto_a_imagen(idVuelo,(96,altura),ruta_imagen_generada,ruta_imagen_generada,13)
                    texto_horas = data["codigo_salida"]+": "+vuelo["hora_salida"]+" ---> "+data["codigo_destino"]+": "+vuelo["hora_llegada"]
                    Imagen.colocar_texto_a_imagen(texto_horas,(144,altura),ruta_imagen_generada,ruta_imagen_generada,15)
                    Imagen.colocar_texto_a_imagen(vuelo["duracion"],(400,altura),ruta_imagen_generada,ruta_imagen_generada,15)
                    escalas = str(vuelo["numero_escalas"])+ " Escala(s)"
                    Imagen.colocar_texto_a_imagen(escalas,(500,altura),ruta_imagen_generada,ruta_imagen_generada,15)
                    ruta_personal = Img.sacar_equipaje("personal",int(vuelo["equipaje_personal"]))
                    ruta_carry = Img.sacar_equipaje("carry",int(vuelo["equipaje_carry"]))
                    ruta_bodega = Img.sacar_equipaje("bodega",int(vuelo["equipaje_bodega"]))
                    Imagen.colocar_imagen_pequena(ruta_personal, (700,altura-3), ruta_imagen_generada, ruta_imagen_generada,18,18)
                    Imagen.colocar_imagen_pequena(ruta_carry, (720,altura-4), ruta_imagen_generada, ruta_imagen_generada,20,20)
                    Imagen.colocar_imagen_pequena(ruta_bodega, (740,altura-4), ruta_imagen_generada, ruta_imagen_generada,20,20)
                    altura = altura +52
            imagen_base64 = Imagen.convertir_imagen_a_base64(ruta_imagen_generada)
            if imagen_base64:
                return {"estado": True, "mensaje": "Imagen generada correctamente", "imagen": imagen_base64}  
            else:
                return {"estado": False, "mensaje": "No se ha podido generar Imagen"}  
        else:
            return {"estado": False, "mensaje": "No hay datos en el body"}  
        

    @staticmethod
    def sacar_logo_aereolina(aereolina):
        if aereolina == "AV" or aereolina == '2K':
            return os.path.abspath("img/aereolinas_logos/avianca.png")
        elif aereolina == 'CM':
            return os.path.abspath("img/aereolinas_logos/copa.png")
        elif aereolina == 'DL':
            return os.path.abspath("img/aereolinas_logos/delta.png")        
        elif aereolina == 'B6':
            return os.path.abspath("img/aereolinas_logos/jet.png")
        elif aereolina == 'LA':
            return os.path.abspath("img/aereolinas_logos/latam.png")
        elif aereolina == 'AA':
            return os.path.abspath("img/aereolinas_logos/american.png")
        

    @staticmethod
    def sacar_equipaje(tipo,id):
        if tipo == "personal":
            if id >= 1:
                return os.path.abspath("img/equipaje/si_personal.png")
            else:
                return os.path.abspath("img/equipaje/no_personal.png")
        elif tipo == 'carry':
            if id >= 1:
                return os.path.abspath("img/equipaje/si_carry.png")
            else:
                return os.path.abspath("img/equipaje/no_carry.png")
        elif tipo == 'bodega':
            if id >= 1:
                return os.path.abspath("img/equipaje/si_bodega.png")
            else:
                return os.path.abspath("img/equipaje/no_bodega.png")