import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Configuración de la ruta del archivo de log
log_file = os.path.abspath("logs/output.log")

# Crear un manejador que rote los logs después de alcanzar un tamaño límite (por ejemplo, 5MB)
log_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)  # 5MB, mantener 3 archivos antiguos

# Configurar el formato del log
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Establece el nivel de logging
logger.addHandler(log_handler)

# Redirigir stdout y stderr a logging
class LoggerWriter:
    def __init__(self, level):
        self.level = level  # logging.INFO o logging.ERROR
    def write(self, message):
        if message.strip():  # Evita líneas vacías
            self.level(message.strip())
    def flush(self):
        pass  # No se necesita para logging

sys.stdout = LoggerWriter(logging.info)  # Captura print normales
sys.stderr = LoggerWriter(logging.error)  # Captura errores
