
from abc import ABCMeta
from typing import Dict, Optional

from .base import PAIPort
from .typing import Property


class SystemPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, address: str, peripheral_name: Optional[str] = None) -> None:
        super().__init__(address, peripheral_name=peripheral_name)

    def make_id(self) -> str:
        return f'system.{self.ID}'

    def get_property(self, name: str) -> Property:
        return self.get_peripheral().get_property('system', None, name)

    def get_properties(self) -> Dict[str, Property]:
        return self.get_peripheral().get_properties('system', None)


class SystemTroublePort(SystemPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'trouble'

    async def read_value(self) -> Optional[bool]:
        return self.get_property('trouble')
