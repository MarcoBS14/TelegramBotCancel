import os
import stripe
import requests
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

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
MAKE_API_KEY = os.getenv("MAKE_API_KEY")  # Asegúrate de tener esta variable en tu .env

# Función para mostrar el menú principal
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("❌ Cancelar suscripción", callback_data="cancelar"),
            InlineKeyboardButton("💳 Consultar pagos", callback_data="pagos"),
        ],
        [
            InlineKeyboardButton("📞 Contactar administrador", callback_data="contacto")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Hola, ¿cómo podemos ayudarte?", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Hola, ¿cómo podemos ayudarte?", reply_markup=reply_markup)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejador para cualquier texto
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejador de botones
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "Sin nombre"
    username = query.from_user.username or "Sin username"

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
            "telegram_id": user_id,
            "nombre": first_name,
            "username": username
        }
        headers = {
            "x-make-apikey": MAKE_API_KEY
        }
        try:
            response = requests.post(MAKE_WEBHOOK_URL, json=data, headers=headers)
            if response.status_code == 200:
                print("✅ Enviado a Make correctamente")
            else:
                print(f"❌ Error al enviar a Make: {response.status_code} - {response.text}")
        except Exception as e:
            print("❌ Excepción al enviar a Make:", e)

    elif query.data == "no_cancelar":
        await query.edit_message_text("❌ Cancelación anulada. Tu suscripción sigue activa.")

    elif query.data == "pagos":
        await query.edit_message_text("💰 Puedes consultar tus pagos en tu panel personal o escribiendo 'pagos'.")

    elif query.data == "contacto":
        await query.edit_message_text(
            "📞 Puedes contactar al administrador respondiendo este mensaje. "
            "Un miembro del equipo te responderá pronto."
        )

# Configuración del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot de cancelación corriendo...")
    app.run_polling()