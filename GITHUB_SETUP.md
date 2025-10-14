# Инструкция по созданию GitHub репозитория

## Создание репозитория на GitHub

1. **Откройте GitHub** и войдите в свой аккаунт

2. **Создайте новый репозиторий:**
   - Перейдите на https://github.com/new
   - Название репозитория: `telegram-travel-bot`
   - Описание: `Telegram bot for travel application submissions`
   - Выберите Public или Private (по желанию)
   - **НЕ инициализируйте с README, .gitignore или лицензией** (они уже есть в проекте)
   - Нажмите "Create repository"

3. **Скопируйте URL репозитория** (будет показан на следующей странице)

## Загрузка кода в репозиторий

Код уже подготовлен в директории `/home/ubuntu/github_repos/telegram-travel-bot/`

### Вариант 1: Через HTTPS (рекомендуется)

```bash
cd /home/ubuntu/github_repos/telegram-travel-bot

# Добавьте удаленный репозиторий (замените YOUR_USERNAME на ваше имя пользователя)
git remote add origin https://github.com/YOUR_USERNAME/telegram-travel-bot.git

# Установите основную ветку
git branch -M main

# Загрузите код
git push -u origin main
```

При запросе логина и пароля:
- **Username**: ваше имя пользователя GitHub
- **Password**: используйте [Personal Access Token](https://github.com/settings/tokens) (НЕ пароль от аккаунта)

### Вариант 2: Через SSH (если настроен SSH ключ)

```bash
cd /home/ubuntu/github_repos/telegram-travel-bot

# Добавьте удаленный репозиторий
git remote add origin git@github.com:YOUR_USERNAME/telegram-travel-bot.git

# Установите основную ветку
git branch -M main

# Загрузите код
git push -u origin main
```

## Создание Personal Access Token (PAT)

Если у вас нет токена:

1. Перейдите в **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Нажмите **Generate new token** → **Generate new token (classic)**
3. Дайте токену имя: `telegram-travel-bot`
4. Выберите срок действия
5. Выберите права:
   - `repo` (полный доступ к репозиториям)
6. Нажмите **Generate token**
7. **Скопируйте токен** (он больше не будет показан!)

## Команда для загрузки с использованием токена

```bash
cd /home/ubuntu/github_repos/telegram-travel-bot

# Для sakharchukrv (замените на свое имя пользователя и токен)
git remote add origin https://YOUR_TOKEN@github.com/sakharchukrv/telegram-travel-bot.git
git branch -M main
git push -u origin main
```

## Проверка

После успешной загрузки:

1. Откройте ваш репозиторий на GitHub
2. Убедитесь, что все файлы загружены
3. README.md должен отображаться на главной странице

## Структура загруженного репозитория

```
telegram-travel-bot/
├── bot/                 # Код бота
├── templates/           # Шаблоны Excel
├── tests/              # Тесты
├── .env.example        # Пример конфигурации
├── .gitignore          # Игнорируемые файлы
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose
├── README.md           # Документация
└── requirements.txt    # Зависимости
```

## Готовые команды для sakharchukrv

```bash
# Получите токен из GitHub Settings
export GITHUB_TOKEN="ваш_токен_здесь"

# Загрузите код
cd /home/ubuntu/github_repos/telegram-travel-bot
git remote add origin https://${GITHUB_TOKEN}@github.com/sakharchukrv/telegram-travel-bot.git
git branch -M main
git push -u origin main
```

После загрузки репозиторий будет доступен по адресу:
**https://github.com/sakharchukrv/telegram-travel-bot**
