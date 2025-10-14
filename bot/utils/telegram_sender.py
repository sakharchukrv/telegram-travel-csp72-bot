
"""
Отправка в Telegram чат
"""
import logging
from typing import Optional

from aiogram import Bot
from aiogram.types import FSInputFile

from bot.config import config

logger = logging.getLogger(__name__)


async def send_to_telegram(
    bot: Bot,
    message: str,
    attachment_path: Optional[str] = None,
    chat_id: Optional[int] = None
) -> bool:
    """
    Отправка сообщения в Telegram чат
    
    Args:
        bot: Экземпляр бота
        message: Текст сообщения
        attachment_path: Путь к файлу для прикрепления
        chat_id: ID чата (если None, берется из конфига)
        
    Returns:
        bool: Успешно ли отправлено
    """
    try:
        target_chat_id = chat_id or config.TARGET_CHAT_ID
        logger.info(f"Отправка сообщения в Telegram чат: {target_chat_id}")
        
        if attachment_path:
            # Отправляем с файлом
            document = FSInputFile(attachment_path)
            await bot.send_document(
                chat_id=target_chat_id,
                document=document,
                caption=message
            )
        else:
            # Отправляем только текст
            await bot.send_message(
                chat_id=target_chat_id,
                text=message
            )
        
        logger.info("Сообщение успешно отправлено в Telegram")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}", exc_info=True)
        return False
