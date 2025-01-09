# Анонимный Telegram-бот (Anonymous Telegram Bot)

Это анонимный Telegram-бот, предназначенный для создания тематических чатов между пользователями с учетом их предпочтений. Бот обеспечивает полуанонимное общение, требуя минимальную информацию для лучшего подбора собеседников. Он использует умную систему поиска собеседников на основе возраста, пола и интересов.

# 🛠 Функции

- **Умный поиск собеседников:**
  - Подбор по возрасту (±10 лет от вашего возраста)
  - Приоритетный подбор разнополых пар
  - Тематические комнаты для общения по интересам

- **Тематические комнаты:**
  - General (по умолчанию)
  - Movies (кино)
  - Books (книги)
  - Gaming (игры)
  - Music (музыка)
  - Photography (фотография)
  - Cooking (кулинария)
  - Politics (политика)

- **Поддержка всех типов медиа:**
  - Текстовые сообщения
  - Фотографии и альбомы
  - Видео и видеосообщения
  - Аудио и голосовые сообщения
  - Документы
  - Стикеры
  - GIF-анимации
  - Геолокация
  - Контакты
  - Опросы
  - Игральные кости (dice)
  - Места (venue)

- **Безопасность:**
  - Хеширование пользовательских данных
  - Сохранение настроек в зашифрованном виде

# ⚙️ Установка

### Требования
- Python 3.7 или выше
- pyTelegramBotAPI (Telebot)
- hashlib (для шифрования данных)
- json (для хранения настроек)

## Шаги установки
1. Клонируйте репозиторий:
```sh
git clone https://github.com/Kostik427/teleAnon.git
cd teleAnon
```

2. Установите зависимости:
```sh
pip install pyTelegramBotAPI
```

3. Настройте токен:
- Создайте файл .env и добавьте:
```
TELEGRAM_BOT_TOKEN=ваш_токен
```

4. Запустите бота:
```sh
python bot.py
```

# 🎯 Использование

### Первый запуск
1. Отправьте команду `/start`
2. Пройдите короткую настройку профиля:
   - Укажите ваш возраст (18-99)
   - Укажите ваш пол (M/W)
   - Выберите интересующую комнату

### Основные команды
- `/start` - Начать использование бота
- `/search` - Найти собеседника
- `/end` - Закончить текущий чат
- `/age` - Изменить возраст
- `/gender` - Изменить пол
- `/room` - Сменить комнату

# 🔄 Алгоритм подбора собеседников

Бот использует следующие критерии для подбора пар:
1. Обязательное совпадение по комнате
2. Возрастная разница не более 10 лет
3. Приоритет отдается разнополым парам
4. Однополые пары возможны с вероятностью 30%

# 🚀 Планируемые улучшения

- Время исчезновения сообщений
- Фильтрация нежелательного контента
- Рейтинговая система собеседников
- Черный список пользователей
- Дополнительные тематические комнаты
- Групповые чаты
- История диалогов (опционально)
- Автоматический перевод сообщений

# 🛠 Внесение изменений

1. Форкните репозиторий
2. Создайте ветку:
```sh
git checkout -b feature/ваша-идея
```
3. Зафиксируйте изменения:
```sh
git commit -m 'Добавлена новая функция'
```
4. Отправьте в ваш форк:
```sh
git push origin feature/ваша-идея
```
5. Создайте pull request

# 📜 Лицензия
Проект лицензирован под MIT License. Подробности в файле LICENSE.

# 💬 Обратная связь

Если у вас есть предложения по улучшению алгоритма подбора пар, идеи новых комнат или другие предложения, создайте issue в репозитории или свяжитесь с разработчиками напрямую.