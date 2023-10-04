import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    ApiRequestError, ExpectedDataError,
    ResponseKeyError, ResponseCodeError
)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
sh.setFormatter(formatter)
logger.addHandler(sh)


def check_tokens():
    """Проверка наличия токенов."""
    logger.debug('Проверка переменных глобального окружения')
    if not PRACTICUM_TOKEN:
        logger.critical('Нет токена PRACTICUM_TOKEN')
    if not TELEGRAM_TOKEN:
        logger.critical('Нет токена TELEGRAM_TOKEN')
    if not TELEGRAM_CHAT_ID:
        logger.critical('Нет токена TELEGRAM_CHAT_ID')
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        logger.debug('Все токены успешно получены')
        return None
    logger.critical('Приостанавливаем программу')
    sys.exit('Не найден токен')


def send_message(bot, message):
    """Отправка сообщений ботом в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Бот удачно отправил сообщение об изменении статуса ДЗ')
    except telegram.error.TelegramError:
        logger.error('Сбой при отправке сообщения')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        logger.debug('Отправка запроса к API.')
    except requests.RequestException as error:
        logger.error(f'Ошибка при выполнении запроса к API: {error}')
        raise ApiRequestError(f'Ошибка при выполнении запроса к API: {error}')
    if response.status_code != 200:
        logger.error(
            f'не получен ожидаемый ответ от API. Статус {response.status_code}'
        )
        raise ResponseCodeError(
            f'не получен ожидаемый ответ от API. Статус {response.status_code}'
        )
    else:
        response = response.json()
        logger.debug('Ответ получен и  преобразован к типу данных Python')
        return response


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        logger.error('Данные получены не в виде словаря')
        raise TypeError
    if 'homeworks' not in response:
        logger.error('Нет ключа homeworks')
        raise KeyError
    if not isinstance(response['homeworks'], list):
        logger.error('Данные переданы не в виде списка')
        raise TypeError
    if not response.get('homeworks'):
        raise IndexError('Список работ пуст')
    return response.get('homeworks')[0]


def parse_status(homework):
    """Проверяет статус и формирует сообщение о статусе ДЗ."""
    if 'homework_name' not in homework:
        raise ResponseKeyError('В ответе API отсутствует имя ключа')
    else:
        homework_name = homework.get('homework_name')

    if homework.get('status') not in HOMEWORK_VERDICTS:
        logger.error(
            'Домашней работе присвоен "несуществующий"'
            f'статус {homework.get("status")}'
        )
        raise ExpectedDataError(
            'Домашней работе присвоен "несуществующий"'
            f' статус {homework.get("status")}'
        )
    else:
        verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
        logger.debug(
            'Данные прошли проверку.Формируется ответ для пользователя.'
        )
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.debug('БОТ начинает работу.')
    check_tokens()
    status = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = time.time() - RETRY_PERIOD
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework.get('status') == status:
                logger.debug(
                    'Статус домашнего задания не изменился,'
                    'информирование не требуется.'
                )
            else:
                message = parse_status(homework)
                send_message(bot, message)
                status = homework.get('status')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
