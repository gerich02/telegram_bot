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


class MissTokenError(Exception):
    """Отсутстсвует один или более токен."""

    pass


class MissHomeworkInfoError(Exception):
    """Данные о домашних зданиях отсутствуют в ответе от API."""

    pass
