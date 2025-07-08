import os
import stripe
import requests
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Diccionario para registrar que el usuario quiere contactar admin
dynamic_state = {}

# Menú principal inline
def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🗑️ Cancelar suscripción", callback_data="cancelar"),
            InlineKeyboardButton("💳 Consultar pagos", callback_data="pagos"),
        ],
        [
            InlineKeyboardButton("📩 Contactar administrador", callback_data="contactar_admin")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Botón para volver
def get_return_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver al menú", callback_data="volver_menu")]
    ])

# Mostrar menú principal
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_menu()
    if update.message:
        await update.message.reply_text("👋 ¿Cómo podemos ayudarte hoy?", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("👋 ¿Cómo podemos ayudarte hoy?", reply_markup=reply_markup)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejo de texto (respuesta al contacto)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    nombre = update.effective_user.full_name or "Sin nombre"
    username = update.effective_user.username or "Sin username"

    if user_id in dynamic_state:
        motivo = dynamic_state.pop(user_id)
        mensaje = (
            f"📬 *Nuevo contacto de usuario*\n"
            f"👤 *Nombre:* {nombre}\n"
            f"🆔 *ID de Telegram:* {user_id}\n"
            f"🔗 *Usuario:* @{username}\n"
            f"📌 *Motivo:* {motivo}\n"
            f"✉️ *Mensaje:* {text}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensaje, parse_mode="Markdown")
        await update.message.reply_text("Gracias, el administrador te responderá pronto.")
    else:
        await mostrar_menu(update, context)

# Manejo de botones
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "cancelar":
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí", callback_data="confirmar_cancelacion"),
                InlineKeyboardButton("❌ No", callback_data="no_cancelar")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⚠️ Al cancelar tu suscripción, perderás el acceso al canal premium al final de tu ciclo actual.\n\n"
            "¿Estás seguro que deseas cancelar tu suscripción?",
            reply_markup=reply_markup
        )

    elif query.data == "confirmar_cancelacion":
        await query.edit_message_text("✅ Se ha registrado tu solicitud de cancelación.", reply_markup=get_return_button())
        try:
            response = requests.post(MAKE_WEBHOOK_URL, json={"telegram_id": user_id})
            if response.status_code == 200:
                print("✅ Enviado a Make correctamente")
            else:
                print("❌ Error al enviar a Make:", response.status_code, response.text)
        except Exception as e:
            print("🚨 Excepción al enviar a Make:", e)

    elif query.data == "no_cancelar":
        await query.edit_message_text("❌ Cancelación anulada. Tu suscripción sigue activa.", reply_markup=get_return_button())

    elif query.data == "pagos":
        await query.edit_message_text("💳 Puedes consultar tus pagos en tu panel personal o contactando a soporte.", reply_markup=get_return_button())

    elif query.data == "contactar_admin":
        dynamic_state[user_id] = "Contacto por suscripción"
        await query.edit_message_text("✍️ Por favor, escribe tu mensaje y un administrador se pondrá en contacto contigo.")

    elif query.data == "volver_menu":
        await mostrar_menu(update, context)

# Ejecutar bot
if __name__ == '__main__':
    print("🚀 Bot de cancelación corriendo...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()