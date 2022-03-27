from matplotlib import pyplot as plt
from matplotlib import animation

class Graph:
    def frames(result):
        # while True:
        yield result

    fig = plt.figure()
    ax = plt.gca()
    ax.set_ylim(0,100)

    x = []
    y = []

    def animate(res):
        Graph.x.append(res[0])
        Graph.y.append(res[1])
        Graph.ax.set_xlim(0, res[0])
        return plt.plot(Graph.x, Graph.y, 'r-')

    def mainfunc(result, canvas):
        anim = animation.FuncAnimation(Graph.fig, Graph.animate, frames=Graph.frames(result), interval=100)
        canvas.draw()