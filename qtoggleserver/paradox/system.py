
from abc import ABCMeta
from typing import Dict, Optional

from .paradoxport import ParadoxPort
from .typing import Property


class SystemPort(ParadoxPort, metaclass=ABCMeta):
    def make_id(self) -> str:
        return f'system.{self.ID}'

    def get_property(self, name: str) -> Property:
        return self.get_peripheral().get_property('system', None, name)

    def get_properties(self) -> Dict[str, Property]:
        return self.get_peripheral().get_properties('system', None)


class SystemTroublePort(SystemPort):
    TYPE = 'boolean'
    WRITABLE = False
    DISPLAY_NAME = 'System Trouble'

    ID = 'trouble'

    async def read_value(self) -> Optional[bool]:
        return self.get_property('trouble')
