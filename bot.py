import telebot
from enum import Enum
from typing import Dict, List
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
        @self.bot.message_handler(commands=["start"])
        def start_handler(message):
            user_id = message.from_user.id
            self.user_states[user_id] = UserState.IDLE
            self.bot.reply_to(
                message,
                "Welcome to the anonymous chat! Use /search to find someone to chat with.",
            )

        @self.bot.message_handler(commands=["search"])
        def search_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) == UserState.CHATTING:
                self.bot.reply_to(
                    message,
                    "Finish your current chat with /end before searching for a new one.",
                )
                return

            if user_id in self.waiting_users:
                self.bot.reply_to(
                    message, "You're already searching for a chat partner."
                )
                return

            self.user_states[user_id] = UserState.WAITING
            self.waiting_users.append(user_id)
            self.bot.reply_to(message, "Looking for a chat partner...")
            self._try_match_users()

        @self.bot.message_handler(commands=["end"])
        def end_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) != UserState.CHATTING:
                self.bot.reply_to(message, "You're not in an active chat right now.")
                return

            self._end_chat(user_id)
            self.bot.send_message(
                user_id, "Chat ended. Want to start another? Use /search."
            )

        @self.bot.message_handler(
            content_types=["text", "photo", "video", "audio", "document"]
        )
        def message_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) != UserState.CHATTING:
                self.bot.reply_to(
                    message,
                    "You're not in an active chat. Use /search to find someone to talk to.",
                )
                return

            partner_id = self.active_chats.get(user_id)
            if not partner_id:
                return

            self._forward_message(message, user_id, partner_id)

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

            for user in (user1, user2):
                self.bot.send_message(
                    user,
                    "Chat partner found! Start chatting now. Use /end to finish the chat.",
                )

    def _generate_chat_id(self, user1: int, user2: int) -> int:
        return user1 * 1_000_000 + user2 if user1 < user2 else user2 * 1_000_000 + user1

    def _forward_message(self, message, sender_id: int, receiver_id: int):
        try:
            sent_message = None
            if message.content_type == "text":
                sent_message = self.bot.send_message(receiver_id, message.text)
            elif message.content_type == "photo":
                sent_message = self.bot.send_photo(
                    receiver_id, message.photo[-1].file_id, caption=message.caption
                )
            elif message.content_type == "video":
                sent_message = self.bot.send_video(
                    receiver_id, message.video.file_id, caption=message.caption
                )
            elif message.content_type == "audio":
                sent_message = self.bot.send_audio(
                    receiver_id, message.audio.file_id, caption=message.caption
                )
            elif message.content_type == "document":
                sent_message = self.bot.send_document(
                    receiver_id, message.document.file_id, caption=message.caption
                )

            if sent_message:
                chat_id = self._generate_chat_id(sender_id, receiver_id)
                self.chats[chat_id][sender_id].append(
                    MessageInfo(
                        message_id=message.message_id,
                        chat_id=message.chat.id,
                        partner_message_id=sent_message.message_id,
                        timestamp=datetime.now(),
                    )
                )

        except Exception as e:
            print(f"Error while forwarding message: {e}")
            self.bot.send_message(
                sender_id, "Oops! Something went wrong with sending your message."
            )

    def _end_chat(self, user_id: int):
        partner_id = self.active_chats.pop(user_id, None)
        if not partner_id:
            return

        chat_id = self._generate_chat_id(user_id, partner_id)
        self.chats.pop(chat_id, None)

        for uid in (user_id, partner_id):
            self.user_states[uid] = UserState.IDLE
            self.active_chats.pop(uid, None)
            if uid != user_id:
                self.bot.send_message(
                    uid,
                    "Your chat partner has ended the conversation. Use /search to find another.",
                )

    def run(self):
        print("Bot is up and running!")
        self.bot.polling(none_stop=True)


if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN is not set.")
    else:
        bot = ChatBot(token)
        bot.run()
