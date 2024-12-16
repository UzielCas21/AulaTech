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

    # Crear el menú con estilos y emojis
    keyboard = [
        [InlineKeyboardButton("📝 ✨ Toma asistencia ✨", callback_data='toma_asistencia')],
        [InlineKeyboardButton("📅 🎯 Agenda 🎯", callback_data='agenda')],
        [InlineKeyboardButton("💎 🚀 Hazte PREMIUM 🚀", callback_data='premium_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ *Selecciona una opción del menú:*", reply_markup=reply_markup)

# Manejar interacciones con botones
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'toma_asistencia':
        text = "📝 **Toma asistencia**: Selecciona una opción."
        keyboard = [
            [InlineKeyboardButton("➕ Crear grupo", callback_data='crear_grupo')],
            [InlineKeyboardButton("📂 Escoger grupo", callback_data='escoger_grupo')],
            [InlineKeyboardButton("🔙 ⬅️ Volver al menú principal ⬅️", callback_data='menu_principal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text=text, reply_markup=reply_markup)
    elif query.data == 'crear_grupo':
        text = "➕ **Crear grupo**: Por favor, ingresa el nombre del nuevo grupo."
        awaiting_message_input[query.from_user.id] = 'crear_grupo'
        await safe_edit_message(query, text=text)
    elif query.data == 'escoger_grupo':
        # Recuperar grupos existentes (esto depende de la lógica de la base de datos de grupos)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT group_name FROM groups')
        groups = cursor.fetchall()
        conn.close()

        if not groups:
            text = "📂 **Escoger grupo**: No hay grupos disponibles."
        else:
            text = "📂 **Escoger grupo**: Selecciona un grupo de la lista."
            keyboard = [[InlineKeyboardButton(group[0], callback_data=f'grupo_{group[0]}')] for group in groups]
            keyboard.append([InlineKeyboardButton("🔙 ⬅️ Volver al menú principal ⬅️", callback_data='menu_principal')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_edit_message(query, text=text, reply_markup=reply_markup)
            return

        await safe_edit_message(query, text=text)
    elif query.data.startswith('grupo_'):
        group_name = query.data.split('_')[1]
        text = f"✅ Has seleccionado el grupo: {group_name}."
        await safe_edit_message(query, text=text)
    elif query.data == 'agenda':
        text = "📅 **Agenda**: Aquí puedes gestionar tus eventos y actividades 📅📋"
        await safe_edit_message(query, text=text)
    elif query.data == 'premium_menu':
        text = "💎 Accede a alguna opción *PREMIUM*:"
        keyboard = [
            [InlineKeyboardButton("🔖 ✏️ Registro de actividades ✏️", callback_data='registro_actividades')],
            [InlineKeyboardButton("📊 📋 Generación de reportes 📋", callback_data='generacion_reportes')],
            [InlineKeyboardButton("📈 📌 Envío de calificaciones 📌", callback_data='envio_calificaciones')],
            [InlineKeyboardButton("🔙 ⬅️ Volver al menú principal ⬅️", callback_data='menu_principal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text=text, reply_markup=reply_markup)
        return
    elif query.data == 'envio_calificaciones':
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, first_name FROM users')
        users = cursor.fetchall()
        conn.close()

        if not users:
            text = "📈 No hay usuarios registrados para enviar calificaciones."
        else:
            text = "📈 Selecciona los usuarios a los que deseas enviar las calificaciones:"
            keyboard = [[InlineKeyboardButton(f"{user[1]} (ID: {user[0]})", callback_data=f'envio_{user[0]}')] for user in users]
            keyboard.append([InlineKeyboardButton("🔙 ⬅️ Volver al menú principal ⬅️", callback_data='menu_principal')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await safe_edit_message(query, text=text, reply_markup=reply_markup)
            return

        await safe_edit_message(query, text=text)
    elif query.data.startswith('envio_'):
        user_id = query.data.split('_')[1]
        selected_target_user[query.from_user.id] = user_id
        awaiting_message_input[query.from_user.id] = 'send_message'
        text = f"✏️ Ingresa el mensaje para enviar al usuario con ID: {user_id}."
        await safe_edit_message(query, text=text)
    elif query.data == 'menu_principal':
        keyboard = [
            [InlineKeyboardButton("📝 ✨ Toma asistencia ✨", callback_data='toma_asistencia')],
            [InlineKeyboardButton("📅 🎯 Agenda 🎯", callback_data='agenda')],
            [InlineKeyboardButton("💎 🚀 Hazte PREMIUM 🚀", callback_data='premium_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text="✨ *Selecciona una opción del menú:*", reply_markup=reply_markup)
    else:
        text = "⚠️ Opción no válida. ¡Por favor, selecciona una opción del menú! 😅"
        keyboard = [[InlineKeyboardButton("🔙 ⬅️ Volver al menú principal ⬅️", callback_data='menu_principal')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text=text, reply_markup=reply_markup)

async def handle_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in awaiting_message_input:
        action = awaiting_message_input[user_id]

        if action == 'crear_grupo':
            group_name = update.message.text
            # Guardar el grupo en la base de datos
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS groups (group_name TEXT)''')
            cursor.execute('INSERT INTO groups (group_name) VALUES (?)', (group_name,))
            conn.commit()
            conn.close()

            await update.message.reply_text(f"✅ Grupo '{group_name}' creado con éxito.")

        elif action == 'send_message':
            target_user_id = selected_target_user.get(user_id)
            if target_user_id:
                message = update.message.text
                await context.bot.send_message(chat_id=target_user_id, text=message)

                # Crear el menú para enviar otro mensaje o regresar a la lista
                keyboard = [
                    [InlineKeyboardButton("✏️ Enviar otro mensaje", callback_data=f'envio_{target_user_id}')],
                    [InlineKeyboardButton("📋 Regresar a la lista de usuarios", callback_data='envio_calificaciones')],
                    [InlineKeyboardButton("🔙 Volver al menú principal", callback_data='menu_principal')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"✅ Mensaje enviado al usuario con ID: {target_user_id}.",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("⚠️ Error: No se pudo encontrar al usuario objetivo.")

        awaiting_message_input[user_id] = None

# Configuración de handlers
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(toma_asistencia|agenda|premium_menu|crear_grupo|escoger_grupo|menu_principal|grupo_.*|envio_.*)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot en ejecución... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
