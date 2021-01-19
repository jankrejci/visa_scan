import tkinter as tk
import threading
import queue
import time

from message import Message


class Controls(tk.Frame):

    def __init__(self, parent, outbox, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.inbox_q = queue.Queue()
        self.outbox_q = outbox

        self.make()

        threading.Thread(target=self.worker, daemon=True).start()


    def make(self):

        self.scan_button = tk.Button(self.parent, text="Scan", command=self.scan_start, width=10)
        self.scan_button.grid(row=0, column=3, padx=1, pady=1)


    def scan_start(self):

        self.scan_button.config(state="disabled", text="Scanning")

        messages = (
            Message(src="controls", dst="results", cmd="clear"),
            Message(src="controls", dst="scanner", cmd="scan"),
        )
        for message in messages:
            self.outbox_q.put(message)


    def scan_done(self, *args):

        self.scan_button.config(state="normal", text="Scan")


    def put(self, message):

        self.inbox_q.put(message)


    def worker(self):

        commands = {
            "scan_done":self.scan_done,
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
