import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8265367568:AAF39Ckal4XiGbF_vIHlG_WgTSiJT5jOD70')
    ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '7002989319').split(',')]
    GROUP_ID = os.getenv('GROUP_ID', '1003126963687')
    
    # Web Configuration - SERVER PORT 5000 SET KAREIN
    BASE_URL = "https://7375253057ab77.lhr.life"
    PORT = 5000
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'ludo-tournament-secret-key-2024')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'bot.db')
    
    # Game Configuration
    DEFAULT_BALANCE = 1000.0
    COMMISSION_RATE = 0.05  # 5%
