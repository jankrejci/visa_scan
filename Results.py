import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import pandastable  as pdt
import threading
import queue


class Results(tk.Frame):


    def __init__(self, parent, gui_events, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gui_events = gui_events

        self.make_table()


    def make_table(self):

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
        id_names = [x[0] for x in self.columns][1:]
        self.results["columns"] = id_names

        for id, name, width in self.columns:
            self.results.column(id, width=width, minwidth=width)
            self.results.heading(id, text=name, anchor=tk.W)
        self.results.grid()


    def invoke(self, command, *args):

        bindings = {
            "clear":self.clear,
            "write":self.write,
        }
        bindings[command](*args)


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
