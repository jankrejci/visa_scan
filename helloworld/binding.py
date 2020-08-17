import tkinter as tk

class MainApp(tk.Frame):

    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.btn = tk.Button(parent, text="Press", command=self.write)
        self.btn.grid(row=1, column=0, padx=1)

        self.txt = tk.Text(parent)
        self.txt.grid(row=0, column=0)
        self.txt.bind(self.btn('<Button-1>'), self.write)


    def write(self):

        self.txt.insert(tk.END, "btn pressed\n")


if __name__=="__main__":

    root = tk.Tk()
    MainApp(root)
    root.mainloop()