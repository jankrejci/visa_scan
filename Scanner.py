import pandas as pd

import socket
import threading
import queue
import pyvisa


class Scanner():

    def __init__(self, gui_events, port=5025, ip_start=1, ip_end=255, timeout=2):

        self.gui_events = gui_events
        self.ip_start = ip_start
        self.ip_end = ip_end
        self.port = port
        self.timeout = timeout

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        local_ip = local_ip.split('.')
        self.prefix = f"{local_ip[0]}.{local_ip[1]}.{local_ip[2]}."

        self.qVisa = queue.Queue()
        self.qThreads = queue.Queue()


    def invoke(self, command, *args):

        bindings = {
            "scan":self.scan_worker,
        }
        bindings[command](*args)


    def scan_worker(self, *args):

        threading.Thread(target=self.scan, daemon=True).start()


    def scan(self):

        for num in range(self.ip_start, self.ip_end):
            ip = f"{self.prefix}{num}"
            t = threading.Thread(target=self.port_alive, args=(ip,), name=f"port_{ip}", daemon=True)
            t.start()
            self.qThreads.put(t)

        while not self.qThreads.empty():
            t = self.qThreads.get()
            t.join()

        results = []
        while not self.qVisa.empty():
            visa = self.qVisa.get()
            device = self.parse_idn(visa)
            results.append(device)

        event = ("results", "write", results)
        self.gui_events.put(event)
        event = ("controls", "scan_done")
        self.gui_events.put(event)


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
            self.qThreads.put(t)
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
        self.qVisa.put(result)


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
