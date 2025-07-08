import os
import stripe
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")  # Aquí enviarás la intención de cancelar

# Función para iniciar el bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text("Hola, ¿cómo podemos ayudarte?", reply_markup=reply_markup)

# Función cuando se presiona una opción del menú
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
            text=f"⚠️ Al cancelar tu suscripción, perderás el acceso al canal premium al final de tu ciclo actual.\n¿Estás seguro que deseas cancelar tu suscripción?",
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
        await query.edit_message_text("📌 Preguntas frecuentes:\n1. ¿Qué incluye mi suscripción?\n2. ¿Cómo contacto soporte?\n3. ¿Puedo cambiar de plan?")

# Configuración del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot de cancelación corriendo...")
    app.run_polling()