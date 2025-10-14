"""
Обработчики для подачи заявок
"""
import logging
import os
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.database.models import User, UserStatus, Application, ApplicationStatus, Participant
from bot.keyboards import (
    get_cancel_keyboard,
    get_participants_menu,
    get_confirmation_keyboard,
    get_main_menu,
    get_admin_menu
)
from bot.states import ApplicationStates
from bot.utils import (
    validate_date,
    validate_date_range,
    validate_full_name,
    validate_text,
    generate_excel,
    send_email
    # send_to_telegram  # ОТКЛЮЧЕНО: не используется после отключения отправки в Telegram чат
)

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


@router.message(F.text == "📝 Подать заявку")
async def start_application(message: Message, state: FSMContext, session: AsyncSession):
    """Начало подачи заявки"""
    has_access, user = await check_user_access(message.from_user.id, session)
    
    if not has_access:
        await message.answer(
            "❌ У вас нет доступа к подаче заявок.\n"
            "Дождитесь одобрения администратора или обратитесь к нему."
        )
        return
    
    # Очищаем предыдущее состояние
    await state.clear()
    
    # Инициализируем данные
    await state.update_data(
        participants=[],
        user_full_name=user.full_name or f"{user.first_name or ''} {user.last_name or ''}".strip(),
        user_organization=user.organization or ""
    )
    
    await state.set_state(ApplicationStates.sport_type)
    await message.answer(
        "📝 <b>Создание заявки на служебную поездку</b>\n\n"
        "Шаг 1 из 5: Введите <b>вид спорта</b>:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(ApplicationStates.sport_type))
async def process_sport_type(message: Message, state: FSMContext):
    """Обработка ввода вида спорта"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    is_valid, error_msg = validate_text(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(sport_type=message.text.strip())
    await state.set_state(ApplicationStates.event_rank)
    
    await message.answer(
        "✅ Вид спорта сохранен\n\n"
        "Шаг 2 из 5: Введите <b>ранг спортивного мероприятия</b>:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(ApplicationStates.event_rank))
async def process_event_rank(message: Message, state: FSMContext):
    """Обработка ввода ранга мероприятия"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    is_valid, error_msg = validate_text(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(event_rank=message.text.strip())
    await state.set_state(ApplicationStates.country)
    
    await message.answer(
        "✅ Ранг мероприятия сохранен\n\n"
        "Шаг 3 из 5: Введите <b>страну назначения</b>:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(ApplicationStates.country))
async def process_country(message: Message, state: FSMContext):
    """Обработка ввода страны"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    is_valid, error_msg = validate_text(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(country=message.text.strip())
    await state.set_state(ApplicationStates.city)
    
    await message.answer(
        "✅ Страна сохранена\n\n"
        "Шаг 4 из 5: Введите <b>город назначения</b>:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(ApplicationStates.city))
async def process_city(message: Message, state: FSMContext):
    """Обработка ввода города"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    is_valid, error_msg = validate_text(message.text, min_length=2, max_length=255)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(city=message.text.strip())
    await state.set_state(ApplicationStates.participants_menu)
    
    data = await state.get_data()
    participants = data.get("participants", [])
    
    await message.answer(
        "✅ Город сохранен\n\n"
        "Шаг 5 из 5: <b>Добавление участников поездки</b>\n\n"
        f"Участников добавлено: {len(participants)}\n\n"
        "Добавьте минимум одного участника:",
        parse_mode="HTML",
        reply_markup=get_participants_menu(has_participants=len(participants) > 0)
    )


@router.message(StateFilter(ApplicationStates.participants_menu))
async def process_participants_menu(message: Message, state: FSMContext):
    """Обработка меню участников"""
    data = await state.get_data()
    participants = data.get("participants", [])
    
    if message.text == "➕ Добавить участника":
        await state.set_state(ApplicationStates.participant_name)
        await message.answer(
            "👤 Введите <b>ФИО участника</b> (Фамилия Имя Отчество):",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
    
    elif message.text == "📋 Список участников":
        if not participants:
            await message.answer("📋 Список участников пуст")
            return
        
        response = "📋 <b>Список участников:</b>\n\n"
        for idx, p in enumerate(participants, 1):
            response += (
                f"{idx}. <b>{p['full_name']}</b>\n"
                f"   Даты: {p['date_from']} - {p['date_to']}\n\n"
            )
        
        await message.answer(response, parse_mode="HTML")
    
    elif message.text == "🗑️ Удалить участника":
        if not participants:
            await message.answer("❌ Нет участников для удаления")
            return
        
        # Показываем список для удаления
        response = "🗑️ Введите номер участника для удаления:\n\n"
        for idx, p in enumerate(participants, 1):
            response += f"{idx}. {p['full_name']}\n"
        
        await message.answer(response)
        # TODO: Реализовать удаление через FSM состояние
    
    elif message.text == "✅ Завершить ввод участников":
        if not participants:
            await message.answer("❌ Добавьте минимум одного участника")
            return
        
        # Переходим к подтверждению
        await show_confirmation(message, state)
    
    elif message.text == "❌ Отменить":
        await cancel_application(message, state)


@router.message(StateFilter(ApplicationStates.participant_name))
async def process_participant_name(message: Message, state: FSMContext):
    """Обработка ввода ФИО участника"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    is_valid, error_msg = validate_full_name(message.text)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(current_participant_name=message.text.strip())
    await state.set_state(ApplicationStates.participant_date_from)
    
    await message.answer(
        "✅ ФИО сохранено\n\n"
        "Введите <b>дату начала поездки</b> (формат: ДД.ММ.ГГГГ):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(ApplicationStates.participant_date_from))
async def process_participant_date_from(message: Message, state: FSMContext):
    """Обработка ввода даты начала"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    is_valid, error_msg = validate_date(message.text)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(current_participant_date_from=message.text.strip())
    await state.set_state(ApplicationStates.participant_date_to)
    
    await message.answer(
        "✅ Дата начала сохранена\n\n"
        "Введите <b>дату окончания поездки</b> (формат: ДД.ММ.ГГГГ):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(ApplicationStates.participant_date_to))
async def process_participant_date_to(message: Message, state: FSMContext):
    """Обработка ввода даты окончания"""
    if message.text == "❌ Отменить":
        await cancel_application(message, state)
        return
    
    data = await state.get_data()
    date_from = data.get("current_participant_date_from")
    date_to = message.text.strip()
    
    is_valid, error_msg = validate_date_range(date_from, date_to)
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nПопробуйте еще раз:")
        return
    
    # Добавляем участника
    participants = data.get("participants", [])
    participants.append({
        "full_name": data.get("current_participant_name"),
        "date_from": date_from,
        "date_to": date_to
    })
    
    await state.update_data(participants=participants)
    await state.set_state(ApplicationStates.participants_menu)
    
    await message.answer(
        f"✅ Участник добавлен!\n\n"
        f"Всего участников: {len(participants)}\n\n"
        "Выберите действие:",
        reply_markup=get_participants_menu(has_participants=True)
    )


async def show_confirmation(message: Message, state: FSMContext):
    """Показ подтверждения заявки"""
    data = await state.get_data()
    
    # Формируем сводку
    summary = (
        "📋 <b>Проверьте данные заявки:</b>\n\n"
        f"<b>Вид спорта:</b> {data.get('sport_type')}\n"
        f"<b>Ранг мероприятия:</b> {data.get('event_rank')}\n"
        f"<b>Страна:</b> {data.get('country')}\n"
        f"<b>Город:</b> {data.get('city')}\n\n"
        f"<b>Участники ({len(data.get('participants', []))}):</b>\n"
    )
    
    for idx, p in enumerate(data.get("participants", []), 1):
        summary += (
            f"{idx}. {p['full_name']}\n"
            f"   {p['date_from']} - {p['date_to']}\n"
        )
    
    await state.set_state(ApplicationStates.confirm)
    await message.answer(
        summary,
        parse_mode="HTML",
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(F.data == "confirm_yes", StateFilter(ApplicationStates.confirm))
async def confirm_application(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение и отправка заявки"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    
    processing_msg = await callback.message.answer("⏳ Обработка заявки...")
    
    try:
        data = await state.get_data()
        user_id = callback.from_user.id
        
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one()
        
        # Создаем заявку
        application = Application(
            user_id=user_id,
            sport_type=data.get("sport_type"),
            event_rank=data.get("event_rank"),
            country=data.get("country"),
            city=data.get("city"),
            participants_data={"participants": data.get("participants", [])},
            status=ApplicationStatus.SUBMITTED,
            submitted_at=datetime.now()
        )
        session.add(application)
        await session.flush()
        
        # Добавляем участников
        for idx, p in enumerate(data.get("participants", []), 1):
            participant = Participant(
                application_id=application.id,
                full_name=p["full_name"],
                date_from=p["date_from"],
                date_to=p["date_to"],
                order_num=idx
            )
            session.add(participant)
        
        await session.commit()
        
        # Генерируем Excel
        excel_data = {
            "sport_type": data.get("sport_type"),
            "event_rank": data.get("event_rank"),
            "country": data.get("country"),
            "city": data.get("city"),
            "participants": data.get("participants", [])
        }
        
        excel_path = generate_excel(excel_data)
        application.excel_file_path = excel_path
        
        # Отправляем Email
        email_subject = f"Заявка на служебную поездку — {user.full_name or user.first_name} — {data.get('city')}/{datetime.now().strftime('%d.%m.%Y')}"
        email_body = (
            f"Заявка на служебную поездку\n\n"
            f"От: {user.full_name or user.first_name} {user.last_name or ''}\n"
            f"Организация: {user.organization or 'Не указана'}\n\n"
            f"Вид спорта: {data.get('sport_type')}\n"
            f"Ранг мероприятия: {data.get('event_rank')}\n"
            f"Страна: {data.get('country')}\n"
            f"Город: {data.get('city')}\n\n"
            f"Количество участников: {len(data.get('participants', []))}\n\n"
            f"Подробности в прикрепленном файле."
        )
        
        email_sent = await send_email(
            subject=email_subject,
            body=email_body,
            attachment_path=excel_path
        )
        application.email_sent = email_sent
        
        # # ОТКЛЮЧЕНО: Отправка в Telegram чат (TARGET_CHAT_ID)
        # # Оставлена только отправка на email
        # telegram_message = (
        #     f"📝 Новая заявка на служебную поездку\n\n"
        #     f"От: {user.full_name or user.first_name} {user.last_name or ''}\n"
        #     f"Username: @{user.username or 'N/A'}\n\n"
        #     f"Вид спорта: {data.get('sport_type')}\n"
        #     f"Ранг: {data.get('event_rank')}\n"
        #     f"Направление: {data.get('country')}, {data.get('city')}\n"
        #     f"Участников: {len(data.get('participants', []))}"
        # )
        # 
        # telegram_sent = await send_to_telegram(
        #     bot=callback.bot,
        #     message=telegram_message,
        #     attachment_path=excel_path
        # )
        # application.telegram_sent = telegram_sent
        telegram_sent = False  # Отправка в Telegram отключена
        
        await session.commit()
        
        # Очищаем состояние
        await state.clear()
        
        # Определяем клавиатуру
        keyboard = get_admin_menu() if user.is_admin else get_main_menu()
        
        await processing_msg.edit_text(
            "✅ <b>Заявка успешно отправлена!</b>\n\n"
            f"ID заявки: {application.id}\n"
            f"Email: {'✅' if email_sent else '❌'}\n\n"
            "Вы можете посмотреть историю заявок в меню.",
            parse_mode="HTML"
        )
        
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка при создании заявки: {e}", exc_info=True)
        await processing_msg.edit_text(
            "❌ Произошла ошибка при отправке заявки.\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )
        
        keyboard = get_admin_menu() if callback.from_user.id in config.ADMIN_IDS else get_main_menu()
        await callback.message.answer("Выберите действие:", reply_markup=keyboard)


@router.callback_query(F.data == "confirm_edit", StateFilter(ApplicationStates.confirm))
async def edit_application(callback: CallbackQuery, state: FSMContext):
    """Редактирование заявки"""
    await callback.answer("Функция редактирования в разработке")
    # TODO: Реализовать редактирование


@router.callback_query(F.data == "confirm_draft", StateFilter(ApplicationStates.confirm))
async def save_draft(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Сохранение черновика"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    
    try:
        data = await state.get_data()
        user_id = callback.from_user.id
        
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one()
        
        # Создаем черновик заявки
        draft = Application(
            user_id=user_id,
            sport_type=data.get("sport_type"),
            event_rank=data.get("event_rank"),
            country=data.get("country"),
            city=data.get("city"),
            participants_data={"participants": data.get("participants", [])},
            status=ApplicationStatus.DRAFT,  # Статус черновика
            submitted_at=None
        )
        session.add(draft)
        
        # Добавляем участников
        for idx, p in enumerate(data.get("participants", []), 1):
            participant = Participant(
                application_id=draft.id,
                full_name=p["full_name"],
                date_from=p["date_from"],
                date_to=p["date_to"],
                order_num=idx
            )
            session.add(participant)
        
        await session.commit()
        
        # Очищаем состояние
        await state.clear()
        
        # Определяем клавиатуру
        keyboard = get_admin_menu() if user.is_admin else get_main_menu()
        
        await callback.message.answer(
            f"✅ <b>Черновик сохранён!</b>\n\n"
            f"ID черновика: {draft.id}\n\n"
            "Вы можете продолжить работу с ним позже через историю заявок.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении черновика: {e}", exc_info=True)
        
        keyboard = get_admin_menu() if callback.from_user.id in config.ADMIN_IDS else get_main_menu()
        await callback.message.answer(
            "❌ Произошла ошибка при сохранении черновика.\n"
            "Попробуйте еще раз или обратитесь к администратору.",
            reply_markup=keyboard
        )


async def cancel_application(message: Message, state: FSMContext):
    """Отмена заявки"""
    await state.clear()
    
    user_id = message.from_user.id
    keyboard = get_admin_menu() if user_id in config.ADMIN_IDS else get_main_menu()
    
    await message.answer(
        "❌ Заявка отменена",
        reply_markup=keyboard
    )


@router.message(F.text == "📋 История заявок")
async def show_history(message: Message, session: AsyncSession):
    """Показ истории заявок"""
    has_access, user = await check_user_access(message.from_user.id, session)
    
    if not has_access:
        await message.answer("❌ У вас нет доступа")
        return
    
    # Получаем заявки пользователя
    result = await session.execute(
        select(Application)
        .where(Application.user_id == message.from_user.id)
        .order_by(Application.created_at.desc())
    )
    applications = result.scalars().all()
    
    if not applications:
        await message.answer("📋 У вас пока нет поданных заявок")
        return
    
    response = "📋 <b>Ваши заявки:</b>\n\n"
    
    for app in applications[:10]:  # Показываем последние 10
        status_emoji = "✅" if app.status == ApplicationStatus.SUBMITTED else "⏳"
        response += (
            f"{status_emoji} <b>Заявка #{app.id}</b>\n"
            f"Направление: {app.city}, {app.country}\n"
            f"Дата: {app.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"Участников: {len(app.participants)}\n\n"
        )
    
    await message.answer(response, parse_mode="HTML")
