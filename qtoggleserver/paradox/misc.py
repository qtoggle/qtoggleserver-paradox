from abc import ABCMeta

from .paradoxport import ParadoxPort


class NowAlarmZone(ParadoxPort, metaclass=ABCMeta):
    TYPE = "number"
    WRITABLE = False
    ID = "now_alarm_zone"

    async def attr_get_default_display_name(self) -> str:
        return "Now In Alarm Zone"

    async def read_value(self) -> int:
        paradox_alarm = self.get_peripheral()
        for zone in paradox_alarm.get_zones():
            if paradox_alarm.get_property("zone", 1, "alarm"):
                return zone

        return 0


class WasAlarmZone(ParadoxPort, metaclass=ABCMeta):
    TYPE = "number"
    WRITABLE = False
    ID = "was_alarm_zone"

    async def attr_get_default_display_name(self) -> str:
        return "Was In Alarm Zone"

    async def read_value(self) -> int:
        paradox_alarm = self.get_peripheral()
        for zone in paradox_alarm.get_zones():
            if paradox_alarm.get_property("zone", zone, "was_in_alarm"):
                return zone

        return 0
