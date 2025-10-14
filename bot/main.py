"""
Главный модуль бота
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config
from bot.database import init_db, get_session
from bot.handlers import start, admin, application, drafts


# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Инициализация бота...")
    
    # Инициализация базы данных
    await init_db()
    
    # Уведомление админов о запуске
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "🚀 Бот запущен и готов к работе!"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
    
    logger.info("Бот успешно запущен")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Остановка бота...")
    
    # Уведомление админов об остановке
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "⛔ Бот остановлен"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
    
    logger.info("Бот остановлен")


async def main():
    """Основная функция"""
    try:
        # Валидация конфигурации
        config.validate()
        
        # Создание бота и диспетчера
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher(storage=MemoryStorage())
        
        # Middleware для добавления сессии БД
        @dp.update.middleware()
        async def db_session_middleware(handler, event, data):
            async for session in get_session():
                data["session"] = session
                return await handler(event, data)
        
        # Регистрация роутеров
        dp.include_router(start.router)
        dp.include_router(admin.router)
        dp.include_router(application.router)
        dp.include_router(drafts.router)
        
        # Запуск
        await on_startup(bot)
        
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            await on_shutdown(bot)
            await bot.session.close()
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        sys.exit(1)
