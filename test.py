import random as rn
import math
from tkinter import Y
from turtle import circle
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

# TODO
# Add Parent Class Circles
# where infected, removed and susceptible are children classes each with an array keeping track of its objects


class Circle:
    radius = 5

    def __init__(this, x, y, vx, vy, infected=False, thickness=0):
        this.x = x
        this.y = y
        this.infected = infected
        this.thickness = thickness
        this.vx = vx
        this.vy = vy

    def move(circles):
        for c in circles:
            c.x += c.vx
            c.y += c.vy

    def draw(circles, surface):
        for c in circles:
            pyg.draw.circle(surface, RED if c.infected else BLUE,
                            (c.x, c.y), c.radius, c.thickness)

    def collision_boundary(circles, boundary):
        for c in circles:
            if(c.x - c.radius < boundary[0] or c.x + c.radius > boundary[2]):
                c.vx = c.vx * -1
            if(c.y - c.radius < boundary[1] or c.y + c.radius > boundary[3]):
                c.vy = c.vy * -1

    def collision(circles, nbcircles):
        for i in range(nbcircles):
            for j in range(nbcircles):
                c1 = circles[i]
                c2 = circles[j]
                if(i != j and c1.infected):
                    if(math.pow(c1.x - c2.x, 2) + math.pow(c1.y - c2.y, 2) < (c1.radius+c2.radius)*2):
                        c2.infected = True


def main():
    global FPSCLOCK, DISPLAYSURF
    pyg.init()
    FPSCLOCK = pyg.time.Clock()
    DISPLAYSURF = pyg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pyg.display.set_caption("Test")

    mainLoop()


def mainLoop():
    boundary = (50, 50, 700, 700)
    circles = []
    nb_circles = 100
    rn.seed(432)
    v = 2
    for i in range(nb_circles-1):
        angle = rn.random()*360
        circle = Circle(rn.random()*650 + 60,
                        rn.random()*650 + 60, math.cos(angle) * v, math.sin(angle) * v)
        circles.append(circle)
    circle = Circle(rn.random()*650 + 60,
                    rn.random()*650 + 60, math.cos(angle) * v, math.sin(angle) * v, True)  # adding one infected circle
    circles.append(circle)

    running = True
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False

        Circle.move(circles)
        Circle.collision_boundary(circles, boundary)
        Circle.collision(circles, nb_circles)

        DISPLAYSURF.fill(BLACK)

        pyg.draw.rect(DISPLAYSURF, WHITE, boundary, 2)
        Circle.draw(circles, DISPLAYSURF)

        pyg.display.update()
        FPSCLOCK.tick(FPS)

    pyg.quit()


def drawRect(x, y, w, h):
    rect = pyg.Rect(x, y, w, h)
    pyg.draw.rect(DISPLAYSURF, BLUE, rect)


main()
