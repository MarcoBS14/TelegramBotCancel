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

# Menú principal en formato inline
def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🗑️ Cancelar suscripción", callback_data="cancelar"),
            InlineKeyboardButton("💳 Consultar pagos", callback_data="pagos"),
        ],
        [
            InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Botón de regreso al menú
def get_return_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver al menú", callback_data="volver_menu")]
    ])

# Mostrar el menú principal
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_menu()
    if update.message:
        await update.message.reply_text("👋 ¿Cómo podemos ayudarte hoy?", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("👋 ¿Cómo podemos ayudarte hoy?", reply_markup=reply_markup)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejo de texto general (para que el menú siempre reaparezca)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    elif query.data == "faq":
        await query.edit_message_text(
            "❓ *Preguntas frecuentes:*\n"
            "1️⃣ ¿Qué incluye mi suscripción?\n"
            "2️⃣ ¿Cómo contacto soporte?\n"
            "3️⃣ ¿Puedo cambiar de plan?",
            parse_mode="Markdown",
            reply_markup=get_return_button()
        )

    elif query.data == "volver_menu":
        await mostrar_menu(update, context)

# Configuración del bot
if __name__ == '__main__':
    print("🚀 Bot de cancelación corriendo...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()