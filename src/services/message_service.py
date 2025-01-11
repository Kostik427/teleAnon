from telebot import TeleBot
from src.services.matching_service import MatchingService


class MessageService:
    def __init__(self, bot: TeleBot, matching_service: MatchingService):
        self.bot = bot
        self.matching_service = matching_service

    def forward_message(self, user_id: int, message):
        partner_id = self.matching_service.active_chats.get(user_id)
        if not partner_id:
            self.bot.reply_to(message, "You are not in an active chat.")
            return

        try:
            if message.content_type == "text":
                self.bot.send_message(partner_id, message.text)
            elif message.content_type == "photo":
                self.bot.send_photo(partner_id, message.photo[-1].file_id)
            elif message.content_type == "video":
                self.bot.send_video(partner_id, message.video.file_id)
            elif message.content_type == "voice":
                self.bot.send_voice(partner_id, message.voice.file_id)
            else:
                self.bot.reply_to(message, "Unsupported content type.")
        except Exception as e:
            self.bot.reply_to(message, f"Error forwarding message: {e}")
