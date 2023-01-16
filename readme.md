## Sensing
Recording the data from Mitutoyo sensors.
This project have been implemented to run on `Windows`.
It automatically search all ports for Mitutoyo so that you don't have to exhaustively set them.

## Installation
You should first install USB-ITN for serial ports.

- Install Python 3.8
- Install libraries

```Shell
>> python -m pip install pyserial==3.5
```

## Run
```Shell
>> python main.py -b 9600 -w ./workdir -t 1

// shortcut
>> python main.py -w ./workdir
```