from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler
)

from counter import button_counter, change_counter, reset_counter


from utils.constants import *




button_handler = CommandHandler('counter', button_counter)
change_handler = CallbackQueryHandler(change_counter, '^change_counter:')
reset_handler  = CallbackQueryHandler(reset_counter, '^reset_counter$')