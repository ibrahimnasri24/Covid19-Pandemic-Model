import multiprocessing
import tkinter as tk
from tkinter import ttk, font
from tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import AnimationWindow
import Graph


LARGEFONT = ("Verdana", 35)


class tkinterApp(tk.Tk):

    apps = []

    def __init__(this, *args, **kwargs):

        tk.Tk.__init__(this, *args, **kwargs)
        this.defaultFont = font.nametofont("TkDefaultFont")
        this.defaultFont.configure(family="Ariel", size=14)

        this.protocol("WM_DELETE_WINDOW", quit)
        this.geometry("1110x1000+0+0")
        this.wm_title("Covid19 Model")

        container = tk.Frame(this)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        this.frames = {}

        this.graph_gui = GraphGUI(container, this)
        this.graph_gui.grid(row=0, column=0, sticky="nsew")
        this.frames[GraphGUI] = this.graph_gui

        this.settings_gui = SettingsGUI(container, this)
        this.settings_gui.grid(row=0, column=0, sticky="nsew")
        this.frames[SettingsGUI] = this.settings_gui

        tkinterApp.apps.append(this)

        this.show_frame(GraphGUI)

    def show_frame(this, cont):
        frame = this.frames[cont]
        frame.tkraise()


def quit():
    app = tkinterApp.apps[0]
    app.quit()
    app.destroy()


class GraphGUI(tk.Frame):
    def __init__(this, parent, controller):
        tk.Frame.__init__(this, parent)

        this.first_time = True
        this.graph = Graph.Graph()
        this.canvas = FigureCanvasTkAgg(this.graph.fig, master=this)
        button_start = ttk.Button(
            master=this, text="Start", command=this.start_animation_window
        )

        infection_probability_slider = Slider(
            this, "Infection Probability:", 0, True, from_=0, to_=1, initial_value=1
        )
        social_distancing_efficiency_slider = Slider(
            this,
            "Social Distancing Efficiency:",
            1,
            True,
            from_=0,
            to_=1,
            initial_value=1,
        )
        social_distancing_radius_slider = Slider(
            this,
            "Social Distancing Radius:",
            2,
            False,
            from_=1,
            to_=17,
            initial_value=10,
        )
        infection_radius_slider = Slider(
            this, "Infection Radius:", 3, False, from_=1, to_=17, initial_value=8
        )
        percentage_social_distancing_slider = Slider(
            this,
            "Percentage of Population\nThat are Social Distancing:",
            4,
            True,
            from_=0,
            to_=1,
            initial_value=0.8,
        )

        numeric_input_vaccinate = NumericInput(
            this,
            "Percantage of\nPopulation to Vaccinate:",
            initial_value=0,
        )

        button_goto_settings = ttk.Button(
            this, text="Settings", command=lambda: controller.show_frame(SettingsGUI)
        )

        nb_col = 10
        nb_row = 10

        this.grid(column=0, row=0, sticky=(N, S, E, W))
        this.canvas.get_tk_widget().grid(
            column=0,
            row=0,
            columnspan=5,
            rowspan=5,
            sticky=(N, S, E, W),
            pady=5,
            padx=5,
        )

        infection_radius_slider.frame.grid(
            column=6, row=0, columnspan=3, sticky="we", padx=5, pady=0
        )
        infection_probability_slider.frame.grid(
            column=6, row=1, columnspan=3, sticky="we", padx=5, pady=0
        )
        social_distancing_radius_slider.frame.grid(
            column=6, row=2, columnspan=3, sticky="we", padx=5, pady=0
        )
        social_distancing_efficiency_slider.frame.grid(
            column=6, row=3, columnspan=3, sticky="we", padx=5, pady=0
        )
        percentage_social_distancing_slider.frame.grid(
            column=6, row=4, columnspan=3, sticky="we", padx=5, pady=0
        )

        numeric_input_vaccinate.frame.grid(column=6, row=5, columnspan=3, sticky="we")

        button_start.grid(column=0, row=7, pady=5, padx=5)

        button_goto_settings.grid(column=0, row=10, padx=5, pady=5)

        this.columnconfigure(0, weight=1)
        this.rowconfigure(0, weight=1)

        for i in range(int(nb_col / 2)):
            this.columnconfigure(i, weight=1)
        for i in range(int(nb_col / 2), nb_col):
            this.columnconfigure(i, weight=2)
        for i in range(nb_row):
            this.rowconfigure(i, weight=1)

    def start_animation_window(this):
        try:
            this.result[3] = 1  # setting exit flag to 1
        except:
            pass
        if this.first_time:
            this.result = multiprocessing.Array("d", 4)
            this.slider_values = multiprocessing.Array("d", 6)
            this.vaccination_control = multiprocessing.Array("d", 2)
            this.travel_control = multiprocessing.Array("b", 1)
            this.graph.mainfunc(this.result, this.canvas)
        else:
            this.graph.reset()
        this.first_time = False
        this.result[0] = 0  # time (frame nb)
        this.result[1] = 0  # infected percentage of population
        this.result[2] = 0  # susceptible percentage of population
        this.result[3] = 0  # animation window exit flag

        this.slider_values[0] = float(Slider.sliders[0].value)
        this.slider_values[1] = float(Slider.sliders[1].value)
        this.slider_values[2] = float(Slider.sliders[2].value)
        this.slider_values[3] = float(Slider.sliders[3].value)
        this.slider_values[4] = float(Slider.sliders[4].value)

        this.vaccination_control[0] = 0  # Bool to signal vaccination
        this.vaccination_control[1] = 0  # Vaccination Percentage

        travel = True
        this.travel_control[0] = travel

        p2 = multiprocessing.Process(
            target=AnimationWindow.main,
            args=(
                this.result,
                this.slider_values,
                this.vaccination_control,
                this.travel_control,
            ),
        )
        p2.start()

    def Vaccinate(this):
        percentage_to_vaccinate = float(
            NumericInput.numeric_inputs[0].numeric_input_val.get()
        )
        try:
            if (
                percentage_to_vaccinate > 100
                or percentage_to_vaccinate < 0
                or this.vaccination_control[0] == 1
            ):
                return
            this.vaccination_control[0] = 1
            this.vaccination_control[1] = percentage_to_vaccinate
        except:
            pass


