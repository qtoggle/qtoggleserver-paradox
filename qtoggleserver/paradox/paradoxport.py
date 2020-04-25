
import abc

from typing import cast, Optional

from qtoggleserver.peripherals import PeripheralPort
from qtoggleserver.utils import conf as conf_utils

from .paradoxalarm import ParadoxAlarm
from .typing import Property


class ParadoxPort(PeripheralPort, conf_utils.ConfigurableMixin, metaclass=abc.ABCMeta):
    CMD_TIMEOUT = 60

    def on_property_change(
        self,
        _type: str,
        _id: Optional[str],
        _property: str,
        old_value: Property,
        new_value: Property
    ) -> None:

        pass

    def get_peripheral(self) -> ParadoxAlarm:
        return cast(ParadoxAlarm, super().get_peripheral())
