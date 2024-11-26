from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

TOKEN = '7701740230:AAFNt9Cm2b3NvEGTnHRdMfeOyrEf8Er8J38'

# Comando inicial
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Soy tu bot de Telegram.")

# Manejar mensajes de texto
async def echo(update: Update, context):
    user_message = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {user_message}")

# Configuración de handlers
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot en ejecución...")
    app.run_polling()

#Esto es un comentario