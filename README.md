### About

This is an addon for [qToggleServer](https://github.com/qtoggle/qtoggleserver).

It provides a set of drivers to control your Paradox alarm with qToggleServer.


### Install

Install using pip:

    pip install qtoggleserver-paradox


### Usage

##### `qtoggleserver.conf:`
``` javascript
...
ports = [
    ...
    {
        driver: "qtoggleserver.paradox.ports.area.AreaArmedPort",
        area: 1,
        serial_port: "/tmp/ttyV0"
    }
    {
        driver: "qtoggleserver.paradox.ports.area.AreaAlarmPort",
        area: 1,
        serial_port: "/tmp/ttyV0"
    }

    {
        driver: "qtoggleserver.paradox.ports.output.OutputTroublePort",
        output: 1,
        serial_port: "/tmp/ttyV0"
    }
    {
        driver: "qtoggleserver.paradox.ports.output.OutputTamperPort",
        output: 1,
        serial_port: "/tmp/ttyV0"
    }

    {
        driver: "qtoggleserver.paradox.ports.system.SystemTroublePort",
        serial_port: "/tmp/ttyV0"
    }

    {
        driver: "qtoggleserver.paradox.ports.output.OutputTroublePort",
        output: 1,
        serial_port: "/tmp/ttyV0"
    }

    {
        driver: "qtoggleserver.paradox.ports.zone.ZoneOpenPort",
        zone: 1,
        serial_port: "/tmp/ttyV0"
    }
    {
        driver: "qtoggleserver.paradox.ports.zone.ZoneAlarmPort",
        zone: 1,
        serial_port: "/tmp/ttyV0"
    }
    {
        driver: "qtoggleserver.paradox.ports.zone.ZoneTroublePort",
        zone: 1,
        serial_port: "/tmp/ttyV0"
    }
    {
        driver: "qtoggleserver.paradox.ports.zone.ZoneTamperPort",
        zone: 1,
        serial_port: "/tmp/ttyV0"
    }
    ...
]
...
