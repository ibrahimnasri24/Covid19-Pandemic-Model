from asyncio import subprocess
from pickle import TRUE
import Population as P

import tkinter as tk
from tkinter import font
import os
import subprocess
import shlex
from itertools import cycle


class Population_Window:

    def __init__(self):
        self.start = False

    def open_population_window(this):
        if not this.start:
            this.anim_w = P.AnimationWindow()
            this.anim_w.initialize()
        this.start = True

# def sub_p():
#     com = "python " + "Circles.py"
#     args = shlex.split(com)
#     print(args)
#     #p = subprocess.run(args)
#     os.execlp(args)

root = tk.Tk()
root.title("Covid 19 Model")
root.geometry("1080x720")

pwin = Population_Window()

helv = font.Font(family="Helvetica", size=18, weight="bold")
button = tk.Button(
    root, text="Start", font=helv, command=pwin.open_population_window
).pack(side=tk.LEFT)

running = True


def on_closing():
    running = False
    root.destroy()


while running:
    root.update()

    if pwin.start:
        pwin.start = pwin.anim_w.main_loop(P.Circle)

    try:
        root.protocol("WM_DELETE_WINDOW", on_closing)
    except:
        running = False
