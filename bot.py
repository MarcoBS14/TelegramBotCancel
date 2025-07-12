import os
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
MAKE_API_KEY = os.getenv("MAKE_API_KEY")

# Menú principal (VERTICAL)
def generar_menu():
    keyboard = [
        [InlineKeyboardButton("❌ Cancelar suscripción", callback_data="cancelar")],
        [InlineKeyboardButton("💳 Consultar pagos", callback_data="pagos")],
        [InlineKeyboardButton("💬 Contactar soporte", url="https://t.me/MarcoBS14")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Mostrar menú
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=generar_menu())
    elif update.callback_query:
        await update.callback_query.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=generar_menu())

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejador de mensajes de texto
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update, context)

# Manejo de botones
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    first_name = query.from_user.first_name or "Sin nombre"
    username = query.from_user.username or "Sin username"

    if query.data == "cancelar":
        instrucciones = (
            "<b>Cómo cancelar tu suscripción</b>\n\n"
            "🔗 Haz clic en este enlace para acceder al portal de suscripciones:\n"
            "https://billing.stripe.com/p/login/fZufZib801o65dh61P4F200\n\n"
            "📧 Inicia sesión con el correo electrónico que usaste al suscribirte.\n\n"
            "⚙️ Una vez dentro, ve a la sección “Suscripciones” y selecciona “Cancelar suscripción”.\n\n"
            "⚠️ <b>IMPORTANTE</b>\n"
            "Al confirmar la cancelación, perderás inmediatamente el acceso al grupo.\n\n"
            "Según nuestros Términos y Condiciones, no realizamos reembolsos totales ni parciales, "
            "incluso si no ha finalizado el mes en curso."
        )
        await query.edit_message_text(instrucciones, parse_mode="HTML")

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
                print("✅ Cancelación registrada en Make.")
            else:
                print(f"❌ Error al enviar a Make: {response.status_code} - {response.text}")
        except Exception as e:
            print("❌ Excepción al enviar a Make:", e)

    elif query.data == "pagos":
        await query.edit_message_text(
            "💰 Puedes consultar tus pagos iniciando sesión en el portal de Stripe:\n"
            "https://billing.stripe.com/p/login/fZufZib801o65dh61P4F200"
        )

# Configuración del bot
if __name__ == '__main__':
    print("🤖 Bot de cancelación corriendo...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()