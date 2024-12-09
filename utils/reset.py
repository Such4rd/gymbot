from telegram import Update
from telegram.ext import ContextTypes
import logging
from utils.constants import TIMEOUT_DURATION

async def timeout_handler(update, context: ContextTypes.DEFAULT_TYPE):
    """Función que se llama cuando la conversación se cierra por inactividad."""
    job = context.job
    await context.bot.send_message(job.chat_id, text="Se ha perdido la conexión por inactividad.")
    context.application.current_conversation_handler.end()  # Finalizar conversación

def remove_inactivity_timer(context: ContextTypes.DEFAULT_TYPE, chat_id: str):
    """Elimina cualquier temporizador de inactividad existente."""
    if not hasattr(context.application, "job_queue") or context.application.job_queue is None:
        logging.error("Error: 'job_queue' no está disponible en la aplicación.")
        return

    job_queue = context.application.job_queue
    current_jobs = job_queue.get_jobs_by_name(chat_id)
    for job in current_jobs:
        job.schedule_removal()
    logging.info(f"Timers eliminados para chat_id: {chat_id}")

async def reset_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configura un temporizador de inactividad."""
    logging.info(f"VALOR JOBQUEUEEUEUE: {context.application.job_queue}")
    if not hasattr(context.application, 'job_queue') or context.application.job_queue is None:
        logging.error("Error: 'job_queue' no está disponible en la aplicación.")
        return

    # Determinar el chat_id
    chat_id = (
        update.message.chat_id
        if update.message
        else update.callback_query.message.chat_id
    )
    
    # Elimina temporizadores previos
    remove_inactivity_timer(context, str(chat_id))

    # Agregar nuevo temporizador
    context.application.job_queue.run_once(
        timeout_handler, TIMEOUT_DURATION, chat_id=chat_id, name=str(chat_id)
    )
    logging.info(f"Nuevo temporizador configurado para chat_id: {chat_id}")
