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
    
    # Функция для безопасной записи в ячейку (обработка объединенных ячеек)
    def write_to_cell(cell_ref: str, value):
        """Безопасная запись в ячейку, даже если она объединена"""
        try:
            cell = ws[cell_ref]
            # Если ячейка объединена, найдём базовую ячейку
            for merged_range in ws.merged_cells.ranges:
                if cell.coordinate in merged_range:
                    # Записываем в первую ячейку диапазона
                    top_left_cell = ws.cell(merged_range.min_row, merged_range.min_col)
                    top_left_cell.value = value
                    return
            # Если не объединена, пишем напрямую
            cell.value = value
        except Exception as e:
            logger.warning(f"Не удалось записать в ячейку {cell_ref}: {e}")
    
    # Заполняем основные поля
    write_to_cell("B5", application_data.get("sport_type", ""))  # Вид спорта
    write_to_cell("B7", application_data.get("event_rank", ""))  # Ранг мероприятия
    write_to_cell("I5", application_data.get("city", ""))  # Город
    write_to_cell("I7", application_data.get("country", ""))  # Страна
    
    # Заполняем участников
    participants: List[Dict] = application_data.get("participants", [])
    
    for idx, participant in enumerate(participants):
        # Определяем, в какую колонку писать (1-15 или 16-30)
        if idx < 15:
            # Первая колонка (строки 10-24)
            row = 10 + idx
            write_to_cell(f"B{row}", participant.get("full_name", ""))
            write_to_cell(f"D{row}", participant.get("date_from", ""))
            write_to_cell(f"E{row}", participant.get("date_to", ""))
        else:
            # Вторая колонка (строки 10-24)
            row = 10 + (idx - 15)
            write_to_cell(f"G{row}", participant.get("full_name", ""))
            write_to_cell(f"I{row}", participant.get("date_from", ""))
            write_to_cell(f"J{row}", participant.get("date_to", ""))
    
    # Сохраняем файл
    wb.save(output_path)
    wb.close()
    
    logger.info(f"Excel файл успешно создан: {output_path}")
    return output_path
