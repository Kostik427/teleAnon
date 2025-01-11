import telebot
from typing import Dict
import json
from pathlib import Path
from .handlers.setup_handlers import SetupHandlers
from .handlers.chat_handlers import ChatHandlers
from .handlers.message_handlers import MessageHandlers
from .services.matching_service import MatchingService
from .services.message_service import MessageService
from .services.user_service import UserService
from .models.states import UserState, SetupState
from .utils.helpers import hash_user_id

class ChatBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        
        self.user_service = UserService("user_settings.json")
        self.matching_service = MatchingService()
        self.message_service = MessageService()
        
        self.setup_handlers = SetupHandlers(self.bot, self.user_service)
        self.chat_handlers = ChatHandlers(
            self.bot, 
            self.user_service, 
            self.matching_service
        )
        self.message_handlers = MessageHandlers(
            self.bot,
            self.user_service,
            self.matching_service,
            self.message_service
        )
        
        self._setup_handlers()

    def _setup_handlers(self):
        self.setup_handlers.register_handlers()
        self.chat_handlers.register_handlers()
        self.message_handlers.register_handlers()

    def run(self):
        print("Bot is up and running!")
        self.bot.polling(none_stop=True)