import tkinter as tk
import threading
import time
import queue

from scanner import Scanner
from controls import Controls
from results import Results
from message import Message

class MainApp(tk.Frame):

    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.gui_q = queue.Queue()

        self.scanner = Scanner(outbox=self.gui_q)

        self.make_results()
        self.make_controls()

        threading.Thread(target=self.worker, daemon=True).start()


    def make_results(self):

        self.results_frame = tk.Frame(self.parent, width=120)
        self.results_frame.grid(row=0, column=0, sticky="nswe", padx=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        self.results = Results(self.results_frame, outbox=self.gui_q)


    def make_controls(self):

        self.controls_frame = tk.Frame(self.parent)
        self.controls_frame.grid(row=1, column=0, padx=1)
        self.controls = Controls(self.controls_frame, outbox=self.gui_q)


    def worker(self):

        targets = {
            "results":self.results,
            "controls":self.controls,
            "scanner":self.scanner,
        }

        while True:
            try:
                msg = self.gui_q.get()
            except queue.Empty:
                continue
            else:
                targets[msg.dst].put(msg)
            finally:
                time.sleep(10 / 1000)
