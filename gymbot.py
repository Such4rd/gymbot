import sqlite3
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


TOKEN = os.getenv('TOKEN')






# Conexión a la base de datos
def conectar_db():
    return sqlite3.connect('/app/gym.db')



#crear tablas si no existen

conectar_db().cursor().execute(
    '''
    CREATE TABLE IF NOT EXISTS grupos_musculares (
    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_grupo TEXT
    )
    '''
)

#Creación de la tabla ejercicios
conectar_db().cursor().execute(
    '''
    CREATE TABLE IF NOT EXISTS ejercicios (
    id_ejercicio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_ejercicio TEXT,
    id_grupo INTEGER,
    id_user TEXT,
    date DATE,
    FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo)
)
'''
)

#Creación de la tabla entrenamientos
conectar_db().cursor().execute(
    '''
    CREATE TABLE IF NOT EXISTS entrenamientos (
    id_entreno TEXT,
    id_user TEXT,
    date DATE,
    coment TEXT,
    PRIMARY KEY (id_entreno)
    )'''
)

#Creación de la tabla series
conectar_db().cursor().execute(
    '''
    CREATE TABLE IF NOT EXISTS series (
    id_entreno TEXT,
    id_grupo INTEGER,
    id_ejercicio INTEGER,
    id_serie INTEGER,
    repes INTEGER,
    peso REAL,
    coment TEXT,
    PRIMARY KEY (id_entreno, id_grupo, id_ejercicio, id_serie),
    FOREIGN KEY (id_entreno) REFERENCES entrenamientos(id_entreno),
    FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo),
    FOREIGN KEY (id_ejercicio) REFERENCES ejercicios(id_ejercicio)
    )
    '''
)

#obtenemos grupos musculares
def obtener_grupos_musculares():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_grupo FROM grupos_musculares")
    grupos = cursor.fetchall()
    conn.close()
    return [g[0] for g in grupos] 

def obtener_ejercicios_por_grupo(grupo):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_ejercicio FROM ejercicios WHERE id_grupo = (SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?)", (grupo,))
    ejercicios = cursor.fetchall()
    conn.close()
    return [e[0] for e in ejercicios]  # Devuelve solo los nombres


def generar_id_entreno(usuario):
    fecha = datetime.now().strftime('%d%m%Y')  # Formato DíaMesAño
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM ENTRENAMIENTOS WHERE ID_USER = ?",(usuario,)
    )
    # Obtener el resultado de la query
    count = cursor.fetchone()[0]  # El resultado de COUNT(*) está en el primer (y único) elemento de la tupla

    # Cerrar cursor y conexión
    cursor.close()
    conn.close()

    # Generar el ID en formato '04082024-usuario-#entreno'
    id_entreno = f"{fecha}-{usuario}-{count + 1}"  # Sumamos 1 para obtener el número de entreno siguiente
    
    return id_entreno


# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Definir estados
START, GRUPO_MUSCULAR, EJERCICIO, SERIE, OPCIONES, SAVE = range(6)

# Grupos musculares y ejercicios de ejemplo
#GRUPOS_MUSCULARES = ["Pecho", "Espalda", "Piernas", "Hombros", "Biceps", "Triceps"]
#EJERCICIOS = {
#    "Pecho": ["Press banca", "Aperturas", "Flexiones"],
#    "Espalda": ["Dominadas", "Remo", "Peso muerto"],
#    "Piernas": ["Sentadillas", "Prensa", "Zancadas"],
    # Y así con los demás grupos musculares...
#}

# Función para agrupar los botones de 3 en 3
def grouped_buttons(buttons, group_size=3):
    return [buttons[i:i + group_size] for i in range(0, len(buttons), group_size)]


