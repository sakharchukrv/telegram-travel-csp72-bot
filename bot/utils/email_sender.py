
"""
Отправка Email
"""
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional

import aiosmtplib

from bot.config import config

logger = logging.getLogger(__name__)


async def send_email(
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
    to_email: Optional[str] = None
) -> bool:
    """
    Отправка email
    
    Args:
        subject: Тема письма
        body: Текст письма
        attachment_path: Путь к файлу для прикрепления
        to_email: Email получателя (если None, берется из конфига)
        
    Returns:
        bool: Успешно ли отправлено
    """
    try:
        logger.info(f"Отправка email: {subject}")
        
        # Создаем сообщение
        message = MIMEMultipart()
        message["From"] = config.SMTP_FROM
        message["To"] = to_email or config.EMAIL_TO
        message["Subject"] = subject
        
        # Добавляем текст
        message.attach(MIMEText(body, "plain", "utf-8"))
        
        # Добавляем вложение
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                attachment = MIMEApplication(f.read())
                filename = os.path.basename(attachment_path)
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=filename
                )
                message.attach(attachment)
        
        # Отправляем
        if config.SMTP_PORT == 465:
            # SSL
            await aiosmtplib.send(
                message,
                hostname=config.SMTP_HOST,
                port=config.SMTP_PORT,
                username=config.SMTP_USER,
                password=config.SMTP_PASSWORD,
                use_tls=True
            )
        else:
            # STARTTLS
            await aiosmtplib.send(
                message,
                hostname=config.SMTP_HOST,
                port=config.SMTP_PORT,
                username=config.SMTP_USER,
                password=config.SMTP_PASSWORD,
                start_tls=True
            )
        
        logger.info("Email успешно отправлен")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отправке email: {e}", exc_info=True)
        return False
