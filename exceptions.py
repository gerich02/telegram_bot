"""Хранилище для пользовательских исключений."""


class TokenError(Exception):
    """Ошибка наличия токена."""

    pass


class ApiRequestError(Exception):
    """Ошибка запроса к API."""

    pass


class ResponseCodeError(Exception):
    """Статус ответа не соответствует ожидаемому(200)."""

    pass


class ResponseKeyError(Exception):
    """В ответе отсутствует ожидаемый ключ."""

    pass


class ExpectedDataError(Exception):
    """Данные в ответе не соответствуют ожидаемым."""

    pass
