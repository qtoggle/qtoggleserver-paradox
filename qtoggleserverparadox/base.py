
import asyncio
import logging

from abc import ABCMeta
from paradox.config import config
from paradox.lib import ps
from paradox.paradox import Paradox

from qtoggleserver.utils import ConfigurableMixin
from qtoggleserver.utils import json as json_utils
from qtoggleserver.lib.peripheral import Peripheral, PeripheralPort


from . import constants
from . import exceptions


class PAIPeripheral(Peripheral):
    logger = logging.getLogger(__name__)

    def __init__(self, address, name):
        self._serial_port, self._serial_baud = self.spit_address(address)

        self.setup_config()
        self.setup_logging()

        self._paradox = None
        self._panel_task = None
        self._check_connection_task = None
        self._retry_connect_task = None

        self._properties = {}

        super().__init__(address, name)

    @staticmethod
    def spit_address(address):
        return address.split(':')

    @staticmethod
    def setup_config():
        config.CONFIG_LOADED = True
        for k, v in config.DEFAULTS.items():
            if isinstance(v, tuple):
                v = v[0]

            setattr(config, k, v)

    @staticmethod
    def setup_logging():
        logging.getLogger('PAI').setLevel(logging.ERROR)
        logging.getLogger('PAI.paradox.lib.async_message_manager').setLevel(logging.CRITICAL)

    def make_paradox(self):
        config.SERIAL_PORT = self._serial_port
        config.SERIAL_BAUD = self._serial_baud
        paradox = Paradox()

        ps.subscribe(self.handle_paradox_property_change, 'changes')

        return paradox

    def parse_labels(self):
        for area in self._paradox.storage.data['partition'].values():
            self.debug('detected area id=%s, label=%s', area['id'], json_utils.dumps(area['label']))

        for zone in self._paradox.storage.data['zone'].values():
            self.debug('detected zone id=%s, label=%s', zone['id'], json_utils.dumps(zone['label']))

        for output in self._paradox.storage.data['pgm'].values():
            self.debug('detected output id=%s, label=%s', output['id'], json_utils.dumps(output['label']))

        for _type, entries in self._paradox.storage.data.items():
            for entry in entries.values():
                self._properties.setdefault(_type, {}).setdefault(entry['id'], {})['label'] = entry['label']

    async def connect(self):
        self.debug('connecting to panel')
        self._paradox = self.make_paradox()
        if not await self._paradox.connect_async():
            raise exceptions.PAIConnectError()

        self.debug('connected to panel')
        self._panel_task = asyncio.create_task(self._paradox.async_loop())
        self._check_connection_task = asyncio.create_task(self._check_connection_loop())

        self.parse_labels()

    async def disconnect(self):
        if self._panel_task is None:
            return

        if self._retry_connect_task:
            self._retry_connect_task.cancel()
            self._retry_connect_task = None

        self.debug('disconnecting')
        try:
            self._paradox.disconnect()

        except ConnectionError as e:
            # PAI may raise ConnectionError when disconnecting, so we catch it here and ignore it
            self.error('failed to disconnect from panel: %s', e, exc_info=True)

        self._paradox = None

        try:
            await asyncio.wait_for(self._panel_task, timeout=10)

        except asyncio.TimeoutError:
            self.error('timeout waiting for panel task end')
            self._panel_task.cancel()

        else:
            self.debug('disconnected')

        self._panel_task = None
        self._retry_connect_task = None

    def is_connected(self):
        if not self._paradox:
            return False

        if not self._paradox.panel:
            return False

        if not self._panel_task:
            return False

        return bool(self._paradox.connection.connected)

    async def _check_connection_loop(self):
        while self._panel_task is not None and self.is_enabled():
            if not self._paradox.connection.connected:
                self.error('connection closed, reconnecting')
                await self.disconnect()
                asyncio.create_task(self.connect())
                break

            await asyncio.sleep(1)

    async def _retry_connect_indefinitely(self):
        while True:
            try:
                self.error('retrying to connect')
                await self.connect()
                break

            except asyncio.CancelledError:
                break

            except Exception as e:
                self.error('could not connect to panel: %s', e)
                await asyncio.sleep(5)

    async def handle_enable(self):
        try:
            await self.connect()

        except Exception as e:
            self.error('could not connect to panel: %s', e)
            self._retry_connect_task = asyncio.create_task(self._retry_connect_indefinitely())

    async def handle_disable(self):
        await self.disconnect()

    async def handle_done(self):
        await self.disconnect()

    def handle_paradox_property_change(self, change):
        info = self._paradox.storage.data[change.type].get(change.key)
        if info and ('id' in info):
            _id = info['id']
            self.debug('property change: %s[%s].%s: %s -> %s', change.type, _id, change.property,
                       json_utils.dumps(change.old_value), json_utils.dumps(change.new_value))
            obj = self._properties.setdefault(change.type, {}).setdefault(_id, {})
            obj[change.property] = change.new_value
            obj['label'] = info['label']

        else:
            self.debug('property change: %s.%s: %s -> %s', change.type, change.property,
                       json_utils.dumps(change.old_value), json_utils.dumps(change.new_value))
            self._properties.setdefault(change.type, {})[change.property] = change.new_value

    def get_property(self, _type, _id, name):
        if _type == 'system':
            return self._properties.get(_type, {}).get(name)

        else:
            return self._properties.get(_type, {}).get(_id, {}).get(name)

    async def set_area_armed_mode(self, area, armed_mode):
        self.debug('area %s: set armed mode to %s', area, armed_mode)
        if not await self._paradox.panel.control_partitions([area], armed_mode):
            raise exceptions.PAICommandError('failed to set area armed mode')

    async def set_zone_bypass(self, zone, bypass):
        self.debug('zone %s: % bypass', zone, ['clear', 'set'][bypass])
        if not await self._paradox.panel.control_zones([zone], constants.ZONE_BYPASS_MAPPING[bypass]):
            raise exceptions.PAICommandError('failed to set zone bypass')

    async def set_output_action(self, output, action):
        self.debug('output %s: set action to %s', output, action)
        if not await self._paradox.panel.control_outputs([output], action):
            raise exceptions.PAICommandError('failed to set output action')


class PAIPort(PeripheralPort, ConfigurableMixin, metaclass=ABCMeta):
    PERIPHERAL_CLASS = PAIPeripheral
    CMD_TIMEOUT = 60

    def __init__(self, serial_port, serial_baud, peripheral_name=None):
        super().__init__(self.make_address(serial_port, serial_baud), peripheral_name)

    @staticmethod
    def make_address(serial_port, serial_baud):
        return '{}:{}'.format(serial_port, serial_baud)  # E.g. "/dev/ttyUSB0:9600"

    async def attr_is_online(self):
        return self.get_peripheral().is_connected()
