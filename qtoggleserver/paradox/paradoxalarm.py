
import asyncio
import logging

from typing import Any, cast, Dict, List, Optional, Union

from paradox.config import config
from paradox.lib import ps
from paradox.paradox import Paradox

from qtoggleserver.peripherals import Peripheral
from qtoggleserver.utils import json as json_utils

from . import constants
from . import exceptions
from .typing import Property


class ParadoxAlarm(Peripheral):
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        areas: List[int] = None,
        zones: List[int] = None,
        outputs: List[int] = None,
        serial_port: Optional[str] = None,
        serial_baud: int = constants.DEFAULT_SERIAL_BAUD,
        ip_host: Optional[str] = None,
        ip_port: int = constants.DEFAULT_IP_PORT,
        ip_password: str = constants.DEFAULT_IP_PASSWORD,
        **kwargs
    ) -> None:

        self.setup_config()
        self.setup_logging()

        self._areas = areas or []
        self._zones = zones or []
        self._outputs = outputs or []

        self._serial_port = serial_port
        self._serial_baud = serial_baud
        self._ip_host = ip_host
        self._ip_port = ip_port
        self._ip_password = ip_password

        self._paradox = None
        self._panel_task = None
        self._check_connection_task = asyncio.create_task(self._check_connection_loop())

        ps.subscribe(self.handle_paradox_property_change, 'changes')

        self._properties = {}

        super().__init__(**kwargs)

    @staticmethod
    def setup_config() -> None:
        config.CONFIG_LOADED = True
        for k, v in config.DEFAULTS.items():
            if isinstance(v, tuple):
                v = v[0]

            setattr(config, k, v)

    @staticmethod
    def setup_logging() -> None:
        logging.getLogger('PAI').setLevel(logging.ERROR)
        logging.getLogger('PAI.paradox.lib.async_message_manager').setLevel(logging.CRITICAL)

    def make_paradox(self) -> Paradox:
        if self._serial_port:
            config.CONNECTION_TYPE = 'Serial'
            config.SERIAL_PORT = self._serial_port
            config.SERIAL_BAUD = self._serial_baud

            self.debug('using serial connection on %s:%s', config.SERIAL_PORT, config.SERIAL_BAUD)

        else:  # IP connection, e.g. 192.168.1.2:10000:paradox
            config.CONNECTION_TYPE = 'IP'
            config.IP_CONNECTION_HOST = self._ip_host
            config.IP_CONNECTION_PORT = self._ip_port
            config.IP_CONNECTION_PASSWORD = self._ip_password.encode()

            self.debug('using IP connection on %s:%s', config.IP_CONNECTION_HOST, config.IP_CONNECTION_PORT)

        return Paradox()

    def parse_labels(self) -> None:
        for area in self._paradox.storage.data['partition'].values():
            self.debug('detected area id=%s, label=%s', area['id'], json_utils.dumps(area['label']))

        for zone in self._paradox.storage.data['zone'].values():
            self.debug('detected zone id=%s, label=%s', zone['id'], json_utils.dumps(zone['label']))

        for output in self._paradox.storage.data['pgm'].values():
            self.debug('detected output id=%s, label=%s', output['id'], json_utils.dumps(output['label']))

        for type_, entries in self._paradox.storage.data.items():
            for entry in entries.values():
                if 'label' in entry:
                    self._properties.setdefault(type_, {}).setdefault(entry['id'], {})['label'] = entry['label']

    async def connect(self) -> None:
        self.debug('connecting to panel')

        if not self._paradox:
            self._paradox = self.make_paradox()

        if not await self._paradox.connect():
            raise exceptions.ParadoxConnectError()

        self.debug('connected to panel')
        await self.handle_connected()

    async def make_port_args(self) -> List[Dict[str, Any]]:
        from .area import AreaAlarmPort, AreaArmedPort
        from .output import OutputTamperPort, OutputTroublePort
        from .zone import ZoneAlarmPort, ZoneOpenPort, ZoneTamperPort, ZoneTroublePort
        from .system import SystemTroublePort

        port_args = []
        port_args += [{'driver': AreaAlarmPort, 'area': area} for area in self._areas]
        port_args += [{'driver': AreaArmedPort, 'area': area} for area in self._areas]
        port_args += [{'driver': OutputTamperPort, 'output': output} for output in self._outputs]
        port_args += [{'driver': OutputTroublePort, 'output': output} for output in self._outputs]
        port_args += [{'driver': ZoneAlarmPort, 'zone': zone} for zone in self._zones]
        port_args += [{'driver': ZoneOpenPort, 'zone': zone} for zone in self._zones]
        port_args += [{'driver': ZoneTamperPort, 'zone': zone} for zone in self._zones]
        port_args += [{'driver': ZoneTroublePort, 'zone': zone} for zone in self._zones]
        port_args += [{'driver': SystemTroublePort}]

        return port_args

    async def handle_connected(self) -> None:
        self._panel_task = asyncio.create_task(self._paradox.loop())

        self.parse_labels()
        await self.trigger_port_update()

    async def disconnect(self) -> None:
        if self._panel_task is None:
            return

        self.debug('disconnecting')
        try:
            self._paradox.disconnect()

        except ConnectionError as e:
            # PAI may raise ConnectionError when disconnecting, so we catch it here and ignore it
            self.error('failed to disconnect from panel: %s', e, exc_info=True)

        self._paradox = None

        await self.trigger_port_update()

        try:
            await asyncio.wait_for(self._panel_task, timeout=10)

        except asyncio.TimeoutError:
            self.error('timeout waiting for panel task end')
            self._panel_task.cancel()

        else:
            self.debug('disconnected')

        self._panel_task = None

    async def _check_connection_loop(self) -> None:
        connect_succeeded = False

        try:
            while True:
                connected = (
                    self._paradox and
                    self._paradox.connection and
                    self._paradox.connection.connected and
                    connect_succeeded
                )

                self.set_online(connected)

                if self.is_enabled() and not connected:
                    try:
                        await self.connect()
                        connect_succeeded = True

                    except Exception as e:
                        self.error('failed to connect: %s', e, exc_info=True)

                elif not self.is_enabled() and connected:
                    connect_succeeded = False

                    try:
                        await self.disconnect()

                    except Exception as e:
                        self.error('failed to disconnect: %s', e, exc_info=True)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass

    async def handle_cleanup(self) -> None:
        await super().handle_cleanup()
        await self.disconnect()

    def handle_paradox_property_change(self, change: Any) -> None:
        from .paradoxport import ParadoxPort

        info = self._paradox.storage.data[change.type].get(change.key)
        if info and ('id' in info):
            id_ = info['id']
            self.debug(
                'property change: %s[%s].%s: %s -> %s', change.type, id_, change.property,
                json_utils.dumps(change.old_value, allow_extended_types=True),
                json_utils.dumps(change.new_value, allow_extended_types=True)
            )
            obj = self._properties.setdefault(change.type, {}).setdefault(id_, {})
            obj[change.property] = change.new_value
            obj['label'] = info['label']

        else:
            id_ = None
            self.debug(
                'property change: %s.%s: %s -> %s', change.type, change.property,
                json_utils.dumps(change.old_value, allow_extended_types=True),
                json_utils.dumps(change.new_value, allow_extended_types=True)
            )
            self._properties.setdefault(change.type, {})[change.property] = change.new_value

        for port in self.get_ports():
            pai_port = cast(ParadoxPort, port)

            try:
                pai_port.on_property_change(change.type, id_, change.property, change.old_value, change.new_value)

            except Exception as e:
                self.error('property change handler execution failed: %s', e, exc_info=True)

    def get_property(self, type_: str, id_: Optional[Union[str, int]], name: str) -> Property:
        if type_ == 'system':
            return self._properties.get(type_, {}).get(name)

        else:
            return self._properties.get(type_, {}).get(id_, {}).get(name)

    def get_properties(self, type_: str, id_: Optional[Union[str, int]]) -> Dict[str, Property]:
        if type_ == 'system':
            return self._properties.get(type_, {})

        else:
            return self._properties.get(type_, {}).get(id_, {})

    async def set_area_armed_mode(self, area: int, armed_mode: str) -> None:
        self.debug('area %s: set armed mode to %s', area, armed_mode)
        if not await self._paradox.panel.control_partitions([area], armed_mode):
            raise exceptions.ParadoxCommandError('Failed to set area armed mode')

    async def set_zone_bypass(self, zone: int, bypass: bool) -> None:
        self.debug('zone %s: %s bypass', zone, ['clear', 'set'][bypass])
        if not await self._paradox.panel.control_zones([zone], constants.ZONE_BYPASS_MAPPING[bypass]):
            raise exceptions.ParadoxCommandError('Failed to set zone bypass')

    async def set_output_action(self, output: int, action: str) -> None:
        self.debug('output %s: set action to %s', output, action)
        if not await self._paradox.panel.control_outputs([output], action):
            raise exceptions.ParadoxCommandError('Failed to set output action')
