import pandas as pd
import socket
import threading
import queue
import pyvisa
import time

from message import Message


class Scanner():

    def __init__(self, outbox, port=5025, ip_start=1, ip_end=255, timeout=2):

        self.inbox_q = queue.Queue()
        self.outbox_q = outbox

        self.ip_start = ip_start
        self.ip_end = ip_end
        self.port = port
        self.timeout = timeout

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        local_ip = local_ip.split('.')
        self.prefix = f"{local_ip[0]}.{local_ip[1]}.{local_ip[2]}."

        self.visa_q = queue.Queue()
        self.threads_q = queue.Queue()

        threading.Thread(target=self.worker, daemon=True).start()


    def scan_worker(self, *args):

        threading.Thread(target=self.scan, daemon=True).start()


    def scan(self):

        for num in range(self.ip_start, self.ip_end):
            ip = f"{self.prefix}{num}"
            t = threading.Thread(target=self.port_alive, args=(ip,), name=f"port_{ip}", daemon=True)
            t.start()
            self.threads_q.put(t)

        while not self.threads_q.empty():
            t = self.threads_q.get()
            t.join()

        results = []
        while not self.visa_q.empty():
            visa = self.visa_q.get()
            device = self.parse_idn(visa)
            results.append(device)

        messages = (
            Message(src="scanner", dst="results", cmd="write", args=(results,)),
            Message(src="scanner", dst="controls", cmd="scan_done"),
        )
        for message in messages:
            self.outbox_q.put(message)


    def port_alive(self, ip):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        try:
            sock.connect((ip, self.port))
        except ConnectionRefusedError:
            pass
        except socket.timeout:
            pass
        except TimeoutError:
            pass
        else:
            t = threading.Thread(target=self.visa_alive, args=(ip,), name=f"visa_{ip}", daemon=True)
            t.start()
            self.threads_q.put(t)
        finally:
            sock.close()


    def visa_alive(self, ip):

        resource = f"TCPIP::{ip}::INSTR"
        rm = pyvisa.ResourceManager()

        try:
            instrument = rm.open_resource(resource)
        except Exception:
            return
        
        instrument.timeout = 1000
        instrument.read_termination = "\n"
        instrument.write_termination = "\n"

        try:
            idn = instrument.query('*IDN?')
        except Exception:
            return

        result = (ip, idn,)
        self.visa_q.put(result)


    def parse_idn(self, visa):

            device = {}
            device["ip"] = visa[0]

            idn = visa[1].split(',')
            for index, element in enumerate(idn):
                if index == 0:
                    device["man"] = element
                    continue
                if index == 1:
                    device["device"] = element
                    continue
                if index == 2:
                    device["serial"] = element
                    continue
                if "SW" in element:
                    device["sw"] = element
                    continue
                if "HW" in element:
                    device["hw"] = element
                    continue
                device["sw"] = element

            return device


    def put(self, message):

        self.inbox_q.put(message)


    def worker(self):

        commands = {
            "scan":self.scan_worker,
        }

        while True:
            try:
                msg = self.inbox_q.get()
            except queue.Empty:
                continue
            else:
                commands[msg.cmd](*msg.args)
            finally:
                time.sleep(10 / 1000)
