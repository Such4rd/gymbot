import os

# Obtener la API key desde la variable de entorno
TOKEN = os.getenv('TELEGRAM_API_KEY')

# Verifica que se haya cargado la API key
if TOKEN is None:
    raise ValueError("La variable de entorno 'TELEGRAM_API_KEY' no está configurada.")
import re