"""
OpositApp Telegram Bot
Bot para estudiar flashcards con repetición espaciada vía Telegram
Con soporte de autenticación JWT multi-usuario
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
API_URL = os.getenv("API_URL", "http://localhost:7999/api")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Almacenamiento temporal de flashcards y tokens JWT (por usuario de Telegram)
user_sessions = {}  # flashcards en sesión
user_tokens = {}    # tokens JWT por telegram_user_id


def get_auth_headers(telegram_user_id):
    """Obtener headers de autenticación para un usuario"""
    token = user_tokens.get(telegram_user_id)
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}


def is_authenticated(telegram_user_id):
    """Verificar si el usuario está autenticado"""
    return telegram_user_id in user_tokens


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida"""
    user = update.effective_user
    telegram_id = user.id

    if is_authenticated(telegram_id):
        welcome_message = f"""
🧠 <b>¡Bienvenido de nuevo, {user.first_name}!</b>

Ya estás autenticado y listo para estudiar.

<b>Comandos disponibles:</b>
/study - Estudiar flashcards
/stats - Ver estadísticas de estudio
/logout - Cerrar sesión
/help - Ver ayuda completa

<b>¿Listo para continuar?</b>
Usa /study para comenzar tu sesión de estudio 📚
"""
    else:
        welcome_message = f"""
🧠 <b>¡Bienvenido a OpositApp, {user.first_name}!</b>

Sistema inteligente de flashcards con repetición espaciada para oposiciones.

<b>⚠️ Primero necesitas autenticarte:</b>
<code>/login username password</code>

<b>Comandos disponibles:</b>
/login - Iniciar sesión con tu cuenta
/help - Ver ayuda completa

<b>¿No tienes cuenta?</b>
Regístrate en http://localhost:2998/register
"""
    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ayuda completa"""
    help_text = """
📖 <b>AYUDA - OpositApp Bot</b>

<b>Comandos de Autenticación:</b>
/login username password - Vincular tu cuenta de OpositApp
/logout - Cerrar sesión

<b>Comandos de Estudio:</b>
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

<b>Multi-usuario:</b>
Cada usuario tiene sus propios mazos y progreso independiente. Puedes explorar y clonar mazos públicos de otros usuarios.

