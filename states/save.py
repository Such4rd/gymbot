from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes,
    ConversationHandler
)
from utils.constants import *
from utils import db_utils as db
from utils import helpers as hp
from datetime import datetime
from utils import reset as rt

async def save_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"
    #await rt.reset_timer(update, context)
    # Verificar qué botón fue presionado basado en el callback_data
    
    if query.data == "SAVE" and 'training_log' in context.user_data:
        
        #recoger usuario
        usuario = query.from_user.name
        usuario = usuario.replace('@','').upper() # Obtén el nombre completo del usuario de Telegram
        id_entreno = db.generar_id_entreno(usuario)  # Genera el ID del entrenamiento

        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')

        datos_entreno = context.user_data['training_log']
        db.insertar_entreno(datos_entreno,usuario,fecha_actual,id_entreno)
        # Insertar entrenamiento en la tabla de entrenamientos

        await query.edit_message_text(
            text = f"¡Maravilla! Entreno completado y registrado! \n Hasta la proxima {usuario}",
            reply_markup=None
        )
        context.user_data['training_log'] = []
        return ConversationHandler.END
    else:
        await query.edit_message_text(
            text = "[!] Entrenamiento vacio, empiece de nuevo (/start)",
            reply_markup=None
        )
        return ConversationHandler.END