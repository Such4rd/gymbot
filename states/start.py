from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes,
    ConversationHandler,
    JobQueue
)
from utils.constants import *
from utils import db_utils as db
from utils import helpers as hp
from utils import reset as rt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación y ofrece opciones de entrenamiento."""
    inline_board_button = [
        [InlineKeyboardButton("Nuevo entrenamiento",callback_data='NEW_EJE')], 
        [InlineKeyboardButton("Cargar entrenamiento",callback_data='LOAD')],
        [InlineKeyboardButton("Finalizar entrenamiento",callback_data='END')]] # lista de opciones

    context.user_data['training_log'] = [] 
    user = update.effective_user  # Obtiene el usuario que interactuó
    username = user.username if user.username else user.first_name  # Se obtiene el nombre de usuario o el nombre
    
    await update.message.reply_text(
        f"Bueeeenaaassss {username} !!! Bienvenido! ",
        reply_markup=InlineKeyboardMarkup(inline_board_button)
    )
    #await rt.reset_timer(update, context)

    return START

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón o el comando."""
    #await rt.reset_timer(update, context)
    # Verificar si la función fue llamada desde un CallbackQuery o un CommandHandler
    if update.callback_query:
        query = update.callback_query
        await query.answer()  # Responder al callback para evitar que el botón quede "en espera"
        data = query.data  # `data` contiene el valor de `callback_data` del botón
    else:
        # Si no es un CallbackQuery, asume que fue llamado desde un CommandHandler
        data = 'LOAD' 
    # Verificar qué botón fue presionado basado en el callback_data
    if data == 'NEW_EJE':
        muscles = db.obtener_grupos_musculares()
        #configuramos tantos botones como grupos musculares
        inline_board = hp.grouped_buttons([InlineKeyboardButton(musculo,callback_data=musculo) for musculo in muscles])
        #inline_board.append([InlineKeyboardButton("Nuevo grupo muscular",callback_data="NEW_GRU")])
        inline_board.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text(
            "Selecciona un grupo muscular:",
            reply_markup=InlineKeyboardMarkup(inline_board)
        )
        return MUSCLE_GROUP
    
    elif data == 'LOAD':
        user = update.effective_user.name.upper()
        workouts = db.obtener_entrenos(user)
        inline_board_lista = hp.grouped_buttons(
            [InlineKeyboardButton(entreno[1], callback_data=entreno[0]) for entreno in workouts]
        )
        if update.callback_query:
            await query.edit_message_text(
                text="Seleccione un entreno para ver su resumen:",
                reply_markup=InlineKeyboardMarkup(inline_board_lista)
            )
        else:
            await update.message.reply_text(
                text="Seleccione un entreno para ver su resumen:",
                reply_markup=InlineKeyboardMarkup(inline_board_lista)
            )
        
        return WORKOUT
    
    elif data == 'END':
        await query.edit_message_text(
            text = "Hasta luego Maricarmeeen!"
        )
        return ConversationHandler.END
    

    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"

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
    elif query.data == "NEW_GRU":
        print("hacemos insert en base de datos")
        await query.edit_message_text(
            "Indique el nombre del grupo:",
            reply_markup=None
        )
        return MUSCLE_GROUP
    elif query.data == 'END':
        await query.edit_message_text(
            hp.mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]])
        )
        return SAVE   