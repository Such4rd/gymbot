from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes
)
from utils.constants import *
from utils import db_utils as db
from utils import helpers as hp
import logging
from utils import reset as rt

async def exercise_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger = logging.getLogger(__name__)
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"
    #await rt.reset_timer(update, context)
    # Verificar qué botón fue presionado basado en el callback_data
    logger.info("Estamos gestionando la selección del ejercicio")
    if query.data == "NEW_EJE":
        print("hacemos insert en base de datos")
        await query.edit_message_text(
            "Indique el nombre del ejercicio:",
            reply_markup=None
        )
        return EXERCISE
    elif query.data == 'END':
        await query.edit_message_text(
            hp.mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]])
        )
        return SAVE 
    
    if not "counter_repes" in context.user_data:
        context.user_data["counter_repes"] = 0

    if not "counter_peso" in context.user_data:
        context.user_data["counter_peso"] = 0
    if not "intervalo" in context.user_data:
        context.user_data["intervalo"] = 5

    context.user_data['ejercicio'] = query.data

    
    
    counter_repes = context.user_data["counter_repes"]
    counter_peso = context.user_data["counter_peso"]
    intervalo = context.user_data["intervalo"] 
    grupo = context.user_data["grupo"]
    ejercicio = context.user_data["ejercicio"] 

    
    # Llamada a la función para obtener la mejor marca
    mejor_marca_resultado = db.mejor_marca(grupo, ejercicio)

    # Verificamos si no es None antes de hacer el unpacking
    if mejor_marca_resultado:
        repes_max, peso_max = mejor_marca_resultado
        context.user_data["BEST_BRAND"] = f"{repes_max}-{peso_max} KG"
        mejor_marca = context.user_data["BEST_BRAND"]
    else:
        mejor_marca = ""

    keyboard = keyboard_series(counter_repes,counter_peso, intervalo,grupo,ejercicio,mejor_marca)




    reply_markup = keyboard

    
    await query.edit_message_text(
        text = "Complete la serie",
        reply_markup=reply_markup
    )
    
   
    
    return SET


async def new_exercise_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger = logging.getLogger(__name__)

    nuevo = update.message.text

    # Verificar si es valido el string
    if not isinstance(nuevo, str) or not nuevo.strip() or any(char.isdigit() for char in nuevo) or len(nuevo) < 3 or len(nuevo) > 30:
        await update.message.reply_text(
            text="*Formato incorrecto*\n Indique el nombre del ejercicio(3-30 caracteres, sin números)"
        )
        return EXERCISE
    nuevo = nuevo.capitalize()
    grupo = context.user_data['grupo']

    # Verificar si el ejercicio ya existe
    if db.ejercicio_existe(nuevo):
        await update.message.reply_text(
            text="*El ejercicio ya existe en la base de datos.* Indique un nombre diferente:"
        )
        return EXERCISE


    context.user_data['ejercicio'] = nuevo


    db.insertar_ejercicio(nuevo,grupo,update.message.from_user.id,update.message.date.date())
    # Insertar ejercicio en bs
    
    await update.message.reply_text(
        text = "Indica las repeticiones y el peso (formato: reps, peso(kg),coment):",
        reply_markup=None
    )

    return SET
