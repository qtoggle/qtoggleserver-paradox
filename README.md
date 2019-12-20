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
        driver = "qtoggleserver.paradox.ports.area.AreaArmedPort"
        area = 1
        address = "/dev/ttyUSB0"
    }
    {
        driver = "qtoggleserver.paradox.ports.area.AreaAlarmPort"
        area = 1
        address = "/dev/ttyUSB0"
    }

    {
        driver = "qtoggleserver.paradox.ports.output.OutputTroublePort"
        output = 1
        address = "/dev/ttyUSB0"
    }
    {
        driver = "qtoggleserver.paradox.ports.output.OutputTamperPort"
        output = 1
        address = "/dev/ttyUSB0"
    }

    {
        driver = "qtoggleserver.paradox.ports.system.SystemTroublePort"
        address = "/dev/ttyUSB0"
    }

    {
        driver = "qtoggleserver.paradox.ports.zone.ZoneOpenPort"
        zone = 1
        address = "/dev/ttyUSB0"
    }
    {
        driver = "qtoggleserver.paradox.ports.zone.ZoneAlarmPort"
        zone = 1
        address = "/dev/ttyUSB0"
    }
    {
        driver = "qtoggleserver.paradox.ports.zone.ZoneTroublePort"
        zone = 1
        address = "/dev/ttyUSB0"
    }
    {
        driver = "qtoggleserver.paradox.ports.zone.ZoneTamperPort"
        zone = 1
        address = "/dev/ttyUSB0"
    }
    ...
]
...
```

The `address` field can be:

 * the details of a serial connection, given as `port:baud`, e.g.:
     
         /dev/ttyUSB0:9600
     
     The baud rate is optional and defaults to `9600`.
 
 * the hostname of an IP interfacing module, given as `host:port:password`, e.g.:
 
         192.168.1.2:10000:paradox
     
     The port is optional an defaults to `10000`.
     The password is optional and defaults to `paradox`.

