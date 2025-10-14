"""
Обработчики для работы с черновиками
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User, UserStatus, Draft

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
    
    # Получаем черновики пользователя
    result = await session.execute(
        select(Draft)
        .where(Draft.user_id == message.from_user.id)
        .order_by(Draft.updated_at.desc())
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
    
    for draft in drafts:
        draft_data = draft.draft_data
        response += (
            f"📄 <b>Черновик #{draft.id}</b>\n"
            f"Название: {draft.name or 'Без названия'}\n"
            f"Последнее изменение: {draft.updated_at.strftime('%d.%m.%Y %H:%M')}\n"
        )
        
        # Добавляем краткую информацию из данных
        if draft_data:
            if "city" in draft_data:
                response += f"Город: {draft_data.get('city')}\n"
            if "participants" in draft_data:
                response += f"Участников: {len(draft_data.get('participants', []))}\n"
        
        response += "\n"
    
    response += "\n<i>Для продолжения заполнения черновика выберите его из списка выше.</i>"
    
    await message.answer(response, parse_mode="HTML")
    await message.answer(
        "⚠️ <b>Внимание:</b> Функция продолжения заполнения черновиков будет добавлена в следующей версии.\n\n"
        "Пока что вы можете создавать новые заявки через кнопку '📝 Подать заявку'.",
        parse_mode="HTML"
    )
