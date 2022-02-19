import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use('seaborn-pastel')


fig = plt.figure()
ax = plt.axes(xlim=(0, 4), ylim=(-2, 2))
line, = ax.plot([], [], "r-")


x=[]
y=[]
def init():
    line.set_data([], [])
    return line,
def animate(i):
    x.append(i)
    # y.append(np.sin(2 * np.pi * (i- 0.01 * i)))
    if i <2 :
        aux=0
    if i < 20:
        y.append(2**i)
        ax.set_ylim(0, 2**i + 10)
        aux = y[i-1]
    else:
        y.append(aux * 2**-i)
        print(aux)

    line.set_data(x, y)
    ax.set_xlim(0, i)
    return line,

anim = FuncAnimation(fig, animate, init_func=init, frames=100, interval = 100)
plt.show()