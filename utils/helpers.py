from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( 
    ContextTypes
)

def grouped_buttons(buttons, group_size=3):
    return [buttons[i:i + group_size] for i in range(0, len(buttons), group_size)]


def log_training(context):
    #inicializamos el registro de entrenamiento
    if 'training_log' not in context.user_data:
        context.user_data['training_log'] = []

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
                texto_resumen += f"({coment})\n" if coment else  "\n"  
    
    return texto_resumen