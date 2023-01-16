import argparse
import serial
import time
import atexit
import os

class PortHandler:
    def __init__(self, port, baud_rate=9600, timeout=1, workdir=None):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.workdir = workdir

        self.output_file = open(os.path.join(workdir, f'output-{port}.csv'), 'ab')
        self.ser = serial.Serial(self.port, baud_rate, timeout=timeout)

        atexit.register(self.terminate)

    def terminate(self):
        try:
            self.output_file.flush()
            self.output_file.close()
            self.ser.close()
        except OSError:
            pass

    def run(self):
        while True:
            if self.ser.writable():
                self.ser.write(b'\x31\x0d')

            if self.ser.readable():
                data = self.ser.read(15)
                data = data.decode().strip()

                if data.startswith('01A'):
                    data = data[3:]
                    cur_time = time.time() * 1000

                    self.output_file.write(f'{cur_time},{float(data)}\n'.encode())
                    self.output_file.flush()


def parse_args():
    parser = argparse.ArgumentParser(description='sensing')
    parser.add_argument('-p', dest='port', required=True)
    parser.add_argument('-b', dest='baud_rate', required=True, type=int)
    parser.add_argument('-t', dest='timeout', default=1, type=int)
    parser.add_argument('-w', dest='workdir', required=True)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    port = args.port
    baud_rate = args.baud_rate
    timeout = args.timeout
    workdir = args.workdir

    handler = PortHandler(port, baud_rate, workdir=workdir)
    handler.run()