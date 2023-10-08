import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    ApiRequestError, ExpectedDataError,
    ResponseKeyError, ResponseCodeError,
    MissTokenError, MissHomeworkInfoError
)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOKEN_NAME_LIST = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']

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
fh = logging.FileHandler('homework_bot.log', encoding='utf-8')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(fh)


def check_tokens():
    """Проверка наличия токенов."""
    for token in TOKEN_NAME_LIST:
        if not globals()[token]:
            logger.critical(f'Отсутствует токен {token}')
            logger.critical('Приостанавливаем программу')
            raise MissTokenError('Отсутствует один или более токен')
    logger.debug('Все токены успешно получены')


def send_message(bot, message):
    """Отправка сообщений ботом в телеграмм."""
    logger.debug('Попытка отправки сообщения об изменении статуса ДЗ')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Бот удачно отправил сообщение об изменении статуса ДЗ')
    except telegram.error.TelegramError:
        logger.error('Сбой при отправке сообщения')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    response_data = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        logger.debug(
            'Отправка запроса по адресу {url},'
            'данными заголовка {headers} и параметрами'
            '{params}.'.format(**response_data)
        )
        response = requests.get(**response_data)
    except requests.RequestException as error:
        raise ApiRequestError(f'Ошибка при выполнении запроса к API: {error}')
    if response.status_code != HTTPStatus.OK:
        raise ResponseCodeError(
            f'не получен ожидаемый ответ от API. Статус {response.status_code}'
        )
    response = response.json()
    logger.debug('Ответ получен и  преобразован к типу данных Python')
    return response


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Данные получены не в виде словаря')
    if 'homeworks' not in response:
        raise MissHomeworkInfoError(
            'Данные о домашних зданиях отсутствуют в ответе от API.'
        )
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Данные переданы не в виде списка')
    return homeworks


def parse_status(homework):
    """Проверяет статус и формирует сообщение о статусе ДЗ."""
    if 'homework_name' not in homework:
        raise ResponseKeyError('В ответе API отсутствует имя ключа')
    homework_name = homework.get('homework_name')
    if homework.get('status') not in HOMEWORK_VERDICTS:
        raise ExpectedDataError(
            'Домашней работе присвоен "несуществующий"'
            f' статус {homework.get("status")}'
        )
    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    logger.debug(
        'Данные прошли проверку.Формируется ответ для пользователя.'
    )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.debug('БОТ начинает работу.')
    check_tokens()
    old_status = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
            else:
                logger.debug('Список работ пуст')
                message = 'Новых статусов нет!'
            if message != old_status:
                send_message(bot, message)
                old_status = message
            else:
                logger.debug(
                    'Статус домашнего задания не изменился,'
                    'информирование не требуется.'
                )
        except MissHomeworkInfoError as error:
            logging.error(error)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != old_status:
                bot.send_message(bot, message)
                old_status = message
        finally:
            timestamp = response.get('current_date', timestamp)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()