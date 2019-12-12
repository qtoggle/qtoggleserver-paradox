
import asyncio

from abc import ABCMeta

from . import constants
from . import exceptions
from .base import PAIPort


class AreaPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, area, serial_port, serial_baud=constants.DEFAULT_SERIAL_BAUD, peripheral_name=None):
        self.area = area

        super().__init__(serial_port, serial_baud, peripheral_name=peripheral_name)

    def make_id(self):
        return 'area{}.{}'.format(self.area, self.ID)

    def get_area_label(self):
        return self.get_peripheral().get_property('partition', self.area, 'label') or 'Area {}'.format(self.area)


class AreaArmedPort(AreaPort):
    TYPE = 'number'
    WRITABLE = True
    CHOICES = [
        {'value': 0, 'display_name': 'Disarmed'},
        {'value': 1, 'display_name': 'Armed'},
        {'value': 2, 'display_name': 'Armed (Sleep)'},
        {'value': 3, 'display_name': 'Armed (Stay)'}
    ]

    ID = 'armed'

    _ARMED_STATE_MAPPING = {
        'disarmed': 0,
        'armed_away': 1,
        'armed_night': 2,
        'armed_home': 3,
        0: 'disarmed',
        1: 'armed_away',
        2: 'armed_night',
        3: 'armed_home',
    }

    _ARMED_MODE_MAPPING = {
        0: constants.ARMED_MODE_DISARMED,
        1: constants.ARMED_MODE_ARMED,
        2: constants.ARMED_MODE_ARMED_SLEEP,
        3: constants.ARMED_MODE_ARMED_STAY
    }

    async def attr_get_default_display_name(self):
        return '{} Armed'.format(self.get_area_label())

    async def read_value(self):
        peripheral = self.get_peripheral()
        armed_state = peripheral.get_property('partition', self.area, 'current_state')
        if armed_state == 'pending':
            return None

        return self._ARMED_STATE_MAPPING.get(armed_state)

    async def _wait_armed_state(self, armed_state):
        peripheral = self.get_peripheral()
        while peripheral.get_property('partition', self.area, 'current_state') != armed_state:
            await asyncio.sleep(0.5)

    async def write_value(self, value):
        await self.get_peripheral().set_area_armed_mode(self.area, self._ARMED_MODE_MAPPING[value])
        try:
            await asyncio.wait_for(self._wait_armed_state(self._ARMED_STATE_MAPPING[value]), timeout=self.CMD_TIMEOUT)

        except asyncio.TimeoutError:
            raise exceptions.PAITimeout('timeout waiting for armed state')


class AreaAlarmPort(AreaPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'alarm'

    async def attr_get_default_display_name(self):
        return '{} Alarm'.format(self.get_area_label())

    async def read_value(self):
        peripheral = self.get_peripheral()
        return peripheral.get_property('partition', self.area, 'alarm')
