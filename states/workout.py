from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes,
    ConversationHandler
)
from utils.constants import *
from utils import db_utils as db
from utils import helpers as hp
import logging
from utils import reset as rt

logger = logging.getLogger(__name__)

async def workout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    query = update.callback_query
   
    await query.answer()
    await rt.reset_timer(update, context)
    
    logger.info(f"Vamos a mostrar los entrenos del día que seleccione")
    
    datos_entreno = query.data  # ID del entreno seleccionado

    # Verifica si ya hay un entrenamiento en curso en `training_log`
    if 'training_log' in context.user_data:
        # Guarda el entrenamiento actual en una variable temporal
        context.user_data['previous_training_log'] = context.user_data['training_log']
        logger.info(f"Guardamos el entreno actual para recogerlo más tarde")
    else:
        # Si no hay un entrenamiento actual, asegúrate de limpiar `previous_training_log`
        context.user_data['previous_training_log'] = None
       
    # Carga y muestra el entrenamiento pasado
    context.user_data['training_log'] = db.load_entreno(datos_entreno)
    # Devuelve al usuario a su entrenamiento anterior después de mostrar el seleccionado
    if context.user_data['previous_training_log'] is not None:
        inline_opciones = [
            [
                InlineKeyboardButton('Volver al entreno',callback_data='BACK')
            ]
        ]
        await query.edit_message_text(
            hp.mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup(inline_opciones)
        )
         # Restaurar el entrenamiento anterior en `training_log`
        context.user_data['training_log'] = context.user_data['previous_training_log']
        del context.user_data['previous_training_log']


        return OPTIONS
      
    else:
        # Si no había entrenamiento anterior, limpia `training_log`
        await query.edit_message_text(
           f"{hp.mostrar_resumen(update, context)}"
        )
        del context.user_data['training_log']
        return ConversationHandler.END