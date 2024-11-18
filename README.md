## About

This is an addon for [qToggleServer](https://github.com/qtoggle/qtoggleserver).

It provides a driver to control your Paradox alarm with qToggleServer.


## Install

Install using pip:

    pip install qtoggleserver-paradox


## Usage

##### `qtoggleserver.conf:`
``` ini
...
peripherals = [
    ...
    {
        driver = "qtoggleserver.paradox.ParadoxAlarm"
        name = "myalarm"                # a name of your choice
        zones = [1, 2, 4, 6]            # list of zones in use
        areas = [1, 2]                  # list of areas in use
        outputs = [1]                   # list of outputs in use
        serial_port = "/dev/ttyUSB0"
        serial_baud = 9600              # this is the default
        ip_host = "192.168.1.2"         # specify either this or serial_port, not both
        ip_port = 10000                 # this is the default
        ip_password = "paradox"         # this is the default 
        panel_password = "1234"         # this is the default
    }
    ...
]
...
```
