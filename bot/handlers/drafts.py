"""
Обработчики для работы с черновиками
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User, UserStatus, Application, ApplicationStatus
from bot.keyboards import get_participants_menu, get_admin_menu, get_main_menu
from bot.states import ApplicationStates

logger = logging.getLogger(__name__)

router = Router()


async def check_user_access(user_id: int, session: AsyncSession) -> tuple[bool, User | None]:
    """Проверка доступа пользователя"""
    result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.status != UserStatus.APPROVED:
        return False, user
    
    return True, user


@router.message(F.text == "💾 Мои черновики")
async def show_drafts(message: Message, session: AsyncSession):
    """Показ списка черновиков"""
    has_access, user = await check_user_access(message.from_user.id, session)
    
    if not has_access:
        await message.answer("❌ У вас нет доступа")
        return
    
    # Получаем черновики пользователя (сохранены как заявки со статусом DRAFT)
    result = await session.execute(
        select(Application)
        .where(
            Application.user_id == message.from_user.id,
            Application.status == ApplicationStatus.DRAFT
        )
        .order_by(Application.updated_at.desc())
    )
    drafts = result.scalars().all()
    
    if not drafts:
        await message.answer(
            "💾 У вас пока нет сохраненных черновиков\n\n"
            "Вы можете сохранить черновик при заполнении заявки, "
            "нажав кнопку '💾 Сохранить черновик' на этапе подтверждения."
        )
        return
    
    response = "💾 <b>Ваши черновики:</b>\n\n"
    
    # Создаем инлайн клавиатуру для выбора черновика
    keyboard_buttons = []
    
    for draft in drafts:
        participants_count = len(draft.participants)
        response += (
            f"📄 <b>Черновик #{draft.id}</b>\n"
            f"Город: {draft.city or 'Не указан'}, {draft.country or 'Не указана'}\n"
            f"Участников: {participants_count}\n"
            f"Последнее изменение: {draft.updated_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
        
        # Кнопки для каждого черновика
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"✏️ Продолжить #{draft.id}",
                callback_data=f"load_draft:{draft.id}"
            ),
            InlineKeyboardButton(
                text=f"🗑️ Удалить #{draft.id}",
                callback_data=f"delete_draft:{draft.id}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    response += "\n<i>Выберите черновик для продолжения работы или удаления:</i>"
    
    await message.answer(response, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data.startswith("load_draft:"))
async def load_draft(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Загрузка черновика для продолжения работы"""
    await callback.answer()
    
    try:
        draft_id = int(callback.data.split(":")[1])
        
        # Получаем черновик
        result = await session.execute(
            select(Application)
            .where(
                Application.id == draft_id,
                Application.user_id == callback.from_user.id,
                Application.status == ApplicationStatus.DRAFT
            )
        )
        draft = result.scalar_one_or_none()
        
        if not draft:
            await callback.message.answer("❌ Черновик не найден")
            return
        
        # Восстанавливаем данные в состояние
        participants_data = []
        for p in draft.participants:
            participants_data.append({
                "full_name": p.full_name,
                "date_from": p.date_from,
                "date_to": p.date_to
            })
        
        await state.update_data(
            sport_type=draft.sport_type,
            event_rank=draft.event_rank,
            country=draft.country,
            city=draft.city,
            participants=participants_data,
            draft_id=draft_id  # Сохраняем ID черновика для обновления
        )
        
        # Переходим к меню участников
        await state.set_state(ApplicationStates.participants_menu)
        
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"✅ <b>Черновик #{draft_id} загружен!</b>\n\n"
            f"📋 <b>Текущие данные:</b>\n"
            f"Вид спорта: {draft.sport_type}\n"
            f"Ранг мероприятия: {draft.event_rank}\n"
            f"Страна: {draft.country}\n"
            f"Город: {draft.city}\n"
            f"Участников: {len(participants_data)}\n\n"
            "Вы можете продолжить редактирование:",
            parse_mode="HTML",
            reply_markup=get_participants_menu(has_participants=len(participants_data) > 0)
        )
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке черновика: {e}", exc_info=True)
        await callback.message.answer("❌ Произошла ошибка при загрузке черновика")


@router.callback_query(F.data.startswith("delete_draft:"))
async def delete_draft(callback: CallbackQuery, session: AsyncSession):
    """Удаление черновика"""
    await callback.answer()
    
    try:
        draft_id = int(callback.data.split(":")[1])
        
        # Получаем черновик
        result = await session.execute(
            select(Application)
            .where(
                Application.id == draft_id,
                Application.user_id == callback.from_user.id,
                Application.status == ApplicationStatus.DRAFT
            )
        )
        draft = result.scalar_one_or_none()
        
        if not draft:
            await callback.message.answer("❌ Черновик не найден")
            return
        
        # Удаляем черновик
        await session.delete(draft)
        await session.commit()
        
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"✅ Черновик #{draft_id} успешно удален",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при удалении черновика: {e}", exc_info=True)
        await callback.message.answer("❌ Произошла ошибка при удалении черновика")
