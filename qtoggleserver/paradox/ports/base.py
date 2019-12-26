
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
        self.setup_config()
        self.setup_logging()

        self._paradox = None
        self._panel_task = None
        self._check_connection_task = asyncio.create_task(self._check_connection_loop())

        ps.subscribe(self.handle_paradox_property_change, 'changes')

        self._properties = {}

        super().__init__(address, name)

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
        address = self.get_address()
        parts = address.split(':')

        if parts[0].startswith('/'):  # A serial port, e.g. /dev/ttyUSB0
            config.CONNECTION_TYPE = 'Serial'
            config.SERIAL_PORT = parts[0]
            config.SERIAL_BAUD = constants.DEFAULT_SERIAL_BAUD
            if len(parts) > 1:
                config.SERIAL_BAUD = int(parts[1])

            self.debug('using serial connection on %s:%s', config.SERIAL_PORT, config.SERIAL_BAUD)

        else:  # IP connection, e.g. 192.168.1.2:10000:paradox
            config.CONNECTION_TYPE = 'IP'
            config.IP_CONNECTION_HOST = parts[0]
            config.IP_CONNECTION_PORT = constants.DEFAULT_IP_PORT
            config.IP_CONNECTION_PASSWORD = constants.DEFAULT_IP_PASSWORD
            if len(parts) > 1:
                config.IP_CONNECTION_PORT = int(parts[1])

            if len(parts) > 2:
                config.IP_CONNECTION_PASSWORD = parts[2]

            config.IP_CONNECTION_PASSWORD = config.IP_CONNECTION_PASSWORD.encode()

            self.debug('using IP connection on %s:%s', config.IP_CONNECTION_HOST, config.IP_CONNECTION_PORT)

        return Paradox()

    def parse_labels(self):
        for area in self._paradox.storage.data['partition'].values():
            self.debug('detected area id=%s, label=%s', area['id'], json_utils.dumps(area['label']))

        for zone in self._paradox.storage.data['zone'].values():
            self.debug('detected zone id=%s, label=%s', zone['id'], json_utils.dumps(zone['label']))

        for output in self._paradox.storage.data['pgm'].values():
            self.debug('detected output id=%s, label=%s', output['id'], json_utils.dumps(output['label']))

        for _type, entries in self._paradox.storage.data.items():
            for entry in entries.values():
                if 'label' in entry:
                    self._properties.setdefault(_type, {}).setdefault(entry['id'], {})['label'] = entry['label']

    async def connect(self):
        self.debug('connecting to panel')

        if not self._paradox:
            self._paradox = self.make_paradox()

        if not await self._paradox.connect_async():
            raise exceptions.PAIConnectError()

        self.debug('connected to panel')
        asyncio.create_task(self.handle_connected())

    async def handle_connected(self):
        self._panel_task = asyncio.create_task(self._paradox.async_loop())

        self.parse_labels()
        self.trigger_port_update()

    async def disconnect(self):
        if self._panel_task is None:
            return

        self.debug('disconnecting')
        try:
            self._paradox.disconnect()

        except ConnectionError as e:
            # PAI may raise ConnectionError when disconnecting, so we catch it here and ignore it
            self.error('failed to disconnect from panel: %s', e, exc_info=True)

        self._paradox = None

        self.trigger_port_update()

        try:
            await asyncio.wait_for(self._panel_task, timeout=10)

        except asyncio.TimeoutError:
            self.error('timeout waiting for panel task end')
            self._panel_task.cancel()

        else:
            self.debug('disconnected')

        self._panel_task = None

    def is_connected(self):
        if not self._paradox:
            return False

        if not self._paradox.panel:
            return False

        if not self._panel_task:
            return False

        return bool(self._paradox.connection.connected)

    async def _check_connection_loop(self):
        connect_succeeded = False

        try:
            while True:
                connected = (self._paradox and self._paradox.connection and
                             self._paradox.connection.connected and connect_succeeded)
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

    async def handle_cleanup(self):
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
            _id = None
            self.debug('property change: %s.%s: %s -> %s', change.type, change.property,
                       json_utils.dumps(change.old_value), json_utils.dumps(change.new_value))
            self._properties.setdefault(change.type, {})[change.property] = change.new_value

        for port in self.get_ports():
            try:
                port.on_property_change(change.type, _id, change.property, change.old_value, change.new_value)

            except Exception as e:
                self.error('property change handler execution failed: %s', e, exc_info=True)

    def get_property(self, _type, _id, name):
        if _type == 'system':
            return self._properties.get(_type, {}).get(name)

        else:
            return self._properties.get(_type, {}).get(_id, {}).get(name)

    def get_properties(self, _type, _id):
        if _type == 'system':
            return self._properties.get(_type, {})

        else:
            return self._properties.get(_type, {}).get(_id, {})

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

    def __init__(self, address, peripheral_name=None):
        super().__init__(address, peripheral_name)

    async def attr_is_online(self):
        return self.get_peripheral().is_connected()

    def on_property_change(self, _type, _id, _property, old_value, new_value):
        pass
