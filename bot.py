import os
import stripe
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import requests

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

# Función para mostrar el menú principal
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Cancelar suscripción", callback_data="cancelar"),
            InlineKeyboardButton("Consultar pagos", callback_data="pagos"),
        ],
        [
            InlineKeyboardButton("Preguntas frecuentes", callback_data="faq")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Si viene de mensaje normal
    if update.message:
        await update.message.reply_text("Hola, ¿cómo podemos ayudarte?", reply_markup=reply_markup)
    # Si viene de otra fuente como CallbackQuery
    elif update.callback_query:
        await update.callback_query.message.reply_text("Hola, ¿cómo podemos ayudarte?", reply_markup=reply_markup)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejador para cualquier texto (ej: "hola", "ayuda", etc.)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejador de botones
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
            text=(
                "⚠️ Al cancelar tu suscripción, perderás el acceso al canal premium al final de tu ciclo actual.\n\n"
                "¿Estás seguro que deseas cancelar tu suscripción?"
            ),
            reply_markup=reply_markup
        )

    elif query.data == "confirmar_cancelacion":
        await query.edit_message_text("✅ Se ha registrado tu solicitud de cancelación.")
        data = {
            "telegram_id": user_id
        }
        try:
            response = requests.post(MAKE_WEBHOOK_URL, json=data)
            if response.status_code == 200:
                print("Enviado a Make correctamente")
            else:
                print("Error al enviar a Make:", response.status_code, response.text)
        except Exception as e:
            print("Excepción al enviar a Make:", e)

    elif query.data == "no_cancelar":
        await query.edit_message_text("❌ Cancelación anulada. Tu suscripción sigue activa.")

    elif query.data == "pagos":
        await query.edit_message_text("Puedes consultar tus pagos en tu panel personal.")

    elif query.data == "faq":
        await query.edit_message_text(
            "📌 Preguntas frecuentes:\n"
            "1. ¿Qué incluye mi suscripción?\n"
            "2. ¿Cómo contacto soporte?\n"
            "3. ¿Puedo cambiar de plan?"
        )

# Configuración del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))  # Responde a cualquier texto

    print("Bot de cancelación corriendo...")
    app.run_polling()