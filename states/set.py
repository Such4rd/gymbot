from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes
)
from states.options import options_handler
from utils.constants import *
from utils import helpers as hp
import re
from utils import reset as rt
async def set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    datos_serie = update.message.text
    patron = r"^\d+,\d+(\.\d+)?(,\s*.*)?$"
    #await rt.reset_timer(update, context)
    

    if re.match(patron,datos_serie):
        datos = datos_serie.split(',')
        repes = datos[0]
        peso = datos[1]
        coment = datos[2] if len(datos) > 2 else None

        # Registrar ejercicio en el log
        grupo_actual = context.user_data.get('grupo', '')
        ejercicio_actual = context.user_data.get('ejercicio', '')

        hp.log_training(context)
        """
        'trainin_log' = {'grupo':,
                      'ejercicio':
                      'serie': [(reps,peso),(reps,peso)]}

        """
        # Buscar si ya existe un registro de este ejercicio en el training_log
        found = False
        for registro in context.user_data['training_log']:
            if registro['grupo'] == grupo_actual and registro['ejercicio'] == ejercicio_actual:
                registro['serie'].append((repes, peso, coment))  # Añadir nueva serie (reps, peso)
                found = True
                break

        # Si no se encuentra, agregar un nuevo registro
        if not found:
            nuevo_registro = {
                'grupo': grupo_actual,
                'ejercicio': ejercicio_actual,
                'serie': [(repes, peso, coment)]  # Iniciar la lista de series con la nueva serie
            }
            context.user_data['training_log'].append(nuevo_registro)

        inline_opciones = [
            [
                InlineKeyboardButton('Hacer otra serie',callback_data='NEW_SER'),
                InlineKeyboardButton('Cambiar ejercicio',callback_data='NEW_EJE')
            ],
            [
                InlineKeyboardButton('Mostrar entreno',callback_data='LOG')
            ],
            [
                InlineKeyboardButton('Finalizar entreno',callback_data='END')
            ]
        ]


        await update.message.reply_text(
            text = "Indique la siguiente acción a realizar:",
            reply_markup=InlineKeyboardMarkup(inline_opciones)
        )   

        return OPTIONS
    else:
        await update.message.reply_text(
            text = "*FORMATO INCORRECTO* \n Indica las repeticiones y el peso (formato: reps, peso(kg),coment):"
        )  
        return SET
async def set_handler_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    
    query = update.callback_query
    await query.answer()

    grupo_actual = context.user_data["grupo"]
    ejercicio_actual = context.user_data["ejercicio"]
    if query.data == "YES":
        hp.log_training(context)
        """
            'trainin_log' = {'grupo':,
                        'ejercicio':
                        'serie': [(reps,peso),(reps,peso)]}

            """
        grupo_actual = context.user_data["grupo"]
        ejercicio_actual = context.user_data["ejercicio"]
        repes = context.user_data["counter_repes"]
        peso = context.user_data["counter_peso"]
        coment = ""
        # Buscar si ya existe un registro de este ejercicio en el training_log
        found = False
        for registro in context.user_data['training_log']:
            if registro['grupo'] == grupo_actual and registro['ejercicio'] == ejercicio_actual:
                registro['serie'].append((repes, peso, coment))  # Añadir nueva serie (reps, peso)
                found = True
                break

            # Si no se encuentra, agregar un nuevo registro
        if not found:
            nuevo_registro = {
                'grupo': grupo_actual,
                'ejercicio': ejercicio_actual,
                'serie': [(repes, peso, coment)]  # Iniciar la lista de series con la nueva serie
            }
            context.user_data['training_log'].append(nuevo_registro)
    
    await query.edit_message_text(
        text = f"Indique la siguiente acción a realizar:\n {grupo_actual}-{ejercicio_actual}",
        reply_markup=InlineKeyboardMarkup(keyboard_opciones)
    )   
    
    return OPTIONS

