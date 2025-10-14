
"""
Тесты для бота
"""
import pytest
from bot.utils.validators import validate_date, validate_date_range, validate_full_name, validate_text


class TestValidators:
    """Тесты валидаторов"""
    
    def test_validate_date_valid(self):
        """Тест валидации корректной даты"""
        is_valid, msg = validate_date("25.12.2024")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_date_invalid_format(self):
        """Тест валидации некорректного формата даты"""
        is_valid, msg = validate_date("25/12/2024")
        assert is_valid is False
        assert "формат" in msg.lower()
    
    def test_validate_date_invalid_date(self):
        """Тест валидации несуществующей даты"""
        is_valid, msg = validate_date("32.13.2024")
        assert is_valid is False
        assert "некорректная" in msg.lower()
    
    def test_validate_date_range_valid(self):
        """Тест валидации корректного диапазона дат"""
        is_valid, msg = validate_date_range("25.12.2024", "31.12.2024")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_date_range_invalid(self):
        """Тест валидации некорректного диапазона дат (окончание раньше начала)"""
        is_valid, msg = validate_date_range("31.12.2024", "25.12.2024")
        assert is_valid is False
        assert "раньше" in msg.lower()
    
    def test_validate_full_name_valid(self):
        """Тест валидации корректного ФИО"""
        is_valid, msg = validate_full_name("Иванов Иван Иванович")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_full_name_two_words(self):
        """Тест валидации ФИО из двух слов"""
        is_valid, msg = validate_full_name("Иванов Иван")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_full_name_invalid(self):
        """Тест валидации некорректного ФИО (одно слово)"""
        is_valid, msg = validate_full_name("Иванов")
        assert is_valid is False
        assert "минимум" in msg.lower()
    
    def test_validate_full_name_empty(self):
        """Тест валидации пустого ФИО"""
        is_valid, msg = validate_full_name("")
        assert is_valid is False
        assert "пустым" in msg.lower()
    
    def test_validate_text_valid(self):
        """Тест валидации корректного текста"""
        is_valid, msg = validate_text("Футбол", min_length=2, max_length=50)
        assert is_valid is True
        assert msg == ""
    
    def test_validate_text_too_short(self):
        """Тест валидации слишком короткого текста"""
        is_valid, msg = validate_text("А", min_length=2)
        assert is_valid is False
        assert "минимум" in msg.lower()
    
    def test_validate_text_too_long(self):
        """Тест валидации слишком длинного текста"""
        is_valid, msg = validate_text("А" * 100, max_length=50)
        assert is_valid is False
        assert "превышать" in msg.lower()
    
    def test_validate_text_empty(self):
        """Тест валидации пустого текста"""
        is_valid, msg = validate_text("")
        assert is_valid is False
        assert "пустым" in msg.lower()


class TestApplication:
    """Тесты функционала заявок"""
    
    # TODO: Добавить интеграционные тесты для проверки:
    # - Регистрации и одобрения пользователя
    # - Создания заявки с несколькими участниками
    # - Генерации Excel файла
    # - Отправки email и Telegram сообщений
    # - Работы с черновиками
    
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
