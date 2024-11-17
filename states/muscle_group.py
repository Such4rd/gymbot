from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes
)
from utils.constants import *
from utils import db_utils as db
from utils import helpers as hp
from utils import reset as rt
async def muscle_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"
    await rt.reset_timer(update, context)
    # Verificar qué botón fue presionado basado en el callback_data
    if query.data != "NEW_GRU" and query.data != 'END':    
        context.user_data['grupo'] = query.data
        exercises = db.obtener_ejercicios_por_grupo(query.data)
        inline_board_lista = hp.grouped_buttons([InlineKeyboardButton(ejercicio,callback_data=ejercicio) for ejercicio in exercises])
        inline_board_lista.append([InlineKeyboardButton("Nuevo ejercicio",callback_data="NEW_EJE")])
        inline_board_lista.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text(
            "Selecciona un ejercicio:",
            reply_markup=InlineKeyboardMarkup(inline_board_lista)
        )

        return EXERCISE
    elif query.data == 'END':
        await query.edit_message_text(
            hp.mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]])
       )
        return SAVE   