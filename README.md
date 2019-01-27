# Acer Projector Control - RS232 and MQTT

This has been tested with my Acer M550, a Raspberry Pi Zero W, a UGREEN 20210 USB Serial Cable, USB to RS232 DB9 9 pin Converter Cable and a DB9 F/F Null Modem Cable. I'm sure other cables would work just as well but I have tried a few combinations and failed a few times. In my setup I stupidly didnt leave a working RS232 cable in the wall when I was running my other cables (just a rubbish broken one....) so I have the Pi sitting in a broject box with a AC-DC Isolated AC 110V / 220V To DC 5V 600mA. Not recommending this approach but it got me out of a hole

I've implemented only what I currently use to date though more than happy to take suggestions on functionality (where possible).

## Getting Started

This has been implemented with what I have available. I specifically need power status and the ability to send ON / OFF commands to my Home Assistant / Node Red setup and this is what I have concentrated on.

### Prerequisites

Clearly an Acer projector is required, as stated I have only tried this out with my Acer M550. Would love to know from others if it also works on other models connected to your local network. 

```
python --version
Python 2.7.15rc1

usage: acer-mqtt.py [-h] -b BROKER -p PORT -u USER -pw PASSWORD -sp SERIALPORT
                    [-st STATETOPIC] [-pt POWERTOPIC]

optional arguments:
  -h, --help            show this help message and exit
  -b BROKER, --broker BROKER
                        IP Address for MQTT Broker (Required)
  -p PORT, --port PORT  Port for MQTT Broker (Required)
  -u USER, --user USER  User for MQTT Broker (Required)
  -pw PASSWORD, --password PASSWORD
                        Password for MQTT Broker (Required)
  -sp SERIALPORT, --serialport SERIALPORT
                        Serial port for acer projector (Required)
  -st STATETOPIC, --statetopic STATETOPIC
                        Optional topic for state
  -pt POWERTOPIC, --powertopic POWERTOPIC
                        Optional topic for power
```

My Home Assistant config if this helps anyone
```
switch:  
  - platform:  mqtt
    name: "Acer Projector"
    state_topic: "acer/status"
    command_topic: "acer/power"
    payload_on: '{"command":"* 0 IR 001", "expected_status":"ON"}'
    payload_off: '{"command":"* 0 IR 002", "expected_status":"OFF"}'
    state_on: "ON"
    state_off: "OFF"
    optimistic: false
    qos: 0
    retain: true
```


## Authors

* **John Williamson** - *Initial work* 
