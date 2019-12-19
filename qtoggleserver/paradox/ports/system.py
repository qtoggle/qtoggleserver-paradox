
from abc import ABCMeta

from .base import PAIPort


class SystemPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, address, peripheral_name=None):
        super().__init__(address, peripheral_name=peripheral_name)

    def make_id(self):
        return 'system.{}'.format(self.ID)

    def get_property(self, name):
        return self.get_peripheral().get_property('system', None, name)

    def get_properties(self):
        return self.get_peripheral().get_properties('system', None)


class SystemTroublePort(SystemPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'trouble'

    async def read_value(self):
        return self.get_property('trouble')
