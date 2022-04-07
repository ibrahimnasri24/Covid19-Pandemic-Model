from bz2 import compress
from matplotlib import pyplot as plt
from matplotlib import animation


class Graph:
    def __init__(self) -> None:
        self.fig = plt.figure()
        self.ax = plt.gca()
        self.ax.set_ylim(0, 100)

        self.x = []
        self.y = []
        self.y2 = []

    def reset(self):
        self.x.clear()
        self.y.clear()
        self.y2.clear()
        plt.clf()
        self.ax = plt.gca()
        self.ax.set_ylim(0, 100)

    def frames(self, result):
        yield result

    def animate(self, res):
        if res[0] == 0:
            self.x.append(0)
            self.y.append(0)
            self.y2.append(100)
        else:
            self.x.append(res[0])
            self.y.append(res[1])
            self.y2.append(res[2])

        if res[0] != 0:
            self.ax.set_xlim(0, res[0])
        else:
            self.ax.set_xlim(0, 1)

        return plt.plot(self.x, self.y, "r-", self.x, self.y2, "C7-")

    def mainfunc(self, result, canvas):
        anim = animation.FuncAnimation(
            self.fig, self.animate, frames=self.frames(result), interval=150, blit=False
        )
        canvas.draw()
