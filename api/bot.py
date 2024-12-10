from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = '7518401446:AAGSHaBaBJS5FqouZop33Ul_vlIaS6VcMbw'

# Comando inicial
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar si ya se envió la imagen
    user_id = update.effective_user.id
    if context.user_data.get("image_shown") is None:  # Si no existe la bandera
        # Enviar la imagen
        with open("C:/Users/heard/Desktop/ChatDjango-main/api/img/menu.jpg", "rb") as image:  # Reemplaza con la ruta a tu imagen
            await update.message.reply_photo(photo=image, caption="¡Bienvenido/a! 🌟")
        # Marcar que ya se envió la imagen
        context.user_data["image_shown"] = True
    
    keyboard = [
        [InlineKeyboardButton("Toma asistencia", callback_data='toma_asistencia')],
        [InlineKeyboardButton("Agenda", callback_data='agenda')],
        [InlineKeyboardButton("PREMIUM", callback_data='premium_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¡Hola! \nSoy tu asistente personal😁. \n\nSelecciona una opción del menú principal 🤔:", reply_markup=reply_markup)

# Manejar interacciones con botones
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Opción seleccionada
    if query.data == 'toma_asistencia':
        text = "Has seleccionado **Toma asistencia**. Claro, te voy a ayudar con la toma de asistencia."
    elif query.data == 'agenda':
        text = "Has seleccionado **Agenda**. Aquí puedes gestionar tus eventos y actividades."
    elif query.data == 'premium_menu':
        # Submenú para PREMIUM
        text = "Estás en el menú PREMIUM. Selecciona una opción:"
        keyboard = [
            [InlineKeyboardButton("Registro de actividades", callback_data='registro_actividades')],
            [InlineKeyboardButton("Generación de reportes", callback_data='generacion_reportes')],
            [InlineKeyboardButton("Envío de calificaciones", callback_data='envio_calificaciones')],
            [InlineKeyboardButton("Volver al menú principal", callback_data='menu_principal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return
    elif query.data == 'registro_actividades':
        text = "Has seleccionado **Registro de actividades**. Claro, te voy a ayudar con el registro de actividades."
    elif query.data == 'generacion_reportes':
        text = "Has seleccionado **Generación de reportes**. Claro, te voy a ayudar con la generación de reportes."
    elif query.data == 'envio_calificaciones':
        text = "Has seleccionado **Envío de calificaciones**. Claro, te voy a ayudar con el envío de calificaciones."
    else:
        text = "Opción no válida."

    # Botón para volver al menú principal
    keyboard = [[InlineKeyboardButton("Volver al menú principal", callback_data='menu_principal')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)

# Manejar el regreso al menú principal
async def main_menu(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Reconstruir el menú principal
    keyboard = [
        [InlineKeyboardButton("Toma asistencia", callback_data='toma_asistencia')],
        [InlineKeyboardButton("Agenda", callback_data='agenda')],
        [InlineKeyboardButton("PREMIUM", callback_data='premium_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("¡Hola! Selecciona una opción del menú principal:", reply_markup=reply_markup)

# Configuración de handlers
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(toma_asistencia|agenda|premium_menu|registro_actividades|generacion_reportes|envio_calificaciones)$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^menu_principal$"))

    print("Bot en ejecución...")
    app.run_polling()

if __name__ == "__main__":
    main()
