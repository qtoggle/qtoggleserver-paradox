### About

This is an addon for [qToggleServer](https://github.com/qtoggle/qtoggleserver).

It provides a set of drivers to control your Paradox alarm with qToggleServer.


### Usage

##### `qtoggleserver.conf:`
``` javascript
...
ports = [
    ...
    {
        driver: "qtoggleserverparadox.area.AreaArmedPort",
        area: 1,
        serial_port: "/dev/ttyUSB0"
    }
    {
        driver: "qtoggleserverparadox.area.AreaAlarmPort",
        area: 1,
        serial_port: "/dev/ttyUSB0"
    }
    {
        driver: "qtoggleserverparadox.zone.ZoneOpenPort",
        zone: 1,
        serial_port: "/devy/ttyUSB0"
    } 
    {
        driver: "qtoggleserverparadox.zone.ZoneAlarmPort",
        zone: 1,
        serial_port: "/devy/ttyUSB0"
    } 
    ...
]
...
