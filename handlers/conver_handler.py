from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from states import start, exercise_handler,muscle_group_handler,options_handler,save_handler,set_handler,start_handler,workout_handler,new_exercise_handler,cancel_handler

from utils.constants import *

# Manejador de la conversación
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CommandHandler("workouts", start_handler)
    ],
    states={
        START: [CallbackQueryHandler(start_handler)],
        WORKOUT: [CallbackQueryHandler(workout_handler)],
        MUSCLE_GROUP: [CallbackQueryHandler(muscle_group_handler)],
        EXERCISE: [
            CallbackQueryHandler( exercise_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND,new_exercise_handler)
        ],
        SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_handler)],
        OPTIONS: [CallbackQueryHandler(options_handler)],
        SAVE:[CallbackQueryHandler(save_handler)]
    },
    fallbacks=[
        CommandHandler("cancel", cancel_handler),
        CommandHandler("workouts", workout_handler)
    ]
)
