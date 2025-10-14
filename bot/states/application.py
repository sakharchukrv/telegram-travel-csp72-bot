
"""
FSM состояния для заполнения заявки
"""
from aiogram.fsm.state import State, StatesGroup


class ApplicationStates(StatesGroup):
    """Состояния заполнения заявки"""
    
    # Основная информация
    sport_type = State()  # Вид спорта
    event_rank = State()  # Ранг мероприятия
    country = State()  # Страна
    city = State()  # Город
    
    # Участники
    participants_menu = State()  # Меню работы с участниками
    participant_name = State()  # Ввод ФИО участника
    participant_date_from = State()  # Дата начала
    participant_date_to = State()  # Дата окончания
    
    # Подтверждение
    confirm = State()  # Подтверждение заявки
    
    # Черновики
    draft_name = State()  # Название черновика
