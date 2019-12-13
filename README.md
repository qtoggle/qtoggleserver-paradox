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
        driver: "qtoggleserver.paradox.area.AreaArmedPort",
        area: 1,
        serial_port: "/dev/ttyUSB0"
    }
    {
        driver: "qtoggleserver.paradox.area.AreaAlarmPort",
        area: 1,
        serial_port: "/dev/ttyUSB0"
    }
    {
        driver: "qtoggleserver.paradox.zone.ZoneOpenPort",
        zone: 1,
        serial_port: "/devy/ttyUSB0"
    } 
    {
        driver: "qtoggleserver.paradox.zone.ZoneAlarmPort",
        zone: 1,
        serial_port: "/devy/ttyUSB0"
    } 
    {
        driver: "qtoggleserver.paradox.zone.ZoneTroublePort",
        zone: 1,
        serial_port: "/devy/ttyUSB0"
    } 
    ...
]
...
