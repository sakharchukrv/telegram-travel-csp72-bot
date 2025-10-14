
"""
Валидаторы данных
"""
import re
from datetime import datetime
from typing import Tuple


def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    Валидация даты в формате ДД.ММ.ГГГГ
    
    Args:
        date_str: Строка с датой
        
    Returns:
        Tuple[bool, str]: (валидна ли дата, сообщение об ошибке)
    """
    # Проверка формата
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern, date_str):
        return False, "Дата должна быть в формате ДД.ММ.ГГГГ (например, 25.12.2024)"
    
    # Проверка валидности даты
    try:
        day, month, year = map(int, date_str.split('.'))
        date = datetime(year, month, day)
        
        # Проверка что дата не в прошлом (опционально)
        # if date.date() < datetime.now().date():
        #     return False, "Дата не может быть в прошлом"
        
        return True, ""
    except ValueError:
        return False, "Указана некорректная дата"


def validate_date_range(date_from: str, date_to: str) -> Tuple[bool, str]:
    """
    Валидация диапазона дат
    
    Args:
        date_from: Дата начала
        date_to: Дата окончания
        
    Returns:
        Tuple[bool, str]: (валиден ли диапазон, сообщение об ошибке)
    """
    # Проверка формата обеих дат
    is_valid_from, msg_from = validate_date(date_from)
    if not is_valid_from:
        return False, f"Дата 'С': {msg_from}"
    
    is_valid_to, msg_to = validate_date(date_to)
    if not is_valid_to:
        return False, f"Дата 'ПО': {msg_to}"
    
    # Проверка что дата окончания >= даты начала
    try:
        day_from, month_from, year_from = map(int, date_from.split('.'))
        day_to, month_to, year_to = map(int, date_to.split('.'))
        
        date_obj_from = datetime(year_from, month_from, day_from)
        date_obj_to = datetime(year_to, month_to, day_to)
        
        if date_obj_to < date_obj_from:
            return False, "Дата окончания не может быть раньше даты начала"
        
        return True, ""
    except ValueError:
        return False, "Ошибка при проверке диапазона дат"


def validate_full_name(name: str) -> Tuple[bool, str]:
    """
    Валидация ФИО
    
    Args:
        name: ФИО
        
    Returns:
        Tuple[bool, str]: (валидно ли имя, сообщение об ошибке)
    """
    if not name or not name.strip():
        return False, "ФИО не может быть пустым"
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    # Проверка минимум 2 слова (Фамилия Имя)
    words = name.split()
    if len(words) < 2:
        return False, "ФИО должно содержать минимум Фамилию и Имя"
    
    # Проверка что все слова начинаются с заглавной буквы
    # for word in words:
    #     if not word[0].isupper():
    #         return False, "Каждое слово в ФИО должно начинаться с заглавной буквы"
    
    return True, ""


def validate_text(text: str, min_length: int = 1, max_length: int = 500) -> Tuple[bool, str]:
    """
    Валидация текста
    
    Args:
        text: Текст для проверки
        min_length: Минимальная длина
        max_length: Максимальная длина
        
    Returns:
        Tuple[bool, str]: (валиден ли текст, сообщение об ошибке)
    """
    if not text or not text.strip():
        return False, "Поле не может быть пустым"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Текст должен содержать минимум {min_length} символов"
    
    if len(text) > max_length:
        return False, f"Текст не должен превышать {max_length} символов"
    
    return True, ""