class SettingsGUI(tk.Frame):
    def __init__(this, parent, controller):

        nb_col = 10
        nb_row = 10

        tk.Frame.__init__(this, parent)
        label = ttk.Label(this, text="Settings", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button_goto_settings = ttk.Button(
            this, text="GraphGUI", command=lambda: controller.show_frame(GraphGUI)
        )
        button_goto_settings.grid(column=0, row=10, padx=5, pady=5)

        this.columnconfigure(0, weight=1)
        this.rowconfigure(0, weight=1)

        for i in range(int(nb_col / 2)):
            this.columnconfigure(i, weight=1)
        for i in range(int(nb_col / 2), nb_col):
            this.columnconfigure(i, weight=2)
        for i in range(nb_row):
            this.rowconfigure(i, weight=1)


class NumericInput:
    numeric_inputs = []

    def __init__(
        this,
        parent,
        label,
        from_=0,
        to_=100,
        initial_value=0,
    ):
        this.value = initial_value
        this.frame = tk.Frame(parent)
        this.numeric_input_val = StringVar(value="0")
        numeric_input_label = ttk.Label(this.frame, text=label, width=20)
        numeric_input_label.configure(font=("Ariel", 14))

        numeric_input = ttk.Spinbox(
            this.frame,
            from_=from_,
            to=to_,
            textvariable=this.numeric_input_val,
            width=7,
        )
        numeric_input.configure(font=("Ariel", 14))
        button_vaccinate = ttk.Button(
            this.frame,
            text="Vaccinate",
            command=parent.Vaccinate,
            width=7,
        )
        this.frame.grid(column=0, row=0)
        numeric_input_label.grid(column=0, row=0, rowspan=2, sticky="w", padx=5, pady=5)
        numeric_input.grid(column=1, row=0, sticky="we", padx=20, pady=5)
        button_vaccinate.grid(column=1, row=1, sticky="we", padx=20, pady=5)

        this.frame.columnconfigure(0, weight=1)
        this.frame.columnconfigure(1, weight=1)
        this.frame.rowconfigure(0, weight=1)
        this.frame.rowconfigure(1, weight=1)

        NumericInput.numeric_inputs.append(this)


class Slider:
    sliders = []

    def __init__(
        this,
        parent,
        label,
        index_in_shared_arr,
        percentage,
        orientation=HORIZONTAL,
        length=250,
        from_=0,
        to_=100,
        initial_value=0,
    ):
        this.value = str(initial_value)
        this.frame = tk.Frame(parent)
        this.scale = ttk.Scale(
            this.frame,
            orient=orientation,
            length=length,
            from_=from_,
            to=to_,
            value=initial_value,
            command=this.update,
        )
        this.percentage = percentage
        this.label_title = tk.Label(this.frame, text=label)
        lb_val = (
            "{:.1f}".format(initial_value)
            if not this.percentage
            else "{:.0f} %".format(initial_value * 100)
        )
        this.label_value = tk.Label(this.frame, text=str(lb_val), width=6)
        this.label_title.configure(font=("Ariel", 14))
        this.label_value.configure(font=("Ariel", 11))

        this.index = index_in_shared_arr

        this.frame.grid(column=0, row=0)
        this.label_title.grid(column=0, row=0, columnspan=2, sticky="w", pady=5)
        this.scale.grid(column=0, row=1, sticky="we")
        this.label_value.grid(column=1, row=1, sticky="we")

        this.frame.columnconfigure(0, weight=8)
        this.frame.columnconfigure(1, weight=1)
        this.frame.rowconfigure(0, weight=1)
        this.frame.rowconfigure(1, weight=1)
        Slider.sliders.append(this)

    def update(this, value):
        val = float(value)
        this.value = val
        this.label_value["text"] = (
            "{:.1f}".format(val)
            if not this.percentage
            else "{:.0f} %".format(val * 100)
        )

        graph_gui = tkinterApp.apps[0].graph_gui
        if not graph_gui.first_time:
            graph_gui.slider_values[this.index] = val


class ComboBox:
    comboBoxes = []

    def __init__(this, parent, label, values: list):
        this.frame = tk.Frame(parent)

        travelVar = StringVar()
        travel = ttk.Combobox(this.frame, textvariable=travelVar)
        travel["values"] = ("Without Travelling", "With Traveling")
        travel.bind("<<ComboboxSelected>>", ComboBox.comboBoxSelectionChanged)

        ComboBox.comboBoxes.append(this)

    def comboBoxSelectionChanged():
        pass


if __name__ == "__main__":
    app = tkinterApp()
    tk.mainloop()
    try:
        app.graph_gui.result[3] = 1  # setting exit flag to 1
    except:
        pass
