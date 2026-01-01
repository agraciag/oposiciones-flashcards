"""
OpositApp Telegram Bot
Bot para estudiar flashcards con repetición espaciada vía Telegram
"""

import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Cargar variables de entorno
load_dotenv()

# Configuración
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Almacenamiento temporal de flashcards en sesión (por usuario)
user_sessions = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida"""
    user = update.effective_user
    welcome_message = f"""
🧠 <b>¡Bienvenido a OpositApp, {user.first_name}!</b>

Sistema inteligente de flashcards con repetición espaciada para oposiciones.

<b>Comandos disponibles:</b>
/study - Estudiar flashcards
/stats - Ver estadísticas de estudio
/help - Ver ayuda completa

<b>¿Listo para empezar?</b>
Usa /study para comenzar tu sesión de estudio 📚
"""
    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ayuda completa"""
    help_text = """
📖 <b>AYUDA - OpositApp Bot</b>

<b>Comandos Principales:</b>
/start - Iniciar bot
/study - Comenzar sesión de estudio
/stats - Ver tus estadísticas
/help - Mostrar esta ayuda

<b>¿Cómo funciona el estudio?</b>
1. Usa /study para obtener una flashcard
2. Lee la pregunta
3. Piensa en la respuesta
4. Presiona "Ver Respuesta"
5. Evalúa qué tan bien lo recordaste:
   • ❌ Otra vez - No la recordaste
   • 😰 Difícil - Te costó recordarla
   • ✅ Bien - La recordaste bien
   • 😊 Fácil - La recordaste perfectamente

<b>Sistema SM-2:</b>
El algoritmo ajusta automáticamente cuándo volver a mostrarte cada tarjeta según qué tan bien la recuerdes.

<b>Soporte:</b>
¿Problemas? Contacta al administrador.
"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Mostrar estadísticas"""
    try:
        response = requests.get(f"{API_URL}/study/stats")
        if response.status_code == 200:
            stats = response.json()

            stats_message = f"""
📊 <b>TUS ESTADÍSTICAS</b>

📚 Total tarjetas: <b>{stats['total_cards']}</b>
⏰ Pendientes hoy: <b>{stats['cards_to_review']}</b>
📖 Aprendiendo: <b>{stats['cards_learning']}</b>
✅ Dominadas: <b>{stats['cards_mastered']}</b>

<i>Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>
"""
            await update.message.reply_text(stats_message, parse_mode='HTML')
        else:
            await update.message.reply_text(
                "❌ Error al obtener estadísticas. Verifica que el backend esté funcionando."
            )
    except Exception as e:
        logger.error(f"Error en stats: {e}")
        await update.message.reply_text(
            "❌ No se pudo conectar con el servidor. ¿Está el backend corriendo?"
        )


async def study_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /study - Obtener siguiente flashcard"""
    user_id = update.effective_user.id

    try:
        # Obtener siguiente flashcard del backend
        response = requests.get(f"{API_URL}/study/next")

        if response.status_code == 200:
            flashcard = response.json()

            if flashcard is None:
                await update.message.reply_text(
                    "🎉 ¡Excelente trabajo!\n\n"
                    "No hay tarjetas pendientes de revisión en este momento.\n"
                    "Vuelve más tarde para continuar estudiando.\n\n"
                    "Usa /stats para ver tu progreso."
                )
                return

            # Guardar flashcard en sesión del usuario
            user_sessions[user_id] = {
                'flashcard': flashcard,
                'show_answer': False,
                'start_time': datetime.now()
            }

            # Construir mensaje
            metadata = ""
            if flashcard.get('law_name'):
                metadata = f"📜 {flashcard.get('article_number', '')} - {flashcard['law_name']}\n\n"

            message = f"{metadata}<b>❓ PREGUNTA:</b>\n{flashcard['front']}\n\n"
            message += f"<i>Repeticiones: {flashcard['repetitions']} | Intervalo: {flashcard['interval_days']} días</i>"

            # Botón para mostrar respuesta
            keyboard = [[InlineKeyboardButton("👁️ Ver Respuesta", callback_data="show_answer")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "❌ Error al obtener flashcard. Verifica que el backend esté funcionando."
            )
    except Exception as e:
        logger.error(f"Error en study: {e}")
        await update.message.reply_text(
            "❌ No se pudo conectar con el servidor.\n"
            "Asegúrate de que el backend esté corriendo en http://localhost:8000"
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar callbacks de botones inline"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    action = query.data

    # Verificar si el usuario tiene una sesión activa
    if user_id not in user_sessions:
        await query.edit_message_text("⚠️ Sesión expirada. Usa /study para obtener una nueva tarjeta.")
        return

    session = user_sessions[user_id]
    flashcard = session['flashcard']

    if action == "show_answer":
        # Mostrar respuesta y botones de evaluación
        metadata = ""
        if flashcard.get('law_name'):
            metadata = f"📜 {flashcard.get('article_number', '')} - {flashcard['law_name']}\n\n"

        message = f"{metadata}<b>❓ PREGUNTA:</b>\n{flashcard['front']}\n\n"
        message += f"<b>💡 RESPUESTA:</b>\n{flashcard['back']}\n\n"
        message += "<b>¿Qué tal lo recordaste?</b>"

        # Botones de evaluación
        keyboard = [
            [
                InlineKeyboardButton("❌ Otra vez", callback_data="quality_again"),
                InlineKeyboardButton("😰 Difícil", callback_data="quality_hard"),
            ],
            [
                InlineKeyboardButton("✅ Bien", callback_data="quality_good"),
                InlineKeyboardButton("😊 Fácil", callback_data="quality_easy"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    elif action.startswith("quality_"):
        # Procesar evaluación
        quality = action.replace("quality_", "")

        # Calcular tiempo de estudio
        time_spent = int((datetime.now() - session['start_time']).total_seconds())

        # Enviar review al backend
        review_data = {
            "flashcard_id": flashcard['id'],
            "quality": quality,
            "time_spent_seconds": time_spent
        }

        try:
            response = requests.post(f"{API_URL}/study/review", json=review_data)

            if response.status_code == 200:
                result = response.json()

                # Emojis según calidad
                quality_emoji = {
                    "again": "❌",
                    "hard": "😰",
                    "good": "✅",
                    "easy": "😊"
                }

                quality_text = {
                    "again": "Otra vez",
                    "hard": "Difícil",
                    "good": "Bien",
                    "easy": "Fácil"
                }

                success_message = f"{quality_emoji[quality]} <b>Evaluación: {quality_text[quality]}</b>\n\n"
                success_message += f"📅 Próxima revisión: en {result['interval_days']} día(s)\n"
                success_message += f"🔄 Repeticiones: {result['repetitions']}\n"
                success_message += f"📈 Factor facilidad: {result['easiness_factor']}\n\n"
                success_message += "Usa /study para continuar estudiando."

                await query.edit_message_text(success_message, parse_mode='HTML')

                # Limpiar sesión
                del user_sessions[user_id]
            else:
                await query.edit_message_text(
                    "❌ Error al procesar la evaluación. Intenta de nuevo con /study"
                )
        except Exception as e:
            logger.error(f"Error al procesar evaluación: {e}")
            await query.edit_message_text(
                "❌ Error de conexión con el servidor."
            )


def main():
    """Iniciar el bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        return

    logger.info("🤖 Iniciando OpositApp Bot...")

    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("study", study_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Iniciar bot
    logger.info("✅ Bot iniciado correctamente")
    logger.info(f"📡 Conectado a API: {API_URL}")
    logger.info("⏳ Esperando mensajes...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
