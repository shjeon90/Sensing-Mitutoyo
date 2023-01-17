import re
import os
import argparse
import serial.tools.list_ports
from ProcessMonitor import ProcessMonitor

def list_target_ports():
    def fn(port):
        m = re.match('COM(\d+)', port.description)
        if m:
            return m.group(1)

    ports = serial.tools.list_ports.comports()
    available_ports = [
        port for port in ports if 'USB-ITN' in port.description
    ]
    available_ports.sort(key=fn)

    print('Founded serial ports')
    for idx, port in enumerate(available_ports):
        print(f'{idx}. {port}')
    print()

    return available_ports

def parse_args():
    parser = argparse.ArgumentParser(description='sensing')
    parser.add_argument('-b', dest='baud_rate', default=9600, type=int)
    parser.add_argument('-w', dest='workdir', required=True)
    parser.add_argument('-t', dest='timeout', default=1, type=int)
    parser.add_argument('-l', dest='log_level', choices=['info', 'debug'], default='debug')
    return parser.parse_args()

def main():
    args = parse_args()
    baud_rate = args.baud_rate
    workdir = args.workdir
    timeout = args.timeout
    log_level = args.log_level

    print('Configurations')
    print(f'- baud rate: {baud_rate}')
    print(f'- timeout: {timeout}')
    print(f'- work dir: {workdir}')
    print(f'- log level: {log_level}')
    print()

    if not os.path.exists(workdir):
        os.mkdir(workdir)

    if not os.path.exists(os.path.join(workdir, 'outputs')):
        os.mkdir(os.path.join(workdir, 'outputs'))

    if not os.path.exists(os.path.join(workdir, 'logs')):
        os.mkdir(os.path.join(workdir, 'logs'))

    available_ports = list_target_ports()

    monitor = ProcessMonitor(available_ports, baud_rate, timeout=timeout, workdir=workdir, log_level=log_level)
    monitor.run()


if __name__ == '__main__':
    main()
