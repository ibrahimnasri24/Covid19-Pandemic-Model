from asyncio import subprocess
from pickle import TRUE
import Population

import tkinter as tk
from tkinter import font
import os
import subprocess
import shlex
from itertools import cycle

class Population_Window:
    def __init__(this, root):
        helv = font.Font(family='Helvetica', size=18, weight='bold')
        this.button = tk.Button(root, 
                                text="Start",
                                font=helv,
                                command=this.open_population_window).pack(side=tk.LEFT)
        this.start = False

    def open_population_window(this):
        if not this.start:
            Population.initialize(300)
        this.start = True

# def sub_p():
#     com = "python " + "Circles.py"
#     args = shlex.split(com)
#     print(args)
#     #p = subprocess.run(args)
#     os.execlp(args)

root = tk.Tk()
root.geometry('400x400')
pwin = Population_Window(root)
running = True

def on_closing():
    running = False
    root.destroy()

while(running):
    root.update()

    if(pwin.start):
        pwin.start = Population.population_loop()

    try:
        root.protocol("WM_DELETE_WINDOW", on_closing)
    except:
        running = False