import tkinter as tk
import threading
import time
import queue

from Scanner import Scanner
from Controls import Controls
from Results import Results


class MainApp(tk.Frame):

    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.gui_events = queue.Queue()

        self.scanner = Scanner(self.gui_events)

        self.make_results()
        self.make_controls()

        threading.Thread(target=self.gui_worker, daemon=True).start()


    def make_results(self):

        self.results_frame = tk.Frame(self.parent, width=120)
        self.results_frame.grid(row=0, column=0, sticky="nswe", padx=1)
        self.results = Results(self.results_frame, self.gui_events)


    def make_controls(self):

        self.controls_frame = tk.Frame(self.parent)
        self.controls_frame.grid(row=1, column=0, padx=1)
        self.controls = Controls(self.controls_frame, self.gui_events)


    def gui_worker(self):

        bindings = {
            "results":self.results,
            "controls":self.controls,
            "scanner":self.scanner,
        }

        while True:
            if not self.gui_events.empty():
                target, command, *args = self.gui_events.get()
                bindings[target].invoke(command, *args)
            time.sleep(10 / 1000)
