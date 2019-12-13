
from abc import ABCMeta

from . import constants
from .base import PAIPort


class OutputPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, output, serial_port, serial_baud=constants.DEFAULT_SERIAL_BAUD, peripheral_name=None):
        self.output = output

        super().__init__(serial_port, serial_baud, peripheral_name=peripheral_name)

    def make_id(self):
        return 'output{}.{}'.format(self.output, self.ID)

    def get_output_label(self):
        return self.get_peripheral().get_property('pgm', self.output, 'label') or 'Output {}'.format(self.output)


class OutputTamperPort(OutputPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'tamper'

    async def attr_get_default_display_name(self):
        return '{} Tamper'.format(self.get_output_label())

    async def read_value(self):
        peripheral = self.get_peripheral()
        return peripheral.get_property('pgm', self.output, 'tamper')
