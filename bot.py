import telebot
from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime
import os


class UserState(Enum):
    WAITING = "waiting"
    CHATTING = "chatting"
    IDLE = "idle"

@dataclass
class MessageInfo:
    message_id: int
    chat_id: int
    partner_message_id: int
    timestamp: datetime

class ChatBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.user_states: Dict[int, UserState] = {}
        self.active_chats: Dict[int, int] = {}
        self.waiting_users: List[int] = []
        self.chats: Dict[int, Dict[int, List[MessageInfo]]] = {}

        self._setup_handlers()

    def _setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            user_id = message.from_user.id
            self.user_states[user_id] = UserState.IDLE
            self.user_messages[user_id] = []
            self.bot.reply_to(message, "Добро пожаловать в анонимный чат! Используйте /search для поиска собеседника.")

        @self.bot.message_handler(commands=['search'])
        def search_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) == UserState.CHATTING:
                self.bot.reply_to(message, "Сначала завершите текущий чат командой /end")
                return

            if user_id in self.waiting_users:
                self.bot.reply_to(message, "Вы уже в поиске собеседника.")
                return

            self.user_states[user_id] = UserState.WAITING
            self.waiting_users.append(user_id)
            self.bot.reply_to(message, "Поиск собеседника...")
            self._try_match_users()

        @self.bot.message_handler(commands=['end'])
        def end_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) != UserState.CHATTING:
                self.bot.reply_to(message, "Вы не находитесь в активном чате.")
                return

            partner_id = self.active_chats.get(user_id)
            self._end_chat(user_id)

            self.bot.send_message(
                user_id,
                "Чат завершен. Хотите начать новый чат? Используйте /search."
            )

        @self.bot.message_handler(content_types=['text', 'photo', 'video', 'audio', 'document'])
        def message_handler(message):
            user_id = message.from_user.id

            if self.user_states.get(user_id) != UserState.CHATTING:
                self.bot.reply_to(message, "Вы не находитесь в активном чате. Используйте /search для поиска собеседника.")
                return

            partner_id = self.active_chats.get(user_id)
            if not partner_id:
                return

            self._handle_message(message, user_id, partner_id)

    def _try_match_users(self):
        if len(self.waiting_users) >= 2:
            user1 = self.waiting_users.pop(0)
            user2 = self.waiting_users.pop(0)

            self.active_chats[user1] = user2
            self.active_chats[user2] = user1

            self.user_states[user1] = UserState.CHATTING
            self.user_states[user2] = UserState.CHATTING

            chat_id = self._generate_chat_id(user1, user2)
            self.chats[chat_id] = {user1: [], user2: []}

            for user_id in (user1, user2):
                self.bot.send_message(
                    user_id,
                    "Собеседник найден! Можете начинать общение. /end для завершения."
                )

    def _generate_chat_id(self, user1: int, user2: int) -> int:
        return user1 * 1000000 + user2 if user1 < user2 else user2 * 1000000 + user1

    def _handle_message(self, message, user_id: int, partner_id: int):
        try:
            if message.content_type == 'text':
                sent_message = self.bot.send_message(partner_id, message.text)
            elif message.content_type == 'photo':
                sent_message = self.bot.send_photo(
                    partner_id,
                    message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.content_type == 'video':
                sent_message = self.bot.send_video(
                    partner_id,
                    message.video.file_id,
                    caption=message.caption
                )
            elif message.content_type == 'audio':
                sent_message = self.bot.send_audio(
                    partner_id,
                    message.audio.file_id,
                    caption=message.caption
                )
            elif message.content_type == 'document':
                sent_message = self.bot.send_document(
                    partner_id,
                    message.document.file_id,
                    caption=message.caption
                )

            message_info = MessageInfo(
                message_id=message.message_id,
                chat_id=message.chat.id,
                partner_message_id=sent_message.message_id,
                timestamp=datetime.now()
            )

            chat_id = self._generate_chat_id(user_id, partner_id)
            self.chats[chat_id][user_id].append(message_info)
            self.chats[chat_id][partner_id].append(MessageInfo(
                message_id=sent_message.message_id,
                chat_id=message.chat.id,
                partner_message_id=message.message_id,
                timestamp=datetime.now()
            ))

        except Exception as e:
            print(f"Error handling message: {e}")
            self.bot.send_message(user_id, "Ошибка при отправке сообщения.")

    def _end_chat(self, user_id: int):
        partner_id = self.active_chats.get(user_id)
        if not partner_id:
            return

        chat_id = self._generate_chat_id(user_id, partner_id)
        if chat_id in self.chats:
            del self.chats[chat_id]

        for uid in (user_id, partner_id):
            self.user_states[uid] = UserState.IDLE
            if uid in self.active_chats:
                del self.active_chats[uid]
            if uid != user_id:
                self.bot.send_message(
                    uid,
                    "Собеседник завершил чат. Используйте /search для поиска нового собеседника."
                )

    def run(self):
        self.bot.polling(none_stop=True)

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    bot = ChatBot(token)
    bot.run()
