import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = '7701740230:AAFNt9Cm2b3NvEGTnHRdMfeOyrEf8Er8J38'

# Diccionario para registrar los IDs de los usuarios
awaiting_message_input = {}
selected_target_user = {}
send_to_all = {}

# Conectar a la base de datos SQLite y crear la tabla si no existe
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
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

# Función segura para editar mensajes y evitar errores de "Message is not modified"
async def safe_edit_message(query, text, reply_markup=None):
    current_text = query.message.text
    current_reply_markup = query.message.reply_markup
    if current_text != text or current_reply_markup != reply_markup:
        await query.edit_message_text(text=text, reply_markup=reply_markup)

# Comando inicial
async def start(update: Update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    # Registrar al usuario si no está registrado
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                       (user_id, user_name, update.message.from_user.first_name))
        conn.commit()
        print(f"Usuario registrado: {user_id} - {user_name}")
    else:
        print(f"El usuario ya está registrado: {user_id} - {user_name}")

    conn.close()

    # Enviar mensaje de bienvenida
    image_url = "https://articulandoo.com/wp-content/uploads/2023/04/Quieres-ser-mas-Eficiente-como-Docente-Descubre-como-la-IA-Generativa-puede-Ayudarte-a-Lograrlo-scaled.jpg"
    await update.message.reply_photo(photo=image_url, caption="🎉 ¡Bienvenido a *AulaTech* 🎓!\nTu asistente para una educación más eficiente ✨")

    # Crear el menú
    keyboard = [
        [InlineKeyboardButton("📝 Toma asistencia", callback_data='toma_asistencia')],
        [InlineKeyboardButton("📅 Agenda", callback_data='agenda')],
        [InlineKeyboardButton("💎 Hazte PREMIUM", callback_data='premium_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ *Selecciona una opción del menú:*", reply_markup=reply_markup)

# Manejar interacciones con botones
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'toma_asistencia':
        text = "📝 **Toma asistencia**: ¡Claro! Te voy a ayudar con la toma de asistencia 🙌"
    elif query.data == 'agenda':
        text = "📅 **Agenda**: Aquí puedes gestionar tus eventos y actividades 📅📋"
    elif query.data == 'premium_menu':
        text = "💎 Accede a alguna opción *PREMIUM*:"
        keyboard = [
            [InlineKeyboardButton("🔖 Registro de actividades", callback_data='registro_actividades')],
            [InlineKeyboardButton("📊 Generación de reportes", callback_data='generacion_reportes')],
            [InlineKeyboardButton("📈 Envío de calificaciones", callback_data='envio_calificaciones')],
            [InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text=text, reply_markup=reply_markup)
        return
    elif query.data == 'envio_calificaciones':
        # Mostrar usuarios registrados
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, first_name FROM users')
        users = cursor.fetchall()
        conn.close()

        if not users:
            text = "🚫 No hay usuarios registrados."
        else:
            text = "📈 **Enviar mensaje a un usuario**: Elige el usuario o selecciona 'Enviar a todos'."
            keyboard = [[InlineKeyboardButton(f"{user[2]} ({user[1]})", callback_data=f"send_message_{user[0]}")] for user in users]
            keyboard.append([InlineKeyboardButton("✉️ Enviar a todos", callback_data='send_to_all')])
            keyboard.append([InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_edit_message(query, text=text, reply_markup=reply_markup)
        return
    elif query.data == 'menu_principal':
        # Volver al menú principal
        keyboard = [
            [InlineKeyboardButton("📝 Toma asistencia", callback_data='toma_asistencia')],
            [InlineKeyboardButton("📅 Agenda", callback_data='agenda')],
            [InlineKeyboardButton("💎 Hazte PREMIUM", callback_data='premium_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text="✨ *Selecciona una opción del menú:*", reply_markup=reply_markup)
        return
    else:
        text = "⚠️ Opción no válida. ¡Por favor, selecciona una opción del menú! 😅"
        keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text=text, reply_markup=reply_markup)

# Manejar la selección de usuario para enviar mensaje
async def send_message_to_user(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'send_to_all':
        send_to_all[query.from_user.id] = True
        awaiting_message_input[query.from_user.id] = True
        text = "✉️ Ingresa el mensaje que deseas enviar a todos los usuarios."
    else:
        target_user_id = int(query.data.split('_')[2])
        selected_target_user[query.from_user.id] = target_user_id
        awaiting_message_input[query.from_user.id] = True
        text = f"📈 Ingresa el mensaje para el usuario con ID {target_user_id}."
    keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text=text, reply_markup=reply_markup)

# Manejar el ingreso del mensaje
async def handle_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in awaiting_message_input and awaiting_message_input[user_id]:
        if user_id in send_to_all and send_to_all[user_id]:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            users = cursor.fetchall()
            conn.close()
            for user in users:
                try:
                    await context.bot.send_message(chat_id=user[0], text=update.message.text)
                except Exception as e:
                    print(f"Error al enviar mensaje al usuario {user[0]}: {e}")
            await update.message.reply_text("✅ *Mensaje enviado a todos los usuarios con éxito* 🎉")
            send_to_all[user_id] = False
        else:
            target_user_id = selected_target_user[user_id]
            try:
                await context.bot.send_message(chat_id=target_user_id, text=update.message.text)
                await update.message.reply_text("✅ *Mensaje enviado con éxito* 🎉")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
        awaiting_message_input[user_id] = False
    else:
        await update.message.reply_text("⚠️ No hay ninguna acción pendiente.")

# Configuración de handlers
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(toma_asistencia|agenda|premium_menu|envio_calificaciones|menu_principal)$"))
    app.add_handler(CallbackQueryHandler(send_message_to_user, pattern=r"^(send_message_\d+|send_to_all)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot en ejecución... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
