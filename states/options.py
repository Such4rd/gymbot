from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes
)
from utils.constants import *
from utils import db_utils as db
from utils import helpers as hp
from utils import reset as rt
async def options_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón."""

    query = update.callback_query
    await query.answer()
    print(query.data)
    #await rt.reset_timer(update, context)
    if query.data == "NEW_SER":
        mejor_marca_resultado = db.mejor_marca(context.user_data["grupo"], context.user_data["ejercicio"])

        # Verificamos si no es None antes de hacer el unpacking
        if mejor_marca_resultado:
            repes_max, peso_max = mejor_marca_resultado
            context.user_data["BEST_BRAND"] = f"{repes_max}-{peso_max} KG"
            mejor_marca = context.user_data["BEST_BRAND"]
        else:
            mejor_marca = ""

        await query.edit_message_text(
            text = "Completa la serie:",
            reply_markup=keyboard_series( context.user_data["counter_repes"], context.user_data["counter_peso"], context.user_data["intervalo"], context.user_data["grupo"], context.user_data["ejercicio"],mejor_marca)
        )
       
        return SET
    
    elif query.data == "NEW_EJE":
        # Volver al inicio del flujo para seleccionar un nuevo ejercicio
        muscles = db.obtener_grupos_musculares()
        inline_board = hp.grouped_buttons([InlineKeyboardButton(musculo,callback_data=musculo) for musculo in muscles])
        #inline_board.append([InlineKeyboardButton("Nuevo grupo muscular",callback_data="NEW_GRU")])
        inline_board.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text("Selecciona un grupo muscular:", reply_markup=InlineKeyboardMarkup(inline_board))
        
        return MUSCLE_GROUP
    elif query.data == "LOG" or query.data == "BACK":
        inline_opciones = [
            [
                InlineKeyboardButton('Hacer otra serie',callback_data='NEW_SER'),
                InlineKeyboardButton('Cambiar ejercicio',callback_data='NEW_EJE')
            ],
            [
                InlineKeyboardButton('Finalizar entreno',callback_data='END')
            ]
        ]
        await query.edit_message_text(
            hp.mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup(inline_opciones),
            parse_mode="Markdown"
        )
        return OPTIONS
    elif query.data == "END":
        await query.edit_message_text(
            hp.mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]]),
            parse_mode="Markdown"
        )
        return SAVE