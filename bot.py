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
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "MarcoBS14")  # Username por defecto si no está definido

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

    mensaje = "👋 ¿Cómo puedo ayudarte hoy?"

    if update.message:
        await update.message.reply_text(mensaje, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(mensaje, reply_markup=reply_markup)

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

    if query.data == "cancelar":
        texto = (
            "<b>🧾 Cómo cancelar tu suscripción</b>\n\n"
            "🔗 Haz clic en este enlace para acceder al portal de suscripciones:\n"
            "<a href='https://billing.stripe.com/p/login/fZufZib801o65dh61P4F200'>Abrir portal de Stripe</a>\n\n"
            "📧 Inicia sesión con el correo electrónico que usaste al suscribirte.\n"
            "⚙️ Una vez dentro, ve a la sección “Suscripciones” y selecciona “Cancelar suscripción”.\n\n"
            "⚠️ <b>IMPORTANTE</b>\n"
            "Al confirmar la cancelación, perderás <b>inmediatamente</b> el acceso al grupo.\n"
            "No realizamos reembolsos totales ni parciales, incluso si no ha finalizado el mes en curso."
        )
        await query.edit_message_text(text=texto, parse_mode="HTML")

    elif query.data == "pagos":
        await query.edit_message_text("💰 Puedes consultar tus pagos en tu panel personal o escribiéndonos por soporte.")

    elif query.data == "contacto":
        texto = (
            "📞 Puedes contactar directamente al administrador dando clic aquí:\n\n"
            f"<a href='https://t.me/{ADMIN_USERNAME}'>@{ADMIN_USERNAME}</a>"
        )
        await query.edit_message_text(text=texto, parse_mode="HTML")

# Configuración del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot de cancelación corriendo...")
    app.run_polling()