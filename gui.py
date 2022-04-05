import multiprocessing
import tkinter as tk
from tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import animation_window
import graph

class GUI:

    def __init__(self):
        self.first_time = True
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.geometry("1080x720+100+100")
        self.root.wm_title("Covid19 Model")
        self.content = tk.Frame(self.root)

        self.canvas = FigureCanvasTkAgg(graph.Graph.fig, master=self.content)
        button_start = tk.Button(master=self.content, text="Start", command=self.start_animation_window)

        nb_col = 10
        nb_row = 7

        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        self.canvas.get_tk_widget().grid(column=0, row=0, columnspan=5, rowspan=7, sticky=(N, S, E, W), pady=5, padx=5)
        button_start.grid(column=7, row=0, pady=5, padx=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        for i in range(int(nb_col / 2)):
            self.content.columnconfigure(i, weight=1)
        for i in range(int(nb_col / 2),nb_col):
            self.content.columnconfigure(i, weight=2)
        for i in range(nb_row):
            self.content.rowconfigure(i, weight=1)

        tk.mainloop()

    def quit(self):
        self.root.quit()
        self.root.destroy()

    def start_animation_window(self):
        if self.first_time:
            result = multiprocessing.Array('d', 2)
            graph.Graph.reset()
            graph.Graph.mainfunc(result, self.canvas)
        self.first_time = False
        p2 = multiprocessing.Process(target=animation_window.main, args=(True, result))
        p2.start()

if __name__ == "__main__":
    gui = GUI()