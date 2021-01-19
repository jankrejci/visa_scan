import tkinter as tk
import tkinter.ttk as ttk
import threading
import queue
import time

from message import Message


class Results(tk.Frame):


    def __init__(self, parent, outbox, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.inbox_q = queue.Queue()
        self.outbox_q = outbox

        self.make()

        threading.Thread(target=self.worker, daemon=True).start()


    def make(self):

        self.columns = (
            # ID, name, width
            ("#0", "IP address", 100),
            ("device", "Device", 100),
            ("serial", "Serial number", 150),
            ("hw", "Hardware", 100),
            ("sw", "Software", 100),
            ("man", "Manufacturer", 150),
        )

        self.results = ttk.Treeview(self.parent)
        self.results.grid(row=0, column=0, sticky="nswe")

        id_names = [x[0] for x in self.columns][1:]
        self.results["columns"] = id_names

        for id, name, width in self.columns:
            self.results.column(id, width=width, minwidth=width)
            self.results.heading(id, text=name, anchor=tk.W)
        self.results.grid()


    def clear(self, *args):

        self.results.delete(*self.results.get_children())


    def write(self, *args):

        devices = args[0]
        id_names = [x[0] for x in self.columns][1:]

        for device in devices:
            values = []
            for id in id_names:
                values.append(device.get(id, ""))
            self.results.insert("", "end", text=device.get("ip"), values=values)


    def put(self, message):

        self.inbox_q.put(message)


    def worker(self):

        commands = {
            "clear":self.clear,
            "write":self.write,
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