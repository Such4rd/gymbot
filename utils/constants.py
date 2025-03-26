from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import utils.emojis as meme
START, MUSCLE_GROUP, EXERCISE, SET, CONFIRM, OPTIONS, SAVE, WORKOUT = range(8)

TIMEOUT_DURATION = 10 #5 segundod



def keyboard_series(counter_repes,counter_peso,intervalo,grupo,ejercicio,mejor_marca):
    keyboard = [
        [
            InlineKeyboardButton(text=f" {grupo} - {ejercicio}\n {meme.GOLD} {mejor_marca}" , callback_data='None')  # Esto no hace nada, es solo texto
        ],
        [   
            InlineKeyboardButton(text='Repeticiones:', callback_data='None:'),
            InlineKeyboardButton(text=meme.MINUS, callback_data='counter_repes:-1'),
            InlineKeyboardButton(text=str(counter_repes), callback_data='None:'),
            InlineKeyboardButton(text=meme.PLUS, callback_data='counter_repes:+1'),
            InlineKeyboardButton(text='-', callback_data='None:'),
        ],
        [   
            InlineKeyboardButton(text='Peso:', callback_data='None:'),
            InlineKeyboardButton(text=meme.MINUS, callback_data='counter_peso:-1'),
            InlineKeyboardButton(text=str(counter_peso), callback_data='None:'),
            InlineKeyboardButton(text=meme.PLUS, callback_data='counter_peso:+1'),
            InlineKeyboardButton(text=str(intervalo), callback_data='intervalo:'),
        ],
        [
            InlineKeyboardButton(text=f"Guardar serie {meme.ADVANCE}", callback_data='save_serie:'),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


keyboard_confirm =  [
        [
            InlineKeyboardButton(text=f"SI" , callback_data='YES'),
            InlineKeyboardButton(text=f"NO" , callback_data='NO') # Esto no hace nada, es solo texto
        ]
]

keyboard_opciones = [
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