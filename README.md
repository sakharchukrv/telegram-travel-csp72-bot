
# Telegram Travel Bot - Бот для подачи заявок на служебные поездки

Telegram-бот для автоматизации процесса подачи заявок на служебные поездки сотрудников спортивной организации.

## Возможности

- 🔐 **Система авторизации**: доступ только одобренным пользователям
- 📝 **Пошаговый сбор данных**: удобный диалог для заполнения заявки
- ✅ **Валидация данных**: проверка корректности введенных данных
- 💾 **Черновики**: сохранение и продолжение заполнения заявок
- 📋 **История заявок**: просмотр всех поданных заявок
- 📊 **Генерация Excel**: автоматическое заполнение шаблона заявки
- 📧 **Email уведомления**: отправка заявки на srv@cspto.ru
- 💬 **Telegram уведомления**: отправка в целевой чат
- 👨‍💼 **Админ-панель**: управление пользователями и заявками

## Структура проекта

```
telegram-travel-bot/
├── bot/                      # Основной код бота
│   ├── main.py              # Точка входа
│   ├── config.py            # Конфигурация
│   ├── database/            # Модели и работа с БД
│   ├── handlers/            # Обработчики команд и сообщений
│   ├── states/              # FSM состояния для диалогов
│   ├── utils/               # Утилиты (Excel, Email, Telegram)
│   └── keyboards/           # Клавиатуры для UI
├── templates/               # Шаблон Excel файла
├── tests/                   # Тесты
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose конфигурация
└── requirements.txt        # Зависимости Python
```

## Требования

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (для деплоя)

## Быстрый старт (локально)

### 1. Клонирование репозитория

```bash
git clone https://github.com/sakharchukrv/telegram-travel-bot.git
cd telegram-travel-bot
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
nano .env  # или любой другой редактор
```

**Обязательные переменные:**

- `TELEGRAM_BOT_TOKEN` - токен бота от @BotFather
- `TELEGRAM_ADMIN_IDS` - список ID администраторов через запятую
- `TARGET_CHAT_ID` - ID чата для отправки заявок
- `DATABASE_URL` - строка подключения к PostgreSQL
- `SMTP_USER` - email для отправки (mail.ru)
- `SMTP_PASSWORD` - пароль приложения mail.ru
- `EMAIL_TO_OVERRIDE` - email получателя заявок

### 5. Создание базы данных

```bash
# Создайте БД PostgreSQL
createdb travel_bot

# Примените миграции (после создания alembic)
alembic upgrade head
```

### 6. Запуск бота

```bash
python -m bot.main
```

## Деплой с Docker

### 1. Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируйте .env, установив DATABASE_URL=postgresql://postgres:postgres@db:5432/travel_bot
```

### 2. Запуск контейнеров

```bash
docker-compose up -d
```

### 3. Проверка логов

```bash
docker-compose logs -f bot
```

### 4. Остановка

```bash
docker-compose down
```

## Деплой на Timeweb

### Подготовка

1. Создайте сервер на Timeweb (Ubuntu 22.04 LTS)
2. Установите Docker и Docker Compose
3. Клонируйте репозиторий на сервер
4. Настройте `.env` файл

### Установка Docker на Timeweb

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose -y

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### Запуск бота на Timeweb

```bash
# Клонирование репозитория
git clone https://github.com/sakharchukrv/telegram-travel-bot.git
cd telegram-travel-bot

# Настройка переменных окружения
cp .env.example .env
nano .env

# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
```

### Автозапуск при перезагрузке

Docker Compose автоматически настроен на перезапуск контейнеров (`restart: unless-stopped`).

## Использование бота

### Для пользователей

1. **Старт**: `/start` - начало работы с ботом
2. **Ожидание одобрения**: администратор должен одобрить доступ
3. **Подача заявки**: после одобрения используйте кнопку "📝 Подать заявку"
4. **Заполнение формы**: следуйте инструкциям бота
5. **Черновики**: можно сохранить заявку и продолжить позже
6. **История**: просмотр всех поданных заявок

### Для администраторов

**Команды:**
- `/pending` - список пользователей, ожидающих одобрения
- `/users` - список всех пользователей
- `/approve <user_id>` - одобрить пользователя
- `/reject <user_id>` - отклонить пользователя
- `/revoke <user_id>` - отозвать доступ

## Структура заявки

Бот собирает следующие данные:
- Вид спорта
- Ранг спортивного мероприятия
- Страна назначения
- Город назначения
- Список участников (ФИО, даты поездки для каждого)

После подтверждения:
- Генерируется Excel файл по шаблону
- Отправляется email на srv@cspto.ru
- Отправляется сообщение в Telegram чат

## Настройка SMTP (mail.ru)

### Получение пароля приложения

1. Войдите в mail.ru
2. Настройки → Пароль и безопасность
3. Пароли для внешних приложений
4. Создайте новый пароль
5. Используйте этот пароль в `SMTP_PASSWORD`

### Настройки SMTP

- Host: `smtp.mail.ru`
- Port: `465` (SSL) или `587` (TLS)
- TLS: `true`

## Тестирование

```bash
# Запуск тестов
pytest tests/

# С покрытием
pytest tests/ --cov=bot
```

## Логирование

Логи сохраняются в:
- Консоль (stdout)
- Файл `logs/bot.log` (при наличии директории)

Уровень логирования настраивается через `LOG_LEVEL` в `.env`.

## Безопасность

- Все секреты хранятся в переменных окружения
- Доступ только одобренным пользователям
- Админ-панель только для администраторов
- Валидация всех входных данных

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f bot`
2. Проверьте переменные окружения в `.env`
3. Убедитесь, что PostgreSQL запущен
4. Проверьте доступ к SMTP серверу

## Лицензия

MIT License

## GitHub App Access

⚠️ **Важно**: Для доступа к приватным репозиториям необходимо предоставить доступ нашему [GitHub App](https://github.com/apps/abacusai/installations/select_target).
