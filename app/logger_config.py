import logging
import os
import sys

# Configurar logging
log_file = os.path.abspath("logs/output.log")
logging.basicConfig(
    filename=log_file, 
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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