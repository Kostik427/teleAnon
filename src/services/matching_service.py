from typing import Dict, List
from telebot import TeleBot
from src.models.user import UserSettings
from src.models.states import UserState
from src.utils.helpers import hash_id
import random


class MatchingService:
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.user_states: Dict[int, UserState] = {}
        self.user_settings: Dict[str, UserSettings] = {}
        self.active_chats: Dict[int, int] = {}
        self.waiting_users: List[int] = []
        self.rooms = ["general", "movies", "books", "gaming", "music"]

    def start_setup(self, user_id: int, message):
        hashed_id = hash_id(user_id)

        if hashed_id not in self.user_settings:
            self.user_states[user_id] = UserState.SETUP
            self.user_settings[hashed_id] = UserSettings()
            self.bot.reply_to(
                message, "Welcome! Please enter your age (18-99):"
            )
        else:
            self.bot.reply_to(
                message,
                "Welcome back! Use /search to find someone to chat with.\n"
                "Update your settings with /age, /gender, or /room."
            )

    def start_search(self, user_id: int, message):
        hashed_id = hash_id(user_id)

        if hashed_id not in self.user_settings:
            self.bot.reply_to(message, "Please complete your setup using /start first.")
            return

        if user_id in self.waiting_users:
            self.bot.reply_to(message, "You are already in the search queue.")
            return

        self.user_states[user_id] = UserState.WAITING
        self.waiting_users.append(user_id)
        self.bot.reply_to(message, "Looking for a chat partner...")

        self._try_match_users()

    def _try_match_users(self):
        if len(self.waiting_users) < 2:
            return

        user1 = self.waiting_users.pop(0)
        for i, user2 in enumerate(self.waiting_users):
            if self._is_good_match(user1, user2):
                self.waiting_users.pop(i)

                self.active_chats[user1] = user2
                self.active_chats[user2] = user1

                self.user_states[user1] = UserState.CHATTING
                self.user_states[user2] = UserState.CHATTING

                self.bot.send_message(user1, "Chat partner found! Start chatting.")
                self.bot.send_message(user2, "Chat partner found! Start chatting.")
                break

    def _is_good_match(self, user1: int, user2: int) -> bool:
        user1_hash = hash_id(user1)
        user2_hash = hash_id(user2)

        settings1 = self.user_settings[user1_hash]
        settings2 = self.user_settings[user2_hash]

        if settings1.room != settings2.room:
            return False
        return abs(settings1.age - settings2.age) <= 10

    def end_chat(self, user_id: int, message):
        partner_id = self.active_chats.pop(user_id, None)
        if not partner_id:
            self.bot.reply_to(message, "You are not in an active chat.")
            return

        self.active_chats.pop(partner_id, None)
        self.user_states[user_id] = UserState.IDLE
        self.user_states[partner_id] = UserState.IDLE

        self.bot.send_message(partner_id, "Your chat partner has ended the conversation.")
        self.bot.reply_to(message, "Chat ended.")
