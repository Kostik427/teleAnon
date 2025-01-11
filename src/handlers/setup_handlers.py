from telebot import TeleBot
from src.models.states import SetupState, UserState
from src.services.matching_service import MatchingService


def register_setup_handlers(bot: TeleBot, service: MatchingService):
    @bot.message_handler(commands=["start"])
    def start_handler(message):
        user_id = message.from_user.id
        service.start_setup(user_id, message)
