import os, sys
import tkinter as tk

from Gui import MainApp


def resource_path(relative_path):

    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__=="__main__":

    root = tk.Tk()
    root.title("VISA scan")
    root.iconbitmap(default=resource_path('visa_scan.ico'))
    MainApp(root)
    root.mainloop()