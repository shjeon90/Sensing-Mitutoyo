import multiprocessing
import subprocess
import sys
import os
import atexit
import signal
import time


def generate_cmd(port, baud_rate=9600, workdir=None, log_level='debug', interval=1):
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'PortProcess.py')]
    cmd += ['-p', port]
    cmd += ['-b', str(baud_rate)]
    cmd += ['-w', workdir]
    cmd += ['-l', log_level]
    cmd += ['-i', str(interval)]

    return cmd

def run_process(port, baud_rate=9600, workdir=None, log_level='debug', interval=1):
    cmd = generate_cmd(port, baud_rate, workdir, log_level, interval)
    # cmd = ['ipconfig']
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    try:
        stdout, stderr = p.communicate()
        print(stdout)
        print(stderr)
    except:
        pass

class ProcessMonitor:
    def __init__(self, available_ports, baud_rate=9600, timeout=1, workdir=None, log_level='debug', interval=1):
        self.available_ports = available_ports
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.workdir = workdir
        self.log_level = log_level
        self.interval = interval

        self.processes = []
        self.map_pid_port = {}

        atexit.register(self.kill)

    def kill(self):
        print('kill all children')
        for p in self.processes:
            try:
                # p.terminate()
                os.kill(p.pid, signal.SIGINT)
            except OSError:
                pass

    def create_process(self):
        dead_processes = [p for p in self.processes if not p.is_alive()]
        self.processes = [p for p in self.processes if p.is_alive()]

        for p in dead_processes:
            del self.map_pid_port[p.pid]

        running_ports = set([port_name for port_name in self.map_pid_port.values()])
        available_ports = set([port.name for port in self.available_ports])
        dead_ports = available_ports - running_ports

        for port in dead_ports:
            print(f'Restart to read data from {port}\n')

            process = multiprocessing.Process(target=run_process,
                                              args=(port, self.baud_rate, self.workdir, self.log_level))

            process.start()
            self.map_pid_port[process.pid] = port
            self.processes.append(process)

    def run(self):
        ports = []
        for port in self.available_ports:
            print(f'Start to read data from {port.name}')

            process = multiprocessing.Process(target=run_process,
                                              args=(port.name, self.baud_rate, self.workdir, self.log_level, self.interval))
            self.processes.append(process)
            ports.append(port)
        print()

        try:
            for p, port in zip(self.processes, ports):
                p.start()
                # print(f'pid: {p.pid}')
                self.map_pid_port[p.pid] = port.name
                print()

            while True:
                self.create_process()
                time.sleep(1)

        except KeyboardInterrupt:
            print('hit ctrl+c')

        for p in self.processes:
            p.join()