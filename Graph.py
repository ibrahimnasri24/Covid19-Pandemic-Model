from matplotlib import pyplot as plt
from matplotlib import animation

class Graph:
    def  __init__(self) -> None:
        self.fig = plt.figure()
        self.ax = plt.gca()
        self.ax.set_ylim(0,100)

        self.x = []
        self.y = []

    def reset(self):
        self.x.clear()
        self.y.clear()
        plt.clf()
        self.ax = plt.gca()
        self.ax.set_ylim(0,100)

    def frames(self, result):
        yield result

    def animate(self, res):
        self.x.append(res[0])
        self.y.append(res[1])

        if res[0] != 0:
            self.ax.set_xlim(0, res[0])
        else:
            self.ax.set_xlim(0, 1)

        # print(self.x)
        # print(self.y)

        return plt.plot(self.x, self.y, 'r-')

    def mainfunc(self, result, canvas):
        print("updating graph")
        anim = animation.FuncAnimation(self.fig, self.animate, frames=self.frames(result), interval=100)
        canvas.draw()