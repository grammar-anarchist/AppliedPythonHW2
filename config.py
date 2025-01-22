import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
nutrition_api_id = os.getenv("NUTRITION_API_ID")
nutrition_api_key = os.getenv("NUTRITION_API_KEY")

if not bot_token:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")
