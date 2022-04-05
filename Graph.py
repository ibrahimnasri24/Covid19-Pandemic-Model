from matplotlib import pyplot as plt
from matplotlib import animation

class Graph:

    fig = plt.figure()
    ax = plt.gca()
    ax.set_ylim(0,100)

    x = []
    y = []

    def reset():
        Graph.x = []
        Graph.y = []

    def frames(result):
        yield result

    def animate(res):
        Graph.x.append(res[0])
        Graph.y.append(res[1])

        if res[0] != 0:
            Graph.ax.set_xlim(0, res[0])
        else:
            Graph.ax.set_xlim(0, 1)

        # print(Graph.x)
        # print(Graph.y)

        return plt.plot(Graph.x, Graph.y, 'r-')

    def mainfunc(result, canvas):
        print("updating graph")
        anim = animation.FuncAnimation(Graph.fig, Graph.animate, frames=Graph.frames(result), interval=100)
        canvas.draw()