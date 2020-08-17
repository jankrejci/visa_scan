import tkinter as tk

import threading
import queue


class Controls(tk.Frame):

    def __init__(self, parent, gui_events, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gui_events = gui_events

        self.make_controls()


    def make_controls(self):

        self.scan_button = tk.Button(self.parent, text="Scan", command=self.scan_button, width=10)
        self.scan_button.grid(row=0, column=0, padx=1)


    def scan_button(self):

        self.scan_button.config(state="disabled", text="Scanning")
        event = ("results", "clear")
        self.gui_events.put(event)
        event = ("scanner", "scan")
        self.gui_events.put(event)


    def invoke(self, command, *args):

        bindings = {
            "scan_done":self.scan_done,
        }

        bindings[command](args)


    def scan_done(self, *args):

        self.scan_button.config(state="normal", text="Scan")
