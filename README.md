#  Описание проекта "telegram_bot.git"

## Описание
Telegram-bot который взаимодействует с API сервиса. В его обязанности входит:
- раз в 10 минут опрашивать API сервиса и проверять статус отправленной домашней;
- при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
- логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

**Инструменты и стек:** #Python #python-telegram-bot 

## Запуск
Этот проект настроен на работу с определенным API, для его запуска Вам потребуется зарегистрировать 
бота в Telegram, получить токен для бота, Telegram ID и токен от API сервиса по [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).

## Установка проекта

1. Клонируйте репозиторий:
    ```
    git clone git@github.com:gerich02/telegram_bot.git
    ```
2. Перейдите в папку с проектом:
    ```
    cd telegram_bot
    ```
3. Установите зависимости из файла requirements.txt:
    ```
    pip install -r requirements.txt
    ```
4. Создайте файл .env и заполните его своими данными:
    ```bash
    TELEGRAM_TOKEN= 5445863218:YGVBnkJHBjbkJbKjbyuBjkklJggJIKyugyS                        #Токен, получаемый при регистрации телеграм бота.
    PRACTICUM_TOKEN= y0_HHHghbhyuHBtPMklkmSKLYHGVbkbhtgFtFyuft56UJygvvJvghjGVHVGhgv       #Токен, получаемый при переходе по ссылке API сервиса.
    TELEGRAM_CHAT_ID= 844593658                                                           #Ваш telegram ID.
    ```
5. Выполните команду:
    ```
    python bot.py
    ```

## Об авторе
>[Gerich02](https://github.com/gerich02).
