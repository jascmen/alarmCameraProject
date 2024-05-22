# telegram_bot.py
import telebot
from dotenv import load_dotenv
import os

class TelegramBot:
    def __init__(self, app):
        load_dotenv()
        token = os.getenv("YOUR_BOT_TOKEN")
        self.bot = telebot.TeleBot(token)
        self.app = app

        @self.bot.message_handler(commands=["start", "help"])
        def send_welcome(message):
            self.bot.reply_to(
                message,
                """
            Hola, soy tu primer bot, estos son los comandos disponibles:
            \n /start_system - encender el sistema
            \n /stop_system - apagar el sistema
            """,
            )

        @self.bot.message_handler(commands=["start_system"])
        def start_system(message):
            self.app.open_camera()
            self.bot.reply_to(message, "Sistema encendido")

        @self.bot.message_handler(commands=["stop_system"])
        def stop_system(message):
            self.app.close_camera()
            self.bot.reply_to(message, "Sistema apagado")

    def start_polling(self):
        self.bot.polling()