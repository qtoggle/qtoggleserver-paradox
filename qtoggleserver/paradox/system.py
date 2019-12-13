
from abc import ABCMeta

from .base import PAIPort


class SystemPort(PAIPort, metaclass=ABCMeta):
    ID = 'system'


class SystemTroublePort(SystemPort):
    TYPE = 'boolean'
    WRITABLE = False

    async def read_value(self):
        peripheral = self.get_peripheral()
        return peripheral.get_property('system', None, 'trouble')
