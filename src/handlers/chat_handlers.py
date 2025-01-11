from telebot import TeleBot
from src.services.matching_service import MatchingService


def register_chat_handlers(bot: TeleBot, service: MatchingService):
    @bot.message_handler(commands=["search"])
    def search_handler(message):
        user_id = message.from_user.id
        service.start_search(user_id, message)

    @bot.message_handler(commands=["end"])
    def end_handler(message):
        user_id = message.from_user.id
        service.end_chat(user_id, message)
