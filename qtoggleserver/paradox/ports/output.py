
from abc import ABCMeta

from .base import PAIPort


class OutputPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, output, address, peripheral_name=None):
        self.output = output

        super().__init__(address, peripheral_name=peripheral_name)

    def make_id(self):
        return 'output{}.{}'.format(self.output, self.ID)

    def get_output_label(self):
        return self.get_property('label') or 'Output {}'.format(self.output)

    def get_property(self, name):
        return self.get_peripheral().get_property('pgm', self.output, name)

    def get_properties(self):
        return self.get_peripheral().get_properties('pgm', self.output)


class OutputTroublePort(OutputPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'trouble'

    async def attr_get_default_display_name(self):
        return '{} Trouble'.format(self.get_output_label())

    async def read_value(self):
        for name, value in self.get_properties().items():
            if name.endswith('_trouble') and value:
                return True

        return False


class OutputTamperPort(OutputPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'tamper'

    async def attr_get_default_display_name(self):
        return '{} Tamper'.format(self.get_output_label())

    async def read_value(self):
        return self.get_property('tamper')