def log_training(context):
    #inicializamos el registro de entrenamiento
    if 'training_log' not in context.user_data:
        context.user_data['training_log'] = []



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación y ofrece opciones de entrenamiento."""
    inline_board_button = [[InlineKeyboardButton("Nuevo entrenamiento",callback_data='NEW_EJE'), InlineKeyboardButton("Finalizar entrenamiento",callback_data='END')]] # lista de opciones

    await update.message.reply_text(
        "¿Quiere realizar un nuevo entrenamiento?",
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
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"

    # Verificar qué botón fue presionado basado en el callback_data
    if query.data == 'NEW_EJE':

        GRUPOS_MUSCULARES = obtener_grupos_musculares()
        #configuramos tantos botones como grupos musculares
        inline_board = grouped_buttons([InlineKeyboardButton(musculo,callback_data=musculo) for musculo in GRUPOS_MUSCULARES])
        inline_board.append([InlineKeyboardButton("Nuevo grupo muscular",callback_data="NEW_GRU")])
        inline_board.append([InlineKeyboardButton("Finalizar entreno",callback_data="END")])
        await query.edit_message_text(
            "Selecciona un grupo muscular:",
            reply_markup=InlineKeyboardMarkup(inline_board)
        )

        return GRUPO_MUSCULAR
    
    elif query.data == 'END':
        return ConversationHandler.END
#ST: GRUPO_MUSCULAR -> CH - SELECCION DE GRUPO MUSCULAR Y MUESTRA LISTA DE EJERCICIOS DE ESE GRUPO 
async def button_callback_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"

    # Verificar qué botón fue presionado basado en el callback_data
    if query.data != "NEW_GRU" and query.data != 'END':    
        context.user_data['grupo'] = query.data
        EJERCICIOS = obtener_ejercicios_por_grupo(query.data)
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
async def button_callback_3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
async def datos_serie(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    datos_serie = update.message.text
    patron = r"^\d+,\d+$"

    if re.match(patron,datos_serie):
        datos = datos_serie.split(',')
        repes = datos[0]
        peso = datos[1]

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
                registro['serie'].append((repes, peso))  # Añadir nueva serie (reps, peso)
                found = True
                break

        # Si no se encuentra, agregar un nuevo registro
        if not found:
            nuevo_registro = {
                'grupo': grupo_actual,
                'ejercicio': ejercicio_actual,
                'serie': [(repes, peso)]  # Iniciar la lista de series con la nueva serie
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
async def button_callback_4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        GRUPOS_MUSCULARES = obtener_grupos_musculares()
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
        for i, (reps, peso) in enumerate(grupos['serie'],1):
            texto_resumen += f"\t\t {i}. {reps} reps, {peso} KG.\n"
    
    return texto_resumen


# Gestión de nuevos ejercicios, grupos, etc:
async def gestion_nuevo_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nuevo = update.message.text

    # Verificar si es valido el string
    if not isinstance(nuevo, str) or not nuevo.strip() or any(char.isdigit() for char in nuevo):
        await update.message.reply_text(
            text="*Formato incorrecto*\n Indique el nombre del grupo:"
        )
        return GRUPO_MUSCULAR
    nuevo = nuevo.capitalize()
    context.user_data['grupo'] = nuevo

    # Insertar grupo
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO grupos_musculares (nombre_grupo) VALUES (?)", (nuevo,))
                   
    conn.commit()
    conn.close()

    await update.message.reply_text(
        "Indique el nombre del nuevo ejercicio:",
        reply_markup=None
    )

    return EJERCICIO

# Gestión de nuevos ejercicios, grupos, etc:
async def gestion_nuevo_ejercicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nuevo = update.message.text

    # Verificar si es valido el string
    if not isinstance(nuevo, str) or not nuevo.strip() or any(char.isdigit() for char in nuevo):
        await update.message.reply_text(
            text="*Formato incorrecto*\n Indique el nombre del ejercicio:"
        )
        return EJERCICIO
    nuevo = nuevo.capitalize()
    grupo = context.user_data['grupo']
    context.user_data['ejercicio'] = nuevo

    # Insertar ejercicio en bs
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?", (grupo,))
    result = cursor.fetchone()
    # Suponiendo que tienes una tabla 'grupos_musculares'
    cursor.execute("INSERT INTO ejercicios (nombre_ejercicio, id_grupo, id_user, date) VALUES (?, ?, ?, ?)", 
                   (nuevo, result[0], update.message.from_user.id, update.message.date.date() ))           
    conn.commit()
    conn.close()

    await update.message.reply_text(
        text = "Indica las repeticiones y el peso (formato: reps, peso(kg)):",
        reply_markup=None
    )

    return SERIE

#Guardamos entreno en BBDD
async def save_entreno(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa la selección del botón."""
    query = update.callback_query
    await query.answer()  # Es necesario responder al callback para evitar que el botón quede "en espera"
    # Verificar qué botón fue presionado basado en el callback_data
    
    if query.data == "SAVE" and 'training_log' in context.user_data:
        
        #recoger usuario
        usuario = query.from_user.name
        usuario = usuario.replace('@','').upper() # Obtén el nombre completo del usuario de Telegram
        id_entreno = generar_id_entreno(usuario)  # Genera el ID del entrenamiento

        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')

        # Insertar entrenamiento en la tabla de entrenamientos
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entrenamientos (id_entreno, id_user, date, coment) VALUES (?, ?, ?, ?)", 
                       (id_entreno, usuario, fecha_actual, ''))

        # Insertar series en la tabla de series
        for registro in context.user_data['training_log']:
            grupo = registro['grupo']
            ejercicio = registro['ejercicio']
            for i, (repes, peso) in enumerate(registro['serie'],1):
                cursor.execute("""
                    INSERT INTO series (id_entreno, id_grupo, id_ejercicio, id_serie, repes, peso, coment)
                    VALUES (?, (SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?), 
                    (SELECT id_ejercicio FROM ejercicios WHERE nombre_ejercicio = ?), ?, ?, ?, '')
                """, (id_entreno, grupo, ejercicio, i, repes, peso))
        
        conn.commit()
        conn.close()

        await query.edit_message_text(
            text = "ENTRENO REGISTRADO CORRECTAMENTE! HASTA EL PROXIMO ENTRENO",
            reply_markup=None
        )
        context.user_data['training_log'] = []
        return ConversationHandler.END
    else:
        await query.edit_message_text(
            text = "[ERROR] Entrenamiento vacio, empiece de nuevo (/start)",
            reply_markup=None
        )
        return ConversationHandler.END



def main() -> None:
    """Inicia el bot."""
    application = Application.builder().token(TOKEN).build()

    # Manejador de la conversación
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CallbackQueryHandler(button_callback)],
            GRUPO_MUSCULAR: [
                CallbackQueryHandler(button_callback_2),
                MessageHandler(filters.TEXT,gestion_nuevo_grupo)
            ],
            EJERCICIO: [
                CallbackQueryHandler(button_callback_3),
                MessageHandler(filters.TEXT,gestion_nuevo_ejercicio)
            ],
            SERIE: [MessageHandler(filters.TEXT, datos_serie)],
            OPCIONES: [CallbackQueryHandler(button_callback_4)],
            SAVE:[CallbackQueryHandler(save_entreno)]
        },
        fallbacks=[CommandHandler("cancel", cancelar)],
    )

    application.add_handler(conv_handler)
    # Ejecutar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
