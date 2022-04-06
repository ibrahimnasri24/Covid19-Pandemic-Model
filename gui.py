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
        self.root.geometry("1080x1000+0+0")
        self.root.wm_title("Covid19 Model")
        # self.root.state("zoomed") # open window maximized
        self.content = tk.Frame(self.root)

        self.graph = graph.Graph()
        self.canvas = FigureCanvasTkAgg(self.graph.fig, master=self.content)
        button_start = tk.Button(
            master=self.content, text="Start", command=self.start_animation_window
        )

        social_ditancing_percentage_slider = Slider(
            self.content, "Percentage of Population Social Distancing:"
        )
        social_ditancing_efficiency_slider = Slider(
            self.content, "Social Distancing Efficiency:"
        )

        nb_col = 10
        nb_row = 10

        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        self.canvas.get_tk_widget().grid(
            column=0,
            row=0,
            columnspan=5,
            rowspan=5,
            sticky=(N, S, E, W),
            pady=5,
            padx=5,
        )
        button_start.grid(column=7, row=0, pady=5, padx=5)
        social_ditancing_efficiency_slider.frame.grid(
            column=0, row=5, columnspan=3, sticky="we", padx=5, pady=5
        )
        social_ditancing_percentage_slider.frame.grid(
            column=0, row=6, columnspan=3, sticky="we", padx=5, pady=5
        )

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        for i in range(int(nb_col / 2)):
            self.content.columnconfigure(i, weight=1)
        for i in range(int(nb_col / 2), nb_col):
            self.content.columnconfigure(i, weight=2)
        for i in range(nb_row):
            self.content.rowconfigure(i, weight=1)

        tk.mainloop()

    def quit(self):
        self.root.quit()
        self.root.destroy()

    def start_animation_window(self):
        if self.first_time:
            self.result = multiprocessing.Array("d", 3)
            self.graph.mainfunc(self.result, self.canvas)
        else:
            self.graph.reset()
        self.first_time = False
        self.result[0] = 0  # time (frame nb)
        self.result[1] = 0  # infeted percentage of population
        self.result[2] = 0  # animation window exit flag
        p2 = multiprocessing.Process(
            target=animation_window.main, args=(True, self.result)
        )
        p2.start()


class Slider:
    def __init__(
        self, parent, label, orientation=HORIZONTAL, length=350, from_=0, to_=100
    ):
        self.frame = tk.Frame(parent)
        self.scale = tk.Scale(
            self.frame, orient=orientation, length=length, from_=from_, to=to_
        )
        self.label = tk.Label(self.frame, text=label)

        self.frame.grid(column=0, row=0)
        self.scale.grid(column=1, row=0, sticky="we")
        self.label.grid(column=0, row=0, sticky="es", pady=2, padx=15)
        self.label.configure(font=("Ariel", 14))

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)
        self.frame.rowconfigure(0, weight=1)


if __name__ == "__main__":
    gui = GUI()
    gui.result[2] = 1  # setting exit flag to 1
