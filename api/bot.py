import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = '7701740230:AAFNt9Cm2b3NvEGTnHRdMfeOyrEf8Er8J38'

# Diccionario para registrar los IDs de los usuarios
user_ids = {}

# Variable para almacenar el estado de envío de mensajes
awaiting_message_input = {}
selected_target_user = {}

# Conectar a la base de datos SQLite y crear la tabla si no existe
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Crear la tabla 'users' si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Inicializar la base de datos al arrancar el bot
init_db()

# Comando inicial
async def start(update: Update, context):
    # Obtener información del usuario
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    # Conectar a la base de datos y agregar el usuario si no está registrado
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Verificar si el usuario ya está registrado
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        # Si no está registrado, insertar al usuario en la base de datos
        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                       (user_id, user_name, update.message.from_user.first_name))
        conn.commit()
        print(f"Usuario registrado: {user_id} - {user_name}")
    else:
        print(f"El usuario ya está registrado: {user_id} - {user_name}")

    conn.close()

    # URL o archivo de la imagen a mostrar
    image_url = "https://articulandoo.com/wp-content/uploads/2023/04/Quieres-ser-mas-Eficiente-como-Docente-Descubre-como-la-IA-Generativa-puede-Ayudarte-a-Lograrlo-scaled.jpg"

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
        # Mostrar los usuarios registrados
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('SELECT user_id, username, first_name FROM users')
        users = cursor.fetchall()
        conn.close()

        if not users:
            text = "🚫 No hay usuarios registrados para enviarles mensajes."
        else:
            text = "📈 **Enviar mensaje a un usuario**: Elige el usuario al que deseas enviar un mensaje."

            keyboard = []
            for user_id, username, first_name in users:
                button_text = f"{first_name or 'Sin nombre'} ({username or 'Desconocido'}) - ID: {user_id}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"send_message_{user_id}")])

            # Botón para volver al menú principal
            keyboard.append([InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)
        return
    else:
        text = "⚠️ Opción no válida. ¡Por favor, selecciona una opción del menú! 😅"

    # Botón para volver al menú principal
    keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)

# Manejar el ingreso del mensaje para el usuario seleccionado
async def handle_message(update: Update, context):
    user_id = update.message.from_user.id

    if user_id in awaiting_message_input and awaiting_message_input[user_id]:
        target_user_id = selected_target_user[user_id]  # Obtener el usuario seleccionado

        # Enviar el mensaje al usuario seleccionado
        try:
            await context.bot.send_message(chat_id=target_user_id, text=update.message.text)
            await update.message.reply_text("✅ *Mensaje enviado con éxito* 🎉")

            # Restablecer el estado de espera
            awaiting_message_input[user_id] = False
            del selected_target_user[user_id]
        except Exception as e:
            await update.message.reply_text(f"❌ Error al enviar el mensaje: {e}")
    else:
        await update.message.reply_text("⚠️ No hay ninguna acción pendiente. ¡Por favor, selecciona una opción del menú! 😊")

# Manejar la selección de usuario para enviar mensaje
async def send_message_to_user(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Extraer el ID del usuario seleccionado
    target_user_id = int(query.data.split('_')[2])

    # Guardar el usuario seleccionado para enviar el mensaje
    selected_target_user[query.from_user.id] = target_user_id

    # Marcar que ahora estamos esperando el mensaje del administrador
    awaiting_message_input[query.from_user.id] = True

    # Pedir al administrador que ingrese el mensaje
    text = f"📈 Ahora, por favor, ingresa el mensaje que deseas enviar al usuario con ID {target_user_id}."

    # Botón para volver al menú principal
    keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup)

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
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Obtener todos los usuarios registrados
    cursor.execute('SELECT user_id, username, first_name FROM users')
    users = cursor.fetchall()

    conn.close()

    if not users:
        await update.message.reply_text("🚫 No hay usuarios registrados aún.")
    else:
        users_list = "👥 *Usuarios registrados*:\n"
        for user_id, username, first_name in users:
            users_list += f"👤 {first_name or 'Sin nombre'} ({username or 'Desconocido'}) - ID: {user_id}\n"
        await update.message.reply_text(users_list)

# Configuración de handlers
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show_users", show_users))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(toma_asistencia|agenda|premium_menu|registro_actividades|generacion_reportes|envio_calificaciones)$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^menu_principal$"))
    app.add_handler(CallbackQueryHandler(send_message_to_user, pattern="^send_message_(\d+)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot en ejecución... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
