from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = '7701740230:AAFNt9Cm2b3NvEGTnHRdMfeOyrEf8Er8J38'

# Diccionario para registrar los IDs de los usuarios
user_ids = {}

# Variable para almacenar el estado de envío de mensajes
awaiting_message_input = {}

# Comando inicial
async def start(update: Update, context):
    # Registrar el ID del usuario
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name
    user_ids[user_id] = user_name
    print(f"Usuario registrado: {user_id} - {user_name}")

    # URL o archivo de la imagen a mostrar
    image_url = "https://articulandoo.com/wp-content/uploads/2023/04/Quieres-ser-mas-Eficiente-como-Docente-Descubre-como-la-IA-Generativa-puede-Ayudarte-a-Lograrlo-scaled.jpg"  # Reemplaza con la URL de tu imagen o usa un archivo local

    # Enviar la imagen primero
    await update.message.reply_photo(photo=image_url, caption="🎉 ¡Bienvenido a *AulaTech* 🎓!\nTu asistente para una educación más eficiente ✨")

    # Crear el menú de botones
    keyboard = [
        [InlineKeyboardButton("📝 Toma asistencia", callback_data='toma_asistencia')],
        [InlineKeyboardButton("📅 Agenda", callback_data='agenda')],
        [InlineKeyboardButton("💎 Hazte PREMIUM", callback_data='premium_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar el mensaje con los botones
    await update.message.reply_text("✨ *Selecciona una opción del menú:*", reply_markup=reply_markup)

# Manejar interacciones con botones
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Opción seleccionada
    if query.data == 'toma_asistencia':
        text = "📝 **Toma asistencia**: ¡Claro! Te voy a ayudar con la toma de asistencia 🙌"
    elif query.data == 'agenda':
        text = "📅 **Agenda**: Aquí puedes gestionar tus eventos y actividades 📅📋"
    elif query.data == 'premium_menu':
        # Submenú para PREMIUM
        text = "💎 Accede a alguna opción *PREMIUM*:"
        keyboard = [
            [InlineKeyboardButton("🔖 Registro de actividades", callback_data='registro_actividades')],
            [InlineKeyboardButton("📊 Generación de reportes", callback_data='generacion_reportes')],
            [InlineKeyboardButton("📈 Envío de calificaciones", callback_data='envio_calificaciones')],
            [InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return
    elif query.data == 'registro_actividades':
        text = "🔖 **Registro de actividades**: ¡Perfecto! Vamos a registrar actividades 📚✍️"
    elif query.data == 'generacion_reportes':
        text = "📊 **Generación de reportes**: Te ayudaré a generar los reportes que necesitas 📄✅"
    elif query.data == 'envio_calificaciones':
        # Pedir al usuario que ingrese un ID y mensaje
        user_id = query.from_user.id
        awaiting_message_input[user_id] = True
        text = "📈 **Envío de calificaciones**: Por favor, ingresa el ID del usuario y el mensaje. Ejemplo:\n7063731054 Tus calificaciones son: 80"
    else:
        text = "⚠️ Opción no válida. ¡Por favor, selecciona una opción del menú! 😅"

    # Botón para volver al menú principal
    keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)

# Manejar el ingreso de un ID y mensaje
async def handle_message(update: Update, context):
    user_id = update.message.from_user.id

    if user_id in awaiting_message_input and awaiting_message_input[user_id]:
        awaiting_message_input[user_id] = False  # Resetear estado
        try:
            # Extraer ID y mensaje
            message_text = update.message.text
            target_id, message = message_text.split(' ', 1)
            target_id = int(target_id)

            # Enviar mensaje al usuario especificado
            await context.bot.send_message(chat_id=target_id, text=message)
            await update.message.reply_text("✅ *Mensaje enviado con éxito* 🎉")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al enviar el mensaje: {e}")
    else:
        await update.message.reply_text("⚠️ No hay ninguna acción pendiente. ¡Por favor, selecciona una opción del menú! 😊")

# Manejar el regreso al menú principal
async def main_menu(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Reconstruir el menú principal
    keyboard = [
        [InlineKeyboardButton("📝 Toma asistencia", callback_data='toma_asistencia')],
        [InlineKeyboardButton("📅 Agenda", callback_data='agenda')],
        [InlineKeyboardButton("💎 Hazte PREMIUM", callback_data='premium_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("✨ *Selecciona una opción del menú:*", reply_markup=reply_markup)

# Comando para mostrar usuarios registrados
async def show_users(update: Update, context):
    if not user_ids:
        await update.message.reply_text("🚫 No hay usuarios registrados aún.")
    else:
        users_list = "👥 *Usuarios registrados*:\n"
        for user_id, user_name in user_ids.items():
            users_list += f"👤 {user_name} ({user_id})\n"
        await update.message.reply_text(users_list)

# Configuración de handlers
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show_users", show_users))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(toma_asistencia|agenda|premium_menu|registro_actividades|generacion_reportes|envio_calificaciones)$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^menu_principal$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot en ejecución... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
