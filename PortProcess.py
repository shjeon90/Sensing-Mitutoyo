import argparse
import serial
import time
import os
import logging

class PortHandler:
    def __init__(self, port, baud_rate=9600, timeout=1, workdir=None, log_level='debug', interval=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.workdir = workdir
        self.interval = interval
        self.output_file = open(os.path.join(workdir, 'outputs', f'output-{port}.csv'), 'ab')

        self.log_level = logging.DEBUG if log_level == 'debug' else logging.INFO
        self.logger = logging.getLogger(port)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        file_handler = logging.FileHandler(os.path.join(workdir, 'logs', f'log-{port}.txt'))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(level=self.log_level)

        self.ser = serial.Serial(self.port, baud_rate, timeout=0)

    def terminate(self):
        try:
            self.output_file.flush()
            self.output_file.close()

            self.ser.close()
        except OSError:
            pass

    def run(self):
        while True:
            self.logger.debug('wait to send a signal')
            if self.ser.writable():
                self.logger.debug('send a signal')
                self.ser.write(b'\x31\x0d')

            self.logger.debug('wait to receive data')
            if self.ser.readable():
                data = self.ser.read(15)
                self.logger.debug('data received')
                data = data.decode().strip()

                if data.startswith('01A'):
                    data = data[3:]
                    # cur_time = time.time() * 1000
                    year, month, day, hour, minute, sec = map(int, time.strftime("%Y %m %d %H %M %S").split())
                    self.logger.debug(f'record data: {data}')

                    self.output_file.write(f'{year},{month},{day},{hour},{minute},{sec},{float(data)}\n'.encode())
                    self.output_file.flush()

            time.sleep(self.interval)


def parse_args():
    parser = argparse.ArgumentParser(description='sensing')
    parser.add_argument('-p', dest='port', required=True)
    parser.add_argument('-b', dest='baud_rate', required=True, type=int)
    parser.add_argument('-t', dest='timeout', default=1, type=int)
    parser.add_argument('-w', dest='workdir', required=True)
    parser.add_argument('-l', dest='log_level', choices=['info', 'debug'])
    parser.add_argument('-i', dest='interval', default=1, type=int)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    port = args.port
    baud_rate = args.baud_rate
    timeout = args.timeout
    workdir = args.workdir
    log_level = args.log_level
    interval = args.interval

    handler = PortHandler(port, baud_rate, workdir=workdir, log_level=log_level, interval=interval)
    try:
        handler.run()
    except KeyboardInterrupt:
        handler.terminate()