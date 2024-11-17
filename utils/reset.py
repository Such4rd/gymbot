from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
    Job
)
from utils.constants import *
import logging

async def timeout_handler(update, context:ContextTypes.DEFAULT_TYPE):
    """Función que se llama cuando la conversación se cierra por inactividad."""
    job = context.job
    await context.bot.send_message(job.chat_id, text="Se ha perdido la conexión por inactividad.")
    # Finalizar el flujo de conversación
    context.application.current_conversation_handler.end()

def remove_inactivity_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: str,job_queue):
    """Elimina cualquier temporizador de inactividad existente para evitar múltiples timers."""
    # Verificar si job_queue existe en el contexto
    if not hasattr(context, "job_queue") or context.job_queue is None:
        print("Error: context no tiene 'job_queue'")
        return  # Salir de la función si no hay job_queue

    # Obtener trabajos por nombre
    current_jobs = context.job_queue.get_jobs_by_name(chat_id)
    for job in current_jobs:
        job.schedule_removal()
        
async def reset_timer(update, context: ContextTypes.DEFAULT_TYPE, job_queue):
    """Configura un temporizador de inactividad para cancelar la conversación si no hay respuesta."""
    # Obtener el chat_id según el tipo de update (Message o CallbackQuery)
    if not hasattr(context, 'job_queue') or context.job_queue is None:
        logging.info("Error: 'job_queue' no está disponible en el contexto")
        return  # Sale de la función si no hay 'job_queue'
    
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    elif update.effective_chat:
        chat_id = update.effective_chat.id
    remove_inactivity_timer(context,str(chat_id),job_queue)
    
    context.job.run_once(timeout_handler, TIMEOUT_DURATION, chat_id=chat_id, name=str(chat_id))
