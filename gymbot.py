import db_utils as db
import os
from datetime import datetime
import logging
import re
from telegram import  ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

TOKEN = os.getenv('TOKEN')


# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Definir estados
START, GRUPO_MUSCULAR, EJERCICIO, SERIE, OPCIONES, SAVE, ENTRENOS, TRAIN_LOAD = range(8)



#ESTADO ENTRENOS SE IRA CUANDO SE QUIERA REPETIR UN ENTRENO
#ESTADO TRAIN_LOAD_EJERCICIO


# Función para agrupar los botones de 3 en 3
def grouped_buttons(buttons, group_size=3):
    return [buttons[i:i + group_size] for i in range(0, len(buttons), group_size)]


def log_training(context):
    #inicializamos el registro de entrenamiento
    if 'training_log' not in context.user_data:
        context.user_data['training_log'] = []


# Función de manejo de errores
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Error causado por {update} - {context.error}')
    
    if update.message:
        await update.message.reply_text(
            "¡Oops! Ha ocurrido un error. Por favor, intenta de nuevo más tarde."
        )
    elif update.callback_query:
        await update.callback_query.answer("¡Oops! Ha ocurrido un error. Por favor, intenta de nuevo más tarde.")

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

    return START

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el entrenamiento."""
    user = update.message.from_user
    logger.info("Usuario %s canceló el entrenamiento.", user.first_name)
    await update.message.reply_text("Entrenamiento cancelado.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

# Función que procesa los callback_data de grupos musculares
# ST: START -> CH : GESTIONA EL PRIMER PASO Y MUESTRA GRUPOS MUSCULARES
async def procesar_start(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"

    # Verificar qué botón fue presionado basado en el callback_data
    if query.data == 'NEW_EJE':

        GRUPOS_MUSCULARES = db.obtener_grupos_musculares(conexion)
        #configuramos tantos botones como grupos musculares
        inline_board = grouped_buttons([InlineKeyboardButton(musculo,callback_data=musculo) for musculo in GRUPOS_MUSCULARES])
        inline_board.append([InlineKeyboardButton("Nuevo grupo muscular",callback_data="NEW_GRU")])
        inline_board.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text(
            "Selecciona un grupo muscular:",
            reply_markup=InlineKeyboardMarkup(inline_board)
        )

        return GRUPO_MUSCULAR
    elif query.data == 'LOAD':
         # lista de opciones
        user = query.from_user.name.upper()
        ENTRENAMIENTOS = db.obtener_entrenos(conexion,user)
        inline_board_lista =  grouped_buttons([InlineKeyboardButton(entreno[1],callback_data=entreno[0]) for entreno in ENTRENAMIENTOS])

        await query.edit_message_text(
            text = "Seleccione un entreno para ver su resumen:",
            reply_markup=InlineKeyboardMarkup(inline_board_lista)
        )
        
        return ENTRENOS
    
    elif query.data == 'END':
        await query.edit_message_text(
            text = "Hasta luego Maricarmeeee!!:"
        )
        return ConversationHandler.END
    
# SELECCION DE GRUPO MUSCULAR Y MUESTRA LISTA DE EJERCICIOS DE ESE GRUPO 
async def procesar_grupo_muscular(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"

    # Verificar qué botón fue presionado basado en el callback_data
    if query.data != "NEW_GRU" and query.data != 'END':    
        context.user_data['grupo'] = query.data
        EJERCICIOS = db.obtener_ejercicios_por_grupo(conexion,query.data)
        inline_board_lista = grouped_buttons([InlineKeyboardButton(ejercicio,callback_data=ejercicio) for ejercicio in EJERCICIOS])
        inline_board_lista.append([InlineKeyboardButton("Nuevo ejercicio",callback_data="NEW_EJE")])
        inline_board_lista.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text(
            "Selecciona un ejercicio:",
            reply_markup=InlineKeyboardMarkup(inline_board_lista)
        )

        return EJERCICIO
    elif query.data == "NEW_GRU":
        print("hacemos insert en base de datos")
        await query.edit_message_text(
            "Indique el nombre del grupo:",
            reply_markup=None
        )
        return GRUPO_MUSCULAR
    elif query.data == 'END':
        await query.edit_message_text(
            mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]])
        )
        return SAVE   
    
#ST: EJERCICIO -> CH - SELECCIÓN DE EJERCICIO
async def procesar_ejercicio(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"
    # Verificar qué botón fue presionado basado en el callback_data
    

    if query.data == "NEW_EJE":
        print("hacemos insert en base de datos")
        await query.edit_message_text(
            "Indique el nombre del ejercicio:",
            reply_markup=None
        )
        return EJERCICIO
    elif query.data == 'END':
        await query.edit_message_text(
            mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]])
        )
        return SAVE 
    
    context.user_data['ejercicio'] = query.data
    await query.edit_message_text(
        text = "Indica las repeticiones y el peso (formato: reps, peso(kg)):",
        reply_markup=None
    )

    return SERIE
# ST: SERIE -_ MESSAGE_HANDLER
async def procesar_serie(update: Update, context: ContextTypes.DEFAULT_TYPE, conexion) ->int:
    datos_serie = update.message.text
    patron = r"^\d+,\d+(\.\d+)?(,\s*.*)?$"
    

    if re.match(patron,datos_serie):
        datos = datos_serie.split(',')
        repes = datos[0]
        peso = datos[1]
        coment = datos[2]

        # Registrar ejercicio en el log
        grupo_actual = context.user_data.get('grupo', '')
        ejercicio_actual = context.user_data.get('ejercicio', '')

        log_training(context)
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

        return OPCIONES
    else:
        await update.message.reply_text(
            text = "*FORMATO INCORRECTO* \n Indica las repeticiones y el peso (formato: reps, peso(kg)):"
        )  
        return SERIE


#ST : OPCIONES 
async def procesar_opciones(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()

    if query.data == "NEW_SER":
        await query.edit_message_text(
            text = "Indica las repeticiones y el peso (formato: reps, peso(kg)):",
            reply_markup=None
        )
       
        return SERIE
    
    elif query.data == "NEW_EJE":
        # Volver al inicio del flujo para seleccionar un nuevo ejercicio
        GRUPOS_MUSCULARES = db.obtener_grupos_musculares(conexion)
        inline_board = grouped_buttons([InlineKeyboardButton(musculo,callback_data=musculo) for musculo in GRUPOS_MUSCULARES])
        inline_board.append([InlineKeyboardButton("Nuevo grupo muscular",callback_data="NEW_GRU")])
        inline_board.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text("Selecciona un grupo muscular:", reply_markup=InlineKeyboardMarkup(inline_board))
        
        return GRUPO_MUSCULAR
    elif query.data == "LOG":
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
            mostrar_resumen(update,context),
            reply_markup=InlineKeyboardMarkup(inline_opciones)
        )
        return OPCIONES
    elif query.data == "END":
        await query.edit_message_text(
            mostrar_resumen(update,context),
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirmar guardado de entreno",callback_data="SAVE")]])
        )
        return SAVE



# Función que muestra el resumen del entrenamiento
#  
def mostrar_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Muestra el resumen del entrenamiento actual."""
    resumen = context.user_data.get('training_log', [])
    if not resumen:
        return "No hay ejercicios registrados aún."
    
    # Generar resumen en formato texto
    texto_resumen = "Resumen del entrenamiento actual:\n"
    for indice, grupos in enumerate(resumen,1):
        grupo = grupos['grupo']
        nombre_ejercicio = grupos['ejercicio']
        texto_resumen += f"{indice}. {grupo}: {nombre_ejercicio}\n"
        for i, (reps, peso, coment) in enumerate(grupos['serie'],1):
            texto_resumen += f"\t\t {i}. {reps} reps, {peso} KG."
            if coment:
           	 texto_resumen += f"({coment})\n"
            else: 
            	texto_resumen += "\n"   
    return texto_resumen


