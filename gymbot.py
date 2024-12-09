import utils.db_utils as db
import utils.reset as rst
import os
from datetime import datetime
import logging
from telegram import  ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    JobQueue
)
from dotenv import load_dotenv
from handlers import conv_handler


#cargar variables de entorno
load_dotenv()

TOKEN = os.getenv('TOKEN')


# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


logger.info("GymBot iniciado")
logger.info(f"Token cargado: {'Sí' if TOKEN else 'No'}")

def main() -> None:
    """Inicia el bot."""
    
    logger.info("Iniciando la aplicación Telegram...")
    
    application = Application.builder().token(TOKEN).build()   
    
    logger.info("Bot en ejecución...")
    #Añadir manejador de conversación
            
    application.add_handler(conv_handler)
    # Ejecutar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
