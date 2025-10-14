"""
Обработчики команд администратора
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.database.models import User, UserStatus, Application
from bot.keyboards.common import get_user_approval_keyboard, get_main_menu

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in config.ADMIN_IDS


@router.message(Command("pending"))
async def cmd_pending(message: Message, session: AsyncSession):
    """Список пользователей, ожидающих одобрения"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    # Получаем пользователей со статусом PENDING
    result = await session.execute(
        select(User).where(User.status == UserStatus.PENDING)
    )
    pending_users = result.scalars().all()
    
    if not pending_users:
        await message.answer("✅ Нет пользователей, ожидающих одобрения")
        return
    
    for user in pending_users:
        user_info = (
            f"👤 <b>Пользователь ожидает одобрения</b>\n\n"
            f"ID: <code>{user.telegram_id}</code>\n"
            f"Username: @{user.username or 'не указан'}\n"
            f"Имя: {user.first_name or ''} {user.last_name or ''}\n"
            f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        )
        
        await message.answer(
            user_info,
            parse_mode="HTML",
            reply_markup=get_user_approval_keyboard(user.telegram_id)
        )


@router.message(Command("users"))
@router.message(F.text == "👥 Пользователи")
async def cmd_users(message: Message, session: AsyncSession):
    """Список всех пользователей"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    # Получаем всех пользователей
    result = await session.execute(select(User))
    users = result.scalars().all()
    
    if not users:
        await message.answer("📋 Список пользователей пуст")
        return
    
    # Группируем по статусам
    status_emoji = {
        UserStatus.PENDING: "⏳",
        UserStatus.APPROVED: "✅",
        UserStatus.REJECTED: "❌",
        UserStatus.REVOKED: "⛔"
    }
    
    status_name = {
        UserStatus.PENDING: "Ожидают",
        UserStatus.APPROVED: "Одобрены",
        UserStatus.REJECTED: "Отклонены",
        UserStatus.REVOKED: "Отозваны"
    }
    
    users_by_status = {}
    for user in users:
        if user.status not in users_by_status:
            users_by_status[user.status] = []
        users_by_status[user.status].append(user)
    
    response = "👥 <b>Список пользователей</b>\n\n"
    
    for status in [UserStatus.APPROVED, UserStatus.PENDING, UserStatus.REJECTED, UserStatus.REVOKED]:
        if status in users_by_status:
            response += f"{status_emoji[status]} <b>{status_name[status]}:</b>\n"
            for user in users_by_status[status]:
                admin_badge = " 👨‍💼" if user.is_admin else ""
                response += (
                    f"  • ID: <code>{user.telegram_id}</code> | "
                    f"@{user.username or 'N/A'}{admin_badge}\n"
                )
            response += "\n"
    
    response += (
        "\n<b>Команды:</b>\n"
        "/approve <code>user_id</code> - одобрить\n"
        "/reject <code>user_id</code> - отклонить\n"
        "/revoke <code>user_id</code> - отозвать доступ"
    )
    
    await message.answer(response, parse_mode="HTML")


@router.message(F.text == "⏳ На одобрении")
async def cmd_pending_button(message: Message, session: AsyncSession):
    """Обработчик кнопки 'На одобрении'"""
    await cmd_pending(message, session)


@router.message(Command("approve"))
async def cmd_approve(message: Message, session: AsyncSession):
    """Одобрение пользователя"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    # Парсим user_id
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /approve <user_id>")
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Неверный формат user_id")
        return
    
    # Одобряем пользователя
    await approve_user(target_user_id, session, message.bot)
    await message.answer(f"✅ Пользователь {target_user_id} одобрен")


@router.message(Command("reject"))
async def cmd_reject(message: Message, session: AsyncSession):
    """Отклонение пользователя"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    # Парсим user_id
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /reject <user_id>")
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Неверный формат user_id")
        return
    
    # Отклоняем пользователя
    await reject_user(target_user_id, session, message.bot)
    await message.answer(f"❌ Пользователь {target_user_id} отклонен")


@router.message(Command("revoke"))
async def cmd_revoke(message: Message, session: AsyncSession):
    """Отзыв доступа пользователя"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    # Парсим user_id
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /revoke <user_id>")
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Неверный формат user_id")
        return
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == target_user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    # Отзываем доступ
    user.status = UserStatus.REVOKED
    await session.commit()
    
    # Уведомляем пользователя
    try:
        await message.bot.send_message(
            target_user_id,
            "⛔ Ваш доступ к боту был отозван.\n"
            "Обратитесь к администратору для получения дополнительной информации."
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {target_user_id}: {e}")
    
    await message.answer(f"⛔ Доступ пользователя {target_user_id} отозван")


@router.callback_query(F.data.startswith("user_approve_"))
async def callback_approve_user(callback: CallbackQuery, session: AsyncSession):
    """Callback для одобрения пользователя"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[2])
    await approve_user(user_id, session, callback.bot)
    
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>Одобрен</b>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Пользователь одобрен")


@router.callback_query(F.data.startswith("user_reject_"))
async def callback_reject_user(callback: CallbackQuery, session: AsyncSession):
    """Callback для отклонения пользователя"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[2])
    await reject_user(user_id, session, callback.bot)
    
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>Отклонен</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Пользователь отклонен")


async def approve_user(user_id: int, session: AsyncSession, bot):
    """Одобрение пользователя"""
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    user.status = UserStatus.APPROVED
    await session.commit()
    
    # Уведомляем пользователя
    try:
        await bot.send_message(
            user_id,
            "✅ Ваш доступ одобрен!\n\n"
            "Теперь вы можете подавать заявки на служебные поездки.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")


async def reject_user(user_id: int, session: AsyncSession, bot):
    """Отклонение пользователя"""
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    user.status = UserStatus.REJECTED
    await session.commit()
    
    # Уведомляем пользователя
    try:
        await bot.send_message(
            user_id,
            "❌ К сожалению, ваша заявка на доступ была отклонена.\n"
            "Обратитесь к администратору для получения дополнительной информации."
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
