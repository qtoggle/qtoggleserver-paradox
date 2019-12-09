
from abc import ABCMeta

from . import constants
from .base import PAIPort


class ZonePort(PAIPort, metaclass=ABCMeta):
    def __init__(self, zone, serial_port, serial_baud=constants.DEFAULT_SERIAL_BAUD, peripheral_name=None):
        self.zone = zone

        super().__init__(serial_port, serial_baud, peripheral_name=peripheral_name)

    def make_id(self):
        return 'zone{}.{}'.format(self.zone, self.ID)

    def get_zone_label(self):
        return self.get_peripheral().get_property('zone', self.zone, 'label') or 'Zone {}'.format(self.zone)


class OpenZonePort(ZonePort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'open'

    async def attr_get_default_display_name(self):
        return '{} Open'.format(self.get_zone_label())

    async def read_value(self):
        peripheral = self.get_peripheral()
        return peripheral.get_property('zone', self.zone, 'open')
