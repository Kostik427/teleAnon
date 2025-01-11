import os
from bot import ChatBot

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN is not set.")
        return
    
    bot = ChatBot(token)
    bot.run()

if __name__ == "__main__":
    main()