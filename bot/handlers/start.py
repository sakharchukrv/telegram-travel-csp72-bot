
"""
Обработчики команд старта и помощи
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.database.models import User, UserStatus
from bot.keyboards import get_main_menu, get_admin_menu

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    # Проверяем, есть ли пользователь в базе
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Создаем нового пользователя
        is_admin = user_id in config.ADMIN_IDS
        user = User(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            status=UserStatus.APPROVED if is_admin else UserStatus.PENDING,
            is_admin=is_admin
        )
        session.add(user)
        await session.commit()
        
        logger.info(f"Создан новый пользователь: {user_id} (admin: {is_admin})")
        
        if is_admin:
            await message.answer(
                "👋 Здравствуйте! Вы вошли как администратор.\n\n"
                "Вы можете:\n"
                "• Подавать заявки на служебные поездки\n"
                "• Управлять пользователями\n"
                "• Просматривать все заявки",
                reply_markup=get_admin_menu()
            )
        else:
            await message.answer(
                "👋 Здравствуйте!\n\n"
                "Ваша заявка на доступ отправлена администратору.\n"
                "Пожалуйста, ожидайте одобрения."
            )
            
            # Уведомляем админов о новом пользователе
            for admin_id in config.ADMIN_IDS:
                try:
                    user_info = (
                        f"👤 Новый пользователь:\n"
                        f"ID: {user_id}\n"
                        f"Username: @{message.from_user.username or 'не указан'}\n"
                        f"Имя: {message.from_user.first_name or ''} "
                        f"{message.from_user.last_name or ''}\n\n"
                        f"Для одобрения: /approve {user_id}\n"
                        f"Для отклонения: /reject {user_id}"
                    )
                    await message.bot.send_message(admin_id, user_info)
                except Exception as e:
                    logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
    else:
        # Пользователь уже существует
        if user.status == UserStatus.PENDING:
            await message.answer(
                "⏳ Ваша заявка на доступ все еще ожидает одобрения администратором."
            )
        elif user.status == UserStatus.REJECTED:
            await message.answer(
                "❌ К сожалению, ваша заявка была отклонена.\n"
                "Обратитесь к администратору для получения дополнительной информации."
            )
        elif user.status == UserStatus.REVOKED:
            await message.answer(
                "⛔ Ваш доступ был отозван.\n"
                "Обратитесь к администратору для получения дополнительной информации."
            )
        else:
            # Одобрен
            keyboard = get_admin_menu() if user.is_admin else get_main_menu()
            role = "администратор" if user.is_admin else "пользователь"
            
            await message.answer(
                f"👋 С возвращением!\n\n"
                f"Вы вошли как {role}.\n"
                f"Выберите действие из меню ниже:",
                reply_markup=keyboard
            )


@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message, session: AsyncSession):
    """Обработчик кнопки помощи"""
    user_id = message.from_user.id
    
    # Проверяем статус пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.status != UserStatus.APPROVED:
        await message.answer(
            "⏳ Ваш доступ еще не одобрен администратором.\n"
            "Пожалуйста, дождитесь одобрения."
        )
        return
    
    help_text = (
        "ℹ️ <b>Справка по использованию бота</b>\n\n"
        "<b>Основные функции:</b>\n\n"
        "📝 <b>Подать заявку</b>\n"
        "Создание новой заявки на служебную поездку. Вы пройдете пошаговый процесс заполнения:\n"
        "• Вид спорта\n"
        "• Ранг мероприятия\n"
        "• Страна и город назначения\n"
        "• Список участников с датами поездки\n\n"
        
        "💾 <b>Мои черновики</b>\n"
        "Просмотр сохраненных черновиков заявок. "
        "Вы можете продолжить заполнение или удалить черновик.\n\n"
        
        "📋 <b>История заявок</b>\n"
        "Просмотр всех поданных вами заявок.\n\n"
        
        "<b>Форматы данных:</b>\n"
        "• Даты: ДД.ММ.ГГГГ (например, 25.12.2024)\n"
        "• ФИО: минимум Фамилия и Имя\n\n"
        
        "<b>Управление заявкой:</b>\n"
        "• ❌ Отменить - отмена текущего действия\n"
        "• ⬅️ Назад - возврат к предыдущему шагу\n"
        "• 💾 Сохранить черновик - сохранение для продолжения позже\n\n"
    )
    
    if user.is_admin:
        help_text += (
            "<b>Команды администратора:</b>\n"
            "• /pending - список ожидающих одобрения\n"
            "• /users - список всех пользователей\n"
            "• /approve <user_id> - одобрить пользователя\n"
            "• /reject <user_id> - отклонить пользователя\n"
            "• /revoke <user_id> - отозвать доступ\n"
        )
    
    await message.answer(help_text, parse_mode="HTML")
