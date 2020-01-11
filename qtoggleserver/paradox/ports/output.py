
from abc import ABCMeta
from typing import Dict, Optional

from .base import PAIPort
from .typing import Property


class OutputPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, output: int, address: str, peripheral_name: Optional[str] = None) -> None:
        self.output: int = output

        super().__init__(address, peripheral_name=peripheral_name)

    def make_id(self) -> str:
        return f'output{self.output}.{self.ID}'

    def get_output_label(self) -> str:
        return self.get_property('label') or f'Output {self.output}'

    def get_property(self, name: str) -> Property:
        return self.get_peripheral().get_property('pgm', self.output, name)

    def get_properties(self) -> Dict[str, Property]:
        return self.get_peripheral().get_properties('pgm', self.output)


class OutputTroublePort(OutputPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'trouble'

    async def attr_get_default_display_name(self) -> str:
        return f'{self.get_output_label()} Trouble'

    async def read_value(self) -> bool:
        for name, value in self.get_properties().items():
            if name.endswith('_trouble') and value:
                return True

        return False


class OutputTamperPort(OutputPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'tamper'

    async def attr_get_default_display_name(self) -> str:
        return f'{self.get_output_label()} Tamper'

    async def read_value(self) -> Optional[bool]:
        return self.get_property('tamper')