# Gestión de nuevos ejercicios, grupos, etc:
async def gestion_nuevo_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    nuevo = update.message.text

    # Verificar si es valido el string
    if not isinstance(nuevo, str) or not nuevo.strip() or any(char.isdigit() for char in nuevo) or len(nuevo) < 3 or len(nuevo) > 30:
        await update.message.reply_text(
            text="*Formato incorrecto*\n Indique el nombre del grupo(3-30 caracteres, sin números):"
        )
        return GRUPO_MUSCULAR
    
    nuevo = nuevo.capitalize()

    # Verificar si el grupo ya existe
    if db.grupo_existe(conexion, nuevo):
        await update.message.reply_text(
            text="*El grupo ya existe en la base de datos.* Indique un nombre diferente:"
        )
        return GRUPO_MUSCULAR

    context.user_data['grupo'] = nuevo

    db.insertar_grupo(conexion,nuevo)

    await update.message.reply_text(
        "Indique el nombre del nuevo ejercicio:",
        reply_markup=None
    )

    return EJERCICIO

# Gestión de nuevos ejercicios, grupos, etc:
async def gestion_nuevo_ejercicio(update: Update, context: ContextTypes.DEFAULT_TYPE, conexion) -> int:
    nuevo = update.message.text

    # Verificar si es valido el string
    if not isinstance(nuevo, str) or not nuevo.strip() or any(char.isdigit() for char in nuevo) or len(nuevo) < 3 or len(nuevo) > 30:
        await update.message.reply_text(
            text="*Formato incorrecto*\n Indique el nombre del ejercicio(3-30 caracteres, sin números)"
        )
        return EJERCICIO
    nuevo = nuevo.capitalize()
    grupo = context.user_data['grupo']

    # Verificar si el ejercicio ya existe
    if db.ejercicio_existe(conexion, nuevo):
        await update.message.reply_text(
            text="*El ejercicio ya existe en la base de datos.* Indique un nombre diferente:"
        )
        return EJERCICIO


    context.user_data['ejercicio'] = nuevo


    db.insertar_ejercicio(conexion,nuevo,grupo,update.message.from_user.id,update.message.date.date())
    # Insertar ejercicio en bs
    
    await update.message.reply_text(
        text = "Indica las repeticiones y el peso (formato: reps, peso(kg)):",
        reply_markup=None
    )

    return SERIE

