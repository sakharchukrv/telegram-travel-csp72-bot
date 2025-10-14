
"""
Общие клавиатуры
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню для пользователя"""
    keyboard = [
        [KeyboardButton(text="📝 Подать заявку")],
        [KeyboardButton(text="💾 Мои черновики"), KeyboardButton(text="📋 История заявок")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_admin_menu() -> ReplyKeyboardMarkup:
    """Меню для администратора"""
    keyboard = [
        [KeyboardButton(text="📝 Подать заявку")],
        [KeyboardButton(text="💾 Мои черновики"), KeyboardButton(text="📋 История заявок")],
        [KeyboardButton(text="👥 Пользователи"), KeyboardButton(text="⏳ На одобрении")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = [
        [KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    keyboard = [
        [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="confirm_edit")
        ],
        [
            InlineKeyboardButton(text="💾 Сохранить черновик", callback_data="confirm_draft")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_participants_menu(has_participants: bool = False) -> ReplyKeyboardMarkup:
    """Меню работы с участниками"""
    keyboard = []
    
    if has_participants:
        keyboard.append([KeyboardButton(text="➕ Добавить участника")])
        keyboard.append([KeyboardButton(text="📋 Список участников")])
        keyboard.append([KeyboardButton(text="🗑️ Удалить участника")])
        keyboard.append([KeyboardButton(text="✅ Завершить ввод участников")])
    else:
        keyboard.append([KeyboardButton(text="➕ Добавить участника")])
    
    keyboard.append([KeyboardButton(text="❌ Отменить")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_draft_actions_keyboard(draft_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с черновиком"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📝 Продолжить заполнение", 
                callback_data=f"draft_continue_{draft_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Удалить", 
                callback_data=f"draft_delete_{draft_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_user_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура одобрения пользователя"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Одобрить", 
                callback_data=f"user_approve_{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить", 
                callback_data=f"user_reject_{user_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
