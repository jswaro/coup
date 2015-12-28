

class CoupException(Exception):
    pass


class MalformedCLICommand(CoupException):
    pass


class InvalidCLICommand(CoupException):
    pass


class GameNotFoundException(CoupException):
    pass


class GamePermissionError(CoupException):
    pass


class GameInvalidOperation(CoupException):
    pass