#Guardamos entreno en BBDD
async def procesar_guardado(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"
    # Verificar qué botón fue presionado basado en el callback_data
    
    if query.data == "SAVE" and 'training_log' in context.user_data:
        
        #recoger usuario
        usuario = query.from_user.name
        usuario = usuario.replace('@','').upper() # Obtén el nombre completo del usuario de Telegram
        id_entreno = db.generar_id_entreno(conexion,usuario)  # Genera el ID del entrenamiento

        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')

        datos_entreno = context.user_data['training_log']
        db.insertar_entreno(conexion, datos_entreno,usuario,fecha_actual,id_entreno)
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


async def load_entreno(update: Update, context: ContextTypes.DEFAULT_TYPE,conexion) -> int:
    query = update.callback_query
    await query.answer()

    datos_entreno = query.data #id del entreno
    
    context.user_data['training_log'] = db.load_entreno(conexion,datos_entreno)
    
    await query.edit_message_text(
           f"{mostrar_resumen(update,context) }"
        )
    return ConversationHandler.END



def main() -> None:
    """Inicia el bot."""
    application = Application.builder().token(TOKEN).build()
    #mantenemos la conexión a base de datos mientras se lleva la conversacion:
    with db.conectar_db() as con:

        # Manejador de la conversación
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                START: [CallbackQueryHandler(lambda update, context: procesar_start(update, context, conexion=con))],
                ENTRENOS: [CallbackQueryHandler(lambda update, context: load_entreno(update, context, conexion=con))],
                TRAIN_LOAD: [
                    CallbackQueryHandler(lambda update, context: load_entreno(update, context, conexion=con))
                ],
                GRUPO_MUSCULAR: [
                    CallbackQueryHandler(lambda update, context: procesar_grupo_muscular(update, context, conexion=con)),
                    MessageHandler(filters.TEXT,lambda update, context: gestion_nuevo_grupo(update, context, conexion=con))
                ],
                EJERCICIO: [
                    CallbackQueryHandler(lambda update, context: procesar_ejercicio(update, context, conexion=con)),
                    MessageHandler(filters.TEXT,lambda update, context: gestion_nuevo_ejercicio(update, context, conexion=con))
                ],
                SERIE: [
                    MessageHandler(filters.TEXT, lambda update, context: procesar_serie(update, context, conexion=con))
                ],
                OPCIONES: [CallbackQueryHandler(lambda update, context: procesar_opciones(update, context, conexion=con))],
                SAVE:[CallbackQueryHandler(lambda update, context: procesar_guardado(update, context, conexion=con))]
            },
            fallbacks=[CommandHandler("cancel", cancelar)],
        )

        
        application.add_handler(conv_handler)
        # Ejecutar el bot
        application.run_polling()

if __name__ == "__main__":
    main()
