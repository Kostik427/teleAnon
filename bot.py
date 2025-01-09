import telebot
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import json
import hashlib
import random
from pathlib import Path


class UserState(Enum):
    SETUP = "setup" 
    WAITING = "waiting"
    CHATTING = "chatting"
    IDLE = "idle"


class SetupState(Enum):
    AGE = "age"
    GENDER = "gender"
    ROOM = "room"
    COMPLETE = "complete"


@dataclass
class UserSettings:
    age: int = 0
    gender: str = ""
    room: str = "general"
    setup_state: SetupState = SetupState.AGE

    def to_dict(self):
        return {
            "age": self.age,
            "gender": self.gender,
            "room": self.room,
        }


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
        self.user_settings: Dict[str, UserSettings] = {}
        self.setup_states: Dict[int, SetupState] = {}
        self.active_chats: Dict[int, int] = {}
        self.waiting_users: List[int] = []
        self.chats: Dict[int, Dict[int, List[MessageInfo]]] = {}

        self.ROOMS = [
            "general",
            "movies",
            "books",
            "gaming",
            "music",
            "photography",
            "cooking",
            "politics",
        ]
        self.SETTINGS_FILE = "user_settings.json"

        self._load_settings()
        self._setup_handlers()

    def _hash_id(self, user_id: int) -> str:
        return hashlib.sha256(str(user_id).encode()).hexdigest()

    def _load_settings(self):
        if Path(self.SETTINGS_FILE).exists():
            with open(self.SETTINGS_FILE, "r") as f:
                data = json.load(f)
                for hashed_id, settings in data.items():
                    self.user_settings[hashed_id] = UserSettings(**settings)

    def _save_settings(self):
        data = {
            hashed_id: settings.to_dict()
            for hashed_id, settings in self.user_settings.items()
        }
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def _setup_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start_handler(message):
            user_id = message.from_user.id
            hashed_id = self._hash_id(user_id)

            if hashed_id not in self.user_settings:
                self.user_states[user_id] = UserState.SETUP
                self.setup_states[user_id] = SetupState.AGE
                self.user_settings[hashed_id] = UserSettings()
                self.bot.reply_to(
                    message,
                    "Welcome! Let's set up your profile.\nPlease enter your age (18-99):",
                )
            else:
                self.user_states[user_id] = UserState.IDLE
                self.bot.reply_to(
                    message,
                    "Welcome back! Use /search to find someone to chat with.\n"
                    "You can update your settings with:\n"
                    "/age - Update your age\n"
                    "/gender - Update your gender\n"
                    "/room - Change chat room",
                )

        @self.bot.message_handler(commands=["age"])
        def age_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) == UserState.CHATTING:
                self.bot.reply_to(message, "Please finish your current chat first.")
                return
            self.setup_states[user_id] = SetupState.AGE
            self.bot.reply_to(message, "Please enter your age (18-99):")

        @self.bot.message_handler(commands=["gender"])
        def gender_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) == UserState.CHATTING:
                self.bot.reply_to(message, "Please finish your current chat first.")
                return
            self.setup_states[user_id] = SetupState.GENDER
            self.bot.reply_to(message, "Please enter your gender (M/W):")

        @self.bot.message_handler(commands=["room"])
        def room_handler(message):
            user_id = message.from_user.id
            if self.user_states.get(user_id) == UserState.CHATTING:
                self.bot.reply_to(message, "Please finish your current chat first.")
                return
            self.setup_states[user_id] = SetupState.ROOM
            rooms_str = ", ".join(self.ROOMS)
            self.bot.reply_to(message, f"Please choose a room:\n{rooms_str}")

        @self.bot.message_handler(
            func=lambda message: self.user_states.get(message.from_user.id)
            == UserState.SETUP
            or self.setup_states.get(message.from_user.id)
            in [SetupState.AGE, SetupState.GENDER, SetupState.ROOM]
        )
        def handle_setup(message):
            user_id = message.from_user.id
            hashed_id = self._hash_id(user_id)
            setup_state = self.setup_states.get(user_id)
    
            if setup_state == SetupState.AGE:
                try:
                    age = int(message.text)
                    if 18 <= age <= 99:
                        self.user_settings[hashed_id].age = age
                        self.setup_states[user_id] = SetupState.GENDER
                        self.bot.reply_to(message, "Please enter your gender (M/W):")
                    else:
                        self.bot.reply_to(
                            message, "Please enter a valid age between 18 and 99:"
                        )
                except ValueError:
                    self.bot.reply_to(
                        message, "Please enter a valid number between 18 and 99:"
                    )

            elif setup_state == SetupState.GENDER:
                gender = message.text.upper()
                if gender in ["M", "W"]:
                    self.user_settings[hashed_id].gender = gender
                    self.setup_states[user_id] = SetupState.ROOM
                    rooms_str = ", ".join(self.ROOMS)
                    self.bot.reply_to(message, f"Please choose a room:\n{rooms_str}")
                else:
                    self.bot.reply_to(message, "Please enter either M or W:")

            elif setup_state == SetupState.ROOM:
                room = message.text.lower()
                if room in self.ROOMS:
                    self.user_settings[hashed_id].room = room
                    self.setup_states[user_id] = SetupState.COMPLETE
                    self.user_states[user_id] = UserState.IDLE
                    self._save_settings()
                    self.bot.reply_to(
                        message,
                        "Setup complete! Use /search to find someone to chat with.\n"
                        "You can update your settings anytime with:\n"
                        "/age - Update your age\n"
                        "/gender - Update your gender\n"
                        "/room - Change chat room",
                    )
                else:
                    rooms_str = ", ".join(self.ROOMS)
                    self.bot.reply_to(
                        message, f"Please choose a valid room:\n{rooms_str}"
                    )

        @self.bot.message_handler(commands=["search"])
        def search_handler(message):
            user_id = message.from_user.id
            hashed_id = self._hash_id(user_id)

            if hashed_id not in self.user_settings:
                self.bot.reply_to(
                    message, "Please use /start to set up your profile first."
                )
                return

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
            content_types=[
                "text",
                "audio",
                "document",
                "photo",
                "sticker",
                "video",
                "video_note",
                "voice",
                "location",
                "contact",
                "venue",
                "dice",
                "poll",
                "animation",
            ]
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

    def _is_good_match(self, user1_id: int, user2_id: int) -> bool:
        user1_hash = self._hash_id(user1_id)
        user2_hash = self._hash_id(user2_id)

        user1_settings = self.user_settings[user1_hash]
        user2_settings = self.user_settings[user2_hash]

        if user1_settings.room != user2_settings.room:
            return False

        age_diff = abs(user1_settings.age - user2_settings.age)
        if age_diff > 10:
            return False

        if user1_settings.gender == user2_settings.gender:
            return random.random() < 0.3

        return True

    def _try_match_users(self):
        if len(self.waiting_users) >= 2:
            user1 = self.waiting_users[0]
            best_match = None

            for i, user2 in enumerate(self.waiting_users[1:], 1):
                if self._is_good_match(user1, user2):
                    best_match = i
                    break

            if best_match is not None:
                user1 = self.waiting_users.pop(0)
                user2 = self.waiting_users.pop(
                    best_match - 1
                )  # -1 because we removed user1

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
                    receiver_id,
                    message.photo[-1].file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                )

            elif message.content_type == "video":
                sent_message = self.bot.send_video(
                    receiver_id,
                    message.video.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    duration=message.video.duration,
                    width=message.video.width,
                    height=message.video.height,
                )

            elif message.content_type == "audio":
                sent_message = self.bot.send_audio(
                    receiver_id,
                    message.audio.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    duration=message.audio.duration,
                    performer=message.audio.performer,
                    title=message.audio.title,
                )

            elif message.content_type == "document":
                sent_message = self.bot.send_document(
                    receiver_id,
                    message.document.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    thumb=(
                        message.document.thumb.file_id
                        if message.document.thumb
                        else None
                    ),
                )

            elif message.content_type == "voice":
                sent_message = self.bot.send_voice(
                    receiver_id,
                    message.voice.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    duration=message.voice.duration,
                )

            elif message.content_type == "video_note":
                sent_message = self.bot.send_video_note(
                    receiver_id,
                    message.video_note.file_id,
                    duration=message.video_note.duration,
                    length=message.video_note.length,
                )

            elif message.content_type == "sticker":
                sent_message = self.bot.send_sticker(
                    receiver_id, message.sticker.file_id
                )

            elif message.content_type == "location":
                sent_message = self.bot.send_location(
                    receiver_id,
                    latitude=message.location.latitude,
                    longitude=message.location.longitude,
                    horizontal_accuracy=(
                        message.location.horizontal_accuracy
                        if hasattr(message.location, "horizontal_accuracy")
                        else None
                    ),
                    live_period=(
                        message.location.live_period
                        if hasattr(message.location, "live_period")
                        else None
                    ),
                )

            elif message.content_type == "contact":
                sent_message = self.bot.send_contact(
                    receiver_id,
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=(
                        message.contact.last_name if message.contact.last_name else None
                    ),
                )

            elif message.content_type == "venue":
                sent_message = self.bot.send_venue(
                    receiver_id,
                    latitude=message.venue.location.latitude,
                    longitude=message.venue.location.longitude,
                    title=message.venue.title,
                    address=message.venue.address,
                    foursquare_id=(
                        message.venue.foursquare_id
                        if hasattr(message.venue, "foursquare_id")
                        else None
                    ),
                    foursquare_type=(
                        message.venue.foursquare_type
                        if hasattr(message.venue, "foursquare_type")
                        else None
                    ),
                )

            elif message.content_type == "animation":
                sent_message = self.bot.send_animation(
                    receiver_id,
                    message.animation.file_id,
                    caption=message.caption,
                    caption_entities=message.caption_entities,
                    duration=message.animation.duration,
                    width=message.animation.width,
                    height=message.animation.height,
                )

            elif message.content_type == "poll":
                sent_message = self.bot.send_poll(
                    receiver_id,
                    question=message.poll.question,
                    options=[opt.text for opt in message.poll.options],
                    is_anonymous=message.poll.is_anonymous,
                    type=message.poll.type,
                    allows_multiple_answers=message.poll.allows_multiple_answers,
                    correct_option_id=(
                        message.poll.correct_option_id
                        if hasattr(message.poll, "correct_option_id")
                        else None
                    ),
                    explanation=(
                        message.poll.explanation
                        if hasattr(message.poll, "explanation")
                        else None
                    ),
                    explanation_entities=(
                        message.poll.explanation_entities
                        if hasattr(message.poll, "explanation_entities")
                        else None
                    ),
                    open_period=(
                        message.poll.open_period
                        if hasattr(message.poll, "open_period")
                        else None
                    ),
                    close_date=(
                        message.poll.close_date
                        if hasattr(message.poll, "close_date")
                        else None
                    ),
                )

            elif message.content_type == "dice":
                sent_message = self.bot.send_dice(receiver_id, emoji=message.dice.emoji)

            elif message.content_type == "media_group":
                media = []
                for item in message.media_group_id:
                    if item.type == "photo":
                        media.append(
                            telebot.types.InputMediaPhoto(
                                item.file_id, caption=item.caption
                            )
                        )
                    elif item.type == "video":
                        media.append(
                            telebot.types.InputMediaVideo(
                                item.file_id, caption=item.caption
                            )
                        )
                sent_message = self.bot.send_media_group(receiver_id, media)

            if sent_message:
                chat_id = self._generate_chat_id(sender_id, receiver_id)
                message_id = (
                    sent_message[0].message_id
                    if isinstance(sent_message, list)
                    else sent_message.message_id
                )
                self.chats[chat_id][sender_id].append(
                    MessageInfo(
                        message_id=message.message_id,
                        chat_id=message.chat.id,
                        partner_message_id=message_id,
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
