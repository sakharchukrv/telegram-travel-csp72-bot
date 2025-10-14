
"""
Конфигурация бота
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    # Telegram
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_IDS: List[int] = [
        int(x.strip()) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if x.strip()
    ]
    TARGET_CHAT_ID: int = int(os.getenv("TARGET_CHAT_ID", "-1923544479"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/travel_bot"
    )
    
    # SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.mail.ru")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    
    # Email
    EMAIL_TO: str = os.getenv("EMAIL_TO_OVERRIDE", "srv@cspto.ru")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "templates")
    TEMPLATE_FILE: str = os.path.join(TEMPLATES_DIR, "Заявка на СМ.xlsx")
    
    @classmethod
    def validate(cls) -> None:
        """Валидация конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
        if not cls.ADMIN_IDS:
            raise ValueError("TELEGRAM_ADMIN_IDS не установлен")
        if not cls.SMTP_USER or not cls.SMTP_PASSWORD:
            raise ValueError("SMTP_USER и SMTP_PASSWORD должны быть установлены")
        if not os.path.exists(cls.TEMPLATE_FILE):
            raise ValueError(f"Файл шаблона не найден: {cls.TEMPLATE_FILE}")


config = Config()
