import multiprocessing
import tkinter as tk
from tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import animation_window
import graph

def quit():
    root.quit()
    root.destroy()

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.geometry("1080x720+100+100")
root.wm_title("Covid19 Model")
content = tk.Frame(root)

canvas = FigureCanvasTkAgg(graph.Graph.fig, master=content)
button_quit = tk.Button(master=content, text="Quit", command=root.quit)

nb_col = 10
nb_row = 7

content.grid(column=0, row=0, sticky=(N, S, E, W))
canvas.get_tk_widget().grid(column=0, row=0, columnspan=5, rowspan=7, sticky=(N, S, E, W), pady=5, padx=5)
button_quit.grid(column=7, row=0, pady=5, padx=5)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

for i in range(5):
    content.columnconfigure(i, weight=1)
for i in range(5,10):
    content.columnconfigure(i, weight=2)
for i in range(nb_row):
    content.rowconfigure(i, weight=1)

if __name__ == '__main__':
    result = multiprocessing.Array('d', 2)
    p2 = multiprocessing.Process(target=animation_window.main, args=(True, result))
    p2.start()
    graph.Graph.mainfunc(result, canvas)
    tk.mainloop()
    p2.terminate()
