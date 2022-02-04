import random as rn
import math
import pygame as pyg
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 800


BLUE = (41, 128, 185)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class Circle:
    radius = 5
    v = 2
    vx = 0
    vy = 0

    def __init__(this, x, y, direction, infected=False, thickness=0):
        this.x = x
        this.y = y
        this.infected = infected
        this.thickness = thickness
        this.direction = direction

    def move(circles):
        for c in circles:
            rn.seed(c.x)
            c.direction += rn.normalvariate(0, 0.7)*7
            c.direction = c.direction % 360
            c.vx = math.cos(math.radians(c.direction))*c.v
            c.vy = math.sin(math.radians(c.direction))*c.v
            c.x += c.vx
            c.y += c.vy

    def draw(circles, surface):
        for c in circles:
            pyg.draw.circle(surface, RED if c.infected else BLUE,
                            (c.x, c.y), c.radius, c.thickness)

    def collision_boundary(circles, boundary):
        for c in circles:
            if c.x < boundary[0] and not (c.direction > 300 or c.direction < 60):
                c.direction = c.direction + 10
            if c.x > boundary[2] and not (c.direction > 120 and c.direction < 240):
                c.direction = c.direction + 10
            if c.y < boundary[1] and not (c.direction > 30 and c.direction < 150):
                c.direction = c.direction + 10
            if c.y > boundary[3] and not (c.direction > 210 and c.direction < 230):
                c.direction = c.direction + 10

    def collision(circles, nbcircles):
        for i in range(nbcircles):
            for j in range(nbcircles):
                c1 = circles[i]
                c2 = circles[j]
                if(i != j and c1.infected):
                    if((c1.x - c2.x)**2 + (c1.y - c2.y)**2 < ((c1.radius+c2.radius)*2)**2):
                        c2.infected = True


def main():
    global FPSCLOCK, DISPLAYSURF
    pyg.init()
    FPSCLOCK = pyg.time.Clock()
    DISPLAYSURF = pyg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pyg.display.set_caption("Test")

    mainLoop()


def mainLoop():
    time = 0
    frame = 0
    boundary = (50, 50, 700, 700)
    boundary_virtual = (100, 100, 670, 670)
    circles = []
    nb_circles = 150
    for i in range(nb_circles-1):
        direction = rn.random()*360
        circle = Circle(rn.random()*570 + 100,
                        rn.random()*570 + 100, direction)
        circles.append(circle)
    direction = rn.random()*360
    circle = Circle(rn.random()*570 + 100, rn.random()*570 +
                    100, True, direction)  # adding one infected circle
    circles.append(circle)

    running = True
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False

        Circle.move(circles)
        Circle.collision_boundary(circles, boundary_virtual)
        Circle.collision(circles, nb_circles)

        DISPLAYSURF.fill(BLACK)

        pyg.draw.rect(DISPLAYSURF, WHITE, boundary, 2)
        Circle.draw(circles, DISPLAYSURF)

        pyg.display.update()
        FPSCLOCK.tick(FPS)
        frame += 1
        if(frame % FPS == 0):
            time += 1
            print(time)

    pyg.quit()


def drawRect(x, y, w, h):
    rect = pyg.Rect(x, y, w, h)
    pyg.draw.rect(DISPLAYSURF, BLUE, rect)
