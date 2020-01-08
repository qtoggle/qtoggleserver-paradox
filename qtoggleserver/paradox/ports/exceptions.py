
class PAIException(Exception):
    pass


class PAIConnectError(PAIException):
    def __init__(self) -> None:
        super().__init__('Unable to connect to panel')


class PAICommandError(PAIException):
    pass


class PAITimeout(PAIException):
    pass
