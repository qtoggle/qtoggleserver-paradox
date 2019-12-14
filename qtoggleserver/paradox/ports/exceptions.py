
class PAIException(Exception):
    pass


class PAIConnectError(PAIException):
    def __init__(self):
        super().__init__('unable to connect to panel')


class PAICommandError(PAIException):
    pass


class PAITimeout(PAIException):
    pass
