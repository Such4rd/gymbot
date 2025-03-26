from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram import Update
 
from utils.constants import *


async def button_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not "button_counter" in context.user_data:
        context.user_data["button_counter"] = 0
    counter = context.user_data["button_counter"]
 
    keyboard = [
        [
            InlineKeyboardButton(text='◀️', callback_data='change_counter:-1'),
            InlineKeyboardButton(text=str(counter), callback_data='None'),
            InlineKeyboardButton(text='▶️', callback_data='change_counter:+1'),
        ],
        [
            InlineKeyboardButton(text='🔄 Reset', callback_data='reset_counter'),
        ]
    ]
 
    text = "This is a simple keyboard counter."
    reply_markup = InlineKeyboardMarkup(keyboard)
 
    if not update.callback_query:
        await update.effective_message.reply_text(text=text, reply_markup=reply_markup)
    else:
        await update.effective_message.edit_text(text=text, reply_markup=reply_markup)
 
 
async def change_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("estamos en la funcion del contador")
    
    # Obtener la acción del callback (repeticiones o peso)
    query = update.callback_query
    await query.answer() 
    counter_type, action = update.callback_query.data.split(':')
    peso = context.user_data["counter_peso"]
    repes = context.user_data["counter_repes"] 
    intervalo = context.user_data["intervalo"]
    grupo = context.user_data["grupo"]
    ejercicio = context.user_data["ejercicio"] 
    # Cambiar el contador correspondiente
    if counter_type == "counter_repes":
        counter = "counter_repes"
    elif counter_type == "counter_peso":
        counter = "counter_peso"
    elif counter_type == "intervalo":
        counter = "intervalo"
    elif counter_type == "save_serie":
        counter="save"
        await query.edit_message_text(
            text=f"¿Confirmas guardar esta serie? \n {grupo} - {ejercicio}: {repes} - {peso}",
            reply_markup=InlineKeyboardMarkup(keyboard_confirm)
        )
        return CONFIRM
    else:
        return  # No hacer nada si el callback no es válido

    increment = context.user_data["intervalo"]

    if counter != "intervalo":
        increment = increment if action == "+1" else -increment
        # Actualizar el contador correspondiente
        context.user_data[counter] += increment
        context.user_data[counter] = 0 if context.user_data[counter] < 0 else context.user_data[counter]#controlamos negativo

    else:
        if increment == 5:
            context.user_data[counter] = 0.5
        else:
            context.user_data[counter] += 0.5


    peso = context.user_data["counter_peso"]
    repes = context.user_data["counter_repes"] 
    intervalo = context.user_data["intervalo"]
    grupo = context.user_data["grupo"]
    ejercicio = context.user_data["ejercicio"] 
    mejor_marca = context.user_data["BEST_BRAND"] 
    keyboard = keyboard_series(repes,peso,intervalo,grupo,ejercicio,mejor_marca) 
    await query.edit_message_text(
        text = "Indica las repeticiones y el peso:", 
        reply_markup=keyboard
    )

    return SET

async def reset_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Resetear ambos contadores
    context.user_data["counter_repes"] = 0
    context.user_data["counter_peso"] = 0
 
    return SET
