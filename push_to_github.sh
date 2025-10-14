#!/bin/bash

# Скрипт для автоматического подключения и push в GitHub
# После создания репозитория на GitHub запустите этот скрипт

set -e

echo "🚀 Подключение проекта к GitHub репозиторию..."
echo ""

REPO_NAME="telegram-travel-bot"
GITHUB_USER="sakharchukrv"
GITHUB_TOKEN="ghu_0WQ9TbZ1PjWVzlZRH7cbi55lKH0p5f2kejSO"

# Переход в директорию проекта
cd /home/ubuntu/github_repos/telegram-travel-bot

# Проверка, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: это не git репозиторий"
    exit 1
fi

# Проверка текущей ветки
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 Текущая ветка: $CURRENT_BRANCH"

# Проверка статуса
echo ""
echo "📊 Статус git:"
git status

# Удаление старого remote (если есть)
if git remote | grep -q "origin"; then
    echo ""
    echo "🗑️  Удаление старого remote 'origin'..."
    git remote remove origin
fi

# Добавление нового remote с токеном
echo ""
echo "🔗 Добавление remote репозитория..."
git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

# Проверка remote
echo ""
echo "✅ Remote репозиторий добавлен:"
git remote -v | sed "s/${GITHUB_TOKEN}/***TOKEN***/g"

# Push в GitHub
echo ""
echo "⬆️  Отправка кода в GitHub..."
git push -u origin "$CURRENT_BRANCH"

# Финальная проверка
echo ""
echo "✅ Успешно! Код отправлен в GitHub!"
echo ""
echo "🔗 Репозиторий доступен по адресу:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "📚 Для клонирования используйте:"
echo "   git clone https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
echo ""