<b>Soporte:</b>
¿Problemas? Contacta al administrador.
"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /login username password - Autenticación"""
    telegram_id = update.effective_user.id

    # Verificar si ya está autenticado
    if is_authenticated(telegram_id):
        await update.message.reply_text(
            "✅ Ya estás autenticado.\n"
            "Usa /logout si quieres cambiar de cuenta."
        )
        return

    # Verificar argumentos
    if len(context.args) != 2:
        await update.message.reply_text(
            "🔐 <b>Autenticación OpositApp</b>\n\n"
            "<b>Uso:</b> /login username password\n\n"
            "<b>Ejemplo:</b> <code>/login alejandro oposit2026</code>\n\n"
            "<i>⚠️ Borra tu mensaje después de enviarlo por seguridad</i>\n\n"
            "<b>¿No tienes cuenta?</b>\n"
            "Regístrate en http://localhost:2998/register",
            parse_mode='HTML'
        )
        return

    username = context.args[0]
    password = context.args[1]

    # Borrar mensaje con credenciales
    try:
        await update.message.delete()
    except:
        pass

    try:
        # Autenticar con el backend
        logger.info(f"Intentando login para usuario: {username}")
        response = requests.post(
            f"{API_URL}/auth/token",
            data={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')

            # Guardar token
            user_tokens[telegram_id] = token
            logger.info(f"Login exitoso para usuario: {username} (telegram_id: {telegram_id})")

            # Obtener info del usuario
            user_response = requests.get(
                f"{API_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            if user_response.status_code == 200:
                user_info = user_response.json()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"✅ <b>Autenticación exitosa</b>\n\n"
                         f"👤 Usuario: {user_info['username']}\n"
                         f"📧 Email: {user_info['email']}\n\n"
                         f"Ya puedes usar /study para comenzar a estudiar.",
                    parse_mode='HTML'
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="✅ Autenticación exitosa.\n\nUsa /study para comenzar."
                )
        else:
            logger.warning(f"Login fallido para usuario: {username}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ <b>Error de autenticación</b>\n\n"
                     "Usuario o contraseña incorrectos.\n"
                     "Intenta de nuevo con /login username password",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error en login: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error de conexión con el servidor.\n"
                 "Verifica que el backend esté corriendo."
        )


async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /logout - Cerrar sesión"""
    telegram_id = update.effective_user.id

    if telegram_id in user_tokens:
        del user_tokens[telegram_id]
        await update.message.reply_text(
            "👋 Sesión cerrada correctamente.\n"
            "Usa /login para autenticarte de nuevo."
        )
    else:
        await update.message.reply_text(
            "⚠️ No hay ninguna sesión activa."
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Mostrar estadísticas"""
    telegram_id = update.effective_user.id

    if not is_authenticated(telegram_id):
        await update.message.reply_text(
            "🔐 Necesitas autenticarte primero.\n"
            "Usa /login para vincular tu cuenta."
        )
        return

    try:
        headers = get_auth_headers(telegram_id)
        response = requests.get(f"{API_URL}/study/stats", headers=headers)

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
        elif response.status_code == 401:
            del user_tokens[telegram_id]
            await update.message.reply_text(
                "🔐 Tu sesión ha expirado.\n"
                "Usa /login para autenticarte de nuevo."
            )
        else:
            await update.message.reply_text(
                "❌ Error al obtener estadísticas."
            )
    except Exception as e:
        logger.error(f"Error en stats: {e}")
        await update.message.reply_text(
            "❌ No se pudo conectar con el servidor."
        )


async def study_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /study - Obtener siguiente flashcard"""
    telegram_id = update.effective_user.id

    if not is_authenticated(telegram_id):
        await update.message.reply_text(
            "🔐 Necesitas autenticarte primero.\n"
            "Usa /login para vincular tu cuenta."
        )
        return

    try:
        headers = get_auth_headers(telegram_id)
        response = requests.get(f"{API_URL}/study/next", headers=headers)

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
            user_sessions[telegram_id] = {
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
        elif response.status_code == 401:
            del user_tokens[telegram_id]
            await update.message.reply_text(
                "🔐 Tu sesión ha expirado.\n"
                "Usa /login para autenticarte de nuevo."
            )
        else:
            await update.message.reply_text(
                "❌ Error al obtener flashcard."
            )
    except Exception as e:
        logger.error(f"Error en study: {e}")
        await update.message.reply_text(
            "❌ No se pudo conectar con el servidor.\n"
            f"Asegúrate de que el backend esté corriendo en {API_URL}"
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar callbacks de botones inline"""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    action = query.data

    # Verificar autenticación
    if not is_authenticated(telegram_id):
        await query.edit_message_text(
            "🔐 Tu sesión ha expirado.\n"
            "Usa /login para autenticarte de nuevo."
        )
        return

    # Verificar si el usuario tiene una sesión activa
    if telegram_id not in user_sessions:
        await query.edit_message_text("⚠️ Sesión expirada. Usa /study para obtener una nueva tarjeta.")
        return

    session = user_sessions[telegram_id]
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
            headers = get_auth_headers(telegram_id)
            response = requests.post(
                f"{API_URL}/study/review",
                json=review_data,
                headers=headers
            )

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
                del user_sessions[telegram_id]
            elif response.status_code == 401:
                del user_tokens[telegram_id]
                await query.edit_message_text(
                    "🔐 Tu sesión ha expirado.\n"
                    "Usa /login para autenticarte de nuevo."
                )
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

    logger.info("🤖 Iniciando OpositApp Bot con autenticación JWT...")

    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("login", login_command))
    application.add_handler(CommandHandler("logout", logout_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("study", study_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Iniciar bot
    logger.info("✅ Bot iniciado correctamente")
    logger.info(f"📡 Conectado a API: {API_URL}")
    logger.info("🔐 Sistema de autenticación JWT activo")
    logger.info("⏳ Esperando mensajes...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
