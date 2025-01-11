from telebot import TeleBot
from src.services.message_service import MessageService


def register_message_handlers(bot: TeleBot, service: MessageService):
    @bot.message_handler(content_types=["text", "photo", "video", "voice"])
    def message_handler(message):
        user_id = message.from_user.id
        service.forward_message(user_id, message)
