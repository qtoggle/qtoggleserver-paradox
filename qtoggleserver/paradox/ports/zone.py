
from abc import ABCMeta

from .base import PAIPort


class ZonePort(PAIPort, metaclass=ABCMeta):
    def __init__(self, zone, address, peripheral_name=None):
        self.zone = zone

        super().__init__(address, peripheral_name=peripheral_name)

    def make_id(self):
        return 'zone{}.{}'.format(self.zone, self.ID)

    def get_zone_label(self):
        return self.get_property('label') or 'Zone {}'.format(self.zone)

    def get_property(self, name):
        return self.get_peripheral().get_property('zone', self.zone, name)

    def get_properties(self):
        return self.get_peripheral().get_properties('zone', self.zone)


class ZoneOpenPort(ZonePort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'open'

    async def attr_get_default_display_name(self):
        return '{} Open'.format(self.get_zone_label())

    async def read_value(self):
        return self.get_property('open')


class ZoneAlarmPort(ZonePort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'alarm'

    async def attr_get_default_display_name(self):
        return '{} Alarm'.format(self.get_zone_label())

    async def read_value(self):
        return self.get_property('alarm')


class ZoneTroublePort(ZonePort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'trouble'

    async def attr_get_default_display_name(self):
        return '{} Trouble'.format(self.get_zone_label())

    async def read_value(self):
        for name, value in self.get_properties().items():
            if name.endswith('_trouble') and value:
                return True

        return False


class ZoneTamperPort(ZonePort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'tamper'

    async def attr_get_default_display_name(self):
        return '{} Tamper'.format(self.get_zone_label())

    async def read_value(self):
        return self.get_property('tamper')
