# Инструкция по загрузке проекта на GitHub

## Шаг 1: Создание репозитория на GitHub

1. **Перейдите на страницу создания репозитория**: https://github.com/new
2. **Авторизуйтесь** в своем аккаунте GitHub (sakharchukrv)
3. **Заполните форму создания репозитория**:
   - **Repository name**: `telegram-travel-bot`
   - **Description**: `Telegram-бот для автоматизации процесса подачи заявок на служебные поездки`
   - **Visibility**: выберите `Public` (публичный) или `Private` (приватный) по желанию
   - **НЕ СТАВЬТЕ ГАЛОЧКУ** "Initialize this repository with a README" (не инициализировать с README)
   - Нажмите кнопку **"Create repository"**

## Шаг 2: Подключение удаленного репозитория и push

После создания репозитория на GitHub, выполните следующие команды:

### Вариант А: Используя токен (рекомендуется)

```bash
cd /home/ubuntu/github_repos/telegram-travel-bot

# Добавить удаленный репозиторий с токеном
git remote add origin https://ghu_0WQ9TbZ1PjWVzlZRH7cbi55lKH0p5f2kejSO@github.com/sakharchukrv/telegram-travel-bot.git

# Отправить код на GitHub
git push -u origin master

# Проверить результат
git remote -v
```

### Вариант Б: Используя SSH (если настроен SSH ключ)

```bash
cd /home/ubuntu/github_repos/telegram-travel-bot

# Добавить удаленный репозиторий через SSH
git remote add origin git@github.com:sakharchukrv/telegram-travel-bot.git

# Отправить код на GitHub
git push -u origin master

# Проверить результат
git remote -v
```

## Шаг 3: Проверка

После успешного push, ваш репозиторий будет доступен по адресу:
**https://github.com/sakharchukrv/telegram-travel-bot**

## Что уже готово в проекте:

✅ **Весь код бота** - структура проекта, handlers, database, utils  
✅ **Конфигурация Docker** - Dockerfile и docker-compose.yml  
✅ **Документация** - README.md, DEPLOYMENT.md, DEMO.md  
✅ **Шаблон Excel** - файл для генерации заявок  
✅ **Зависимости** - requirements.txt  
✅ **Тесты** - базовая структура тестов  
✅ **.gitignore** - правильно настроен для исключения:
   - .env файлов (токены, пароли)
   - __pycache__
   - виртуальных окружений
   - баз данных
   - логов
   - сгенерированных файлов

## Безопасность

🔒 **Конфиденциальные данные НЕ попадут в репозиторий:**
- `.env` файл исключен из git
- Токены, пароли и секреты защищены
- В репозитории есть `.env.example` как шаблон для настройки

## Дополнительно: Файл .env.example

В проекте уже есть файл `.env.example`, который содержит шаблон для настройки переменных окружения:

```bash
# Просмотр шаблона
cat .env.example
```

Пользователи, которые будут клонировать репозиторий, должны:
1. Скопировать `.env.example` в `.env`
2. Заполнить свои реальные значения токенов и паролей

## История коммитов

```
742466f Добавлена документация: GitHub setup, Deployment guide, Demo
345cfff Initial commit: Telegram Travel Bot v1.0
```

## Структура проекта

```
telegram-travel-bot/
├── bot/                      # Основной код бота
│   ├── main.py              # Точка входа
│   ├── config.py            # Конфигурация
│   ├── database/            # БД (models, database)
│   ├── handlers/            # Обработчики команд
│   ├── states/              # FSM состояния
│   ├── utils/               # Утилиты (Excel, Email, Telegram)
│   └── keyboards/           # Клавиатуры UI
├── templates/               # Шаблоны Excel
├── tests/                   # Тесты
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose
├── requirements.txt        # Python зависимости
├── README.md               # Основная документация
├── DEPLOYMENT.md           # Инструкция по деплою
├── DEMO.md                 # Демо и примеры использования
├── .gitignore              # Исключения для git
└── .env.example            # Шаблон переменных окружения
```

## Помощь

Если возникнут проблемы:

1. **Ошибка при push**: убедитесь, что репозиторий создан пустым (без README)
2. **Проблемы с авторизацией**: используйте токен доступа (вариант А)
3. **Репозиторий уже существует**: удалите старый или используйте другое имя

## GitHub App Access

⚠️ **Важно**: Для доступа к приватным репозиториям нашему боту необходимо предоставить доступ к [GitHub App](https://github.com/apps/abacusai/installations/select_target).

---

**Готово к использованию!** 🚀
