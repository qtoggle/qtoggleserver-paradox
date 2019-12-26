
from abc import ABCMeta

from . import constants
from .base import PAIPort


class AreaPort(PAIPort, metaclass=ABCMeta):
    def __init__(self, area, address, peripheral_name=None):
        self.area = area

        super().__init__(address, peripheral_name=peripheral_name)

    def make_id(self):
        return 'area{}.{}'.format(self.area, self.ID)

    def get_area_label(self):
        return self.get_property('label') or 'Area {}'.format(self.area)

    def get_property(self, name):
        return self.get_peripheral().get_property('partition', self.area, name)

    def get_properties(self):
        return self.get_peripheral().get_properties('partition', self.area)


class AreaArmedPort(AreaPort):
    TYPE = 'number'
    WRITABLE = True
    CHOICES = [
        {'value': 1, 'display_name': 'Disarmed'},
        {'value': 2, 'display_name': 'Armed'},
        {'value': 3, 'display_name': 'Armed (Sleep)'},
        {'value': 4, 'display_name': 'Armed (Stay)'}
    ]

    ID = 'armed'

    _DEFAULT_STATE = 'disarmed'

    _ARMED_STATE_MAPPING = {
        'disarmed': 1,
        'armed_away': 2,
        'armed_night': 3,
        'armed_home': 4,
        1: 'disarmed',
        2: 'armed_away',
        3: 'armed_night',
        4: 'armed_home',
    }

    _OPPOSITE_ARMED_STATE_MAPPING = {
        'disarmed': 'armed_away',
        'armed_away': 'disarmed',
        'armed_night': 'disarmed',
        'armed_home': 'disarmed'
    }

    _ARMED_MODE_MAPPING = {
        1: constants.ARMED_MODE_DISARMED,
        2: constants.ARMED_MODE_ARMED,
        3: constants.ARMED_MODE_ARMED_SLEEP,
        4: constants.ARMED_MODE_ARMED_STAY
    }

    def __init__(self, area, address, peripheral_name=None):
        super().__init__(area, address, peripheral_name)

        self._requested_value = None  # Used to cache written value while pending
        self._last_state = self.get_property('current_state') or self._DEFAULT_STATE
        self._pending = False

    async def attr_get_default_display_name(self):
        return '{} Armed'.format(self.get_area_label())

    async def read_value(self):
        current_state = self.get_property('current_state')
        last_state = self._last_state

        if current_state == last_state:
            return

        self._last_state = current_state
        self.debug('current state is now %s', current_state)

        if current_state == 'pending':
            if self._requested_value is not None:
                if not self._pending:
                    self.debug('state %s is pending', self._ARMED_STATE_MAPPING[self._requested_value])
                    self._pending = True

                return -self._requested_value

            else:
                # If state becomes pending but we don't have a requested value, it's probably arming/disarming via some
                # other external means. The best we can do is to indicate the opposite state as pending.
                opposite_state = self._OPPOSITE_ARMED_STATE_MAPPING[last_state]
                return -self._ARMED_STATE_MAPPING[opposite_state]

        else:
            if self._pending:
                # Reset requested value when pending request is fulfilled
                self.debug('state %s fulfilled', self._ARMED_STATE_MAPPING[self._requested_value])
                self._pending = False
                self._requested_value = None

            return self._ARMED_STATE_MAPPING.get(current_state)

    async def write_value(self, value):
        await self.get_peripheral().set_area_armed_mode(self.area, self._ARMED_MODE_MAPPING[value])
        self._requested_value = value
        self._last_state = self._ARMED_STATE_MAPPING[value]


class AreaAlarmPort(AreaPort):
    TYPE = 'boolean'
    WRITABLE = False

    ID = 'alarm'

    async def attr_get_default_display_name(self):
        return '{} Alarm'.format(self.get_area_label())

    async def read_value(self):
        return self.get_property('alarm')
