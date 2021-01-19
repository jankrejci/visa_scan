import os
import sys
import tkinter as tk

from gui import MainApp


def resource_path(relative_path):

    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__=="__main__":

    root = tk.Tk()
    root.title("VISA scan")
    root.iconbitmap(default=resource_path('visa_scan.ico'))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.minsize(700, 100)

    MainApp(root)
    root.mainloop()