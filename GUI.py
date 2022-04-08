import multiprocessing
import tkinter as tk
from tkinter import ttk
from tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import classes
import Graph


LARGEFONT = ("Verdana", 35)


class tkinterApp(tk.Tk):

    apps = []

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        first_time = True
        self.protocol("WM_DELETE_WINDOW", quit)
        self.geometry("1110x1000+0+0")
        self.wm_title("Covid19 Model")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.graph_gui = GraphGUI(container, self)
        self.graph_gui.grid(row=0, column=0, sticky="nsew")
        self.frames[GraphGUI] = self.graph_gui

        self.settings_gui = SettingsGUI(container, self)
        self.settings_gui.grid(row=0, column=0, sticky="nsew")
        self.frames[SettingsGUI] = self.settings_gui

        tkinterApp.apps.append(self)

        self.show_frame(GraphGUI)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


def quit():
    app = tkinterApp.apps[0]
    app.quit()
    app.destroy()


class GraphGUI(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.first_time = True
        self.graph = Graph.Graph()
        self.canvas = FigureCanvasTkAgg(self.graph.fig, master=self)
        button_start = ttk.Button(
            master=self, text="Start", command=self.start_animation_window
        )

        infection_probability_slider = Slider(self, "Infection Probability:", 0)
        social_distancing_efficiency_slider = Slider(
            self, "Social Distancing Efficiency:", 1
        )
        social_distancing_radius_slider = Slider(
            self, "Social Distancing Radius:", 2, from_=1, to_=17, initial_value=10
        )
        infection_radius_slider = Slider(
            self, "Infection Radius:", 3, from_=1, to_=17, initial_value=8
        )

        button_goto_settings = ttk.Button(
            self, text="Settings", command=lambda: controller.show_frame(SettingsGUI)
        )

        nb_col = 10
        nb_row = 10

        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.canvas.get_tk_widget().grid(
            column=0,
            row=0,
            columnspan=5,
            rowspan=5,
            sticky=(N, S, E, W),
            pady=5,
            padx=5,
        )
        button_start.grid(column=0, row=7, pady=5, padx=5)

        social_distancing_efficiency_slider.frame.grid(
            column=6, row=0, columnspan=3, sticky="we", padx=5, pady=0
        )
        infection_probability_slider.frame.grid(
            column=6, row=1, columnspan=3, sticky="we", padx=5, pady=0
        )
        social_distancing_radius_slider.frame.grid(
            column=6, row=2, columnspan=3, sticky="we", padx=5, pady=0
        )
        infection_radius_slider.frame.grid(
            column=6, row=3, columnspan=3, sticky="we", padx=5, pady=0
        )

        button_goto_settings.grid(column=0, row=10, padx=5, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for i in range(int(nb_col / 2)):
            self.columnconfigure(i, weight=1)
        for i in range(int(nb_col / 2), nb_col):
            self.columnconfigure(i, weight=2)
        for i in range(nb_row):
            self.rowconfigure(i, weight=1)

    def start_animation_window(self):
        try:
            self.result[3] = 1  # setting exit flag to 1
        except:
            pass
        if self.first_time:
            self.result = multiprocessing.Array("d", 4)
            self.slider_values = multiprocessing.Array("d", 4)
            self.graph.mainfunc(self.result, self.canvas)
        else:
            self.graph.reset()
        self.first_time = False
        self.result[0] = 0  # time (frame nb)
        self.result[1] = 0  # infected percentage of population
        self.result[2] = 0  # susceptible percentage of population
        self.result[3] = 0  # animation window exit flag

        self.slider_values[0] = 0
        self.slider_values[1] = 0
        self.slider_values[2] = 10
        self.slider_values[3] = 8

        p2 = multiprocessing.Process(
            target=classes.main, args=(self.result, self.slider_values)
        )
        p2.start()


class SettingsGUI(tk.Frame):
    def __init__(self, parent, controller):

        nb_col = 10
        nb_row = 10

        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Settings", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button_goto_settings = ttk.Button(
            self, text="GraphGUI", command=lambda: controller.show_frame(GraphGUI)
        )
        button_goto_settings.grid(column=0, row=10, padx=5, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for i in range(int(nb_col / 2)):
            self.columnconfigure(i, weight=1)
        for i in range(int(nb_col / 2), nb_col):
            self.columnconfigure(i, weight=2)
        for i in range(nb_row):
            self.rowconfigure(i, weight=1)


class Slider:
    def __init__(
        self,
        parent,
        label,
        index_in_shared_arr,
        orientation=HORIZONTAL,
        length=250,
        from_=0,
        to_=100,
        initial_value=0,
    ):
        self.value = str(initial_value)
        self.frame = tk.Frame(parent)
        self.scale = ttk.Scale(
            self.frame,
            orient=orientation,
            length=length,
            from_=from_,
            to=to_,
            value=initial_value,
            command=self.update,
        )
        self.label_title = tk.Label(self.frame, text=label)
        self.label_value = tk.Label(self.frame, text=str(initial_value), width=6)
        self.label_title.configure(font=("Ariel", 14))
        self.label_value.configure(font=("Ariel", 11))

        self.index = index_in_shared_arr

        self.frame.grid(column=0, row=0)
        self.label_title.grid(column=0, row=0, columnspan=2, sticky="we")
        self.scale.grid(column=0, row=1, sticky="we")
        self.label_value.grid(column=1, row=1, sticky="we")

        self.frame.columnconfigure(0, weight=8)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

    def update(self, value):
        val = float(value)
        self.label_value["text"] = "{:.2f}".format(val)

        graph_gui = tkinterApp.apps[0].graph_gui
        if not graph_gui.first_time:
            graph_gui.slider_values[self.index] = val


if __name__ == "__main__":
    app = tkinterApp()
    tk.mainloop()
    try:
        app.graph_gui.result[3] = 1  # setting exit flag to 1
    except:
        pass
