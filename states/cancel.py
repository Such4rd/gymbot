from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ( 
    ContextTypes,
    ConversationHandler
)
from utils import reset as rt

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el entrenamiento."""
    user = update.message.from_user
    print("[!] Se ha cancelado el entreno")
    #logger.info("Usuario %s canceló el entrenamiento.", user.first_name)
    await update.message.reply_text("Entrenamiento cancelado.", reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END