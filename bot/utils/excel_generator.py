"""
Генератор Excel файлов по шаблону
"""
import logging
import os
from typing import Dict, List
from datetime import datetime
import shutil

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from bot.config import config

logger = logging.getLogger(__name__)


def generate_excel(application_data: Dict, output_dir: str = "/tmp") -> str:
    """
    Генерация Excel файла по шаблону
    
    Args:
        application_data: Данные заявки
        output_dir: Директория для сохранения файла
        
    Returns:
        str: Путь к сгенерированному файлу
    """
    logger.info("Начинаем генерацию Excel файла")
    
    # Копируем шаблон
    template_path = config.TEMPLATE_FILE
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")
    
    # Генерируем имя выходного файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Заявка_{application_data.get('city', 'Unknown')}_{timestamp}.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    # Копируем шаблон
    shutil.copy2(template_path, output_path)
    
    # Открываем файл для редактирования
    wb = openpyxl.load_workbook(output_path)
    
    # Работаем с листом "Версия для печати"
    ws: Worksheet = wb["Версия для печати"]
    
    # Заполняем основные поля
    ws["B5"] = application_data.get("sport_type", "")  # Вид спорта
    ws["B7"] = application_data.get("event_rank", "")  # Ранг мероприятия
    ws["I5"] = application_data.get("city", "")  # Город
    ws["I7"] = application_data.get("country", "")  # Страна
    
    # Заполняем участников
    participants: List[Dict] = application_data.get("participants", [])
    
    for idx, participant in enumerate(participants):
        # Определяем, в какую колонку писать (1-15 или 16-30)
        if idx < 15:
            # Первая колонка (строки 10-24)
            row = 10 + idx
            ws[f"B{row}"] = participant.get("full_name", "")
            ws[f"D{row}"] = participant.get("date_from", "")
            ws[f"E{row}"] = participant.get("date_to", "")
        else:
            # Вторая колонка (строки 10-24)
            row = 10 + (idx - 15)
            ws[f"G{row}"] = participant.get("full_name", "")
            ws[f"I{row}"] = participant.get("date_from", "")
            ws[f"J{row}"] = participant.get("date_to", "")
    
    # Сохраняем файл
    wb.save(output_path)
    wb.close()
    
    logger.info(f"Excel файл успешно создан: {output_path}")
    return output_path
