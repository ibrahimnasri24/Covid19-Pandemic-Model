import random as rn
import math
import pygame as pyg
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 800

infection_radius = 10
rows, cols = (int(WINDOWWIDTH / infection_radius), int(WINDOWHEIGHT / infection_radius))
next_move_grid = [[[] for j in range(rows)] for i in range(cols)]


BLUE = (41, 128, 185)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Class Circles


class Circle:
    radius = 5
    social_dist_radius = 10
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
            c.clear_grid()
            c.direction += rn.normalvariate(0, 0.7) * 7
            c.direction = c.direction % 360
            c.vx = math.cos(math.radians(c.direction)) * c.v
            c.vy = math.sin(math.radians(c.direction)) * c.v
            c.x += c.vx
            c.y += c.vy
            c.locate_grid()
            surrounding_circles = c.get_surrounding_circles()
            c.social_dist(surrounding_circles)

    # Seems like it's the wrong approach
    def social_dist(this, surrounding_circles):
        deflection_angle = 7
        for c in surrounding_circles:
            if this.dist_from_radius(c, this.social_dist_radius) < 0:
                this.v -=1
                # if this.y < c.y and this.x < c.x:
                #     deflection_angle *= -1
                # elif this.y > c.y and this.x > c.x:
                #     deflection_angle *= 1
                # this.direction += deflection_angle

    def draw(circles, surface):
        for c in circles:
            pyg.draw.circle(
                surface, RED if c.infected else BLUE, (c.x, c.y), c.radius, c.thickness
            )

    def collision_boundary(circles, boundary, boundary_virtual):
        for c in circles:
            reflection_angle = 10
            if c.x - c.radius - 2 < boundary[0] or c.x + c.radius + 2 > boundary[2]:
                c.direction = 180 - c.direction
            elif c.y - c.radius - 2 < boundary[1] or c.y + c.radius + 2 > boundary[3]:
                c.direction = 360 - c.direction
            elif c.x < boundary_virtual[0] and not (
                c.direction > 270 or c.direction < 90
            ):
                # reflection_angle = (
                #     reflection_angle if c.direction > 180 else reflection_angle * -1
                # )
                c.direction += reflection_angle
            elif c.x > boundary_virtual[2] and not (
                c.direction > 90 and c.direction < 270
            ):
                # reflection_angle = (
                #     reflection_angle if c.direction < 270 else reflection_angle * -1
                # )
                c.direction += reflection_angle
            elif c.y < boundary_virtual[1] and not (
                c.direction > 0 and c.direction < 180
            ):
                # reflection_angle = (
                #     reflection_angle if c.direction > 270 else reflection_angle * -1
                # )
                c.direction += reflection_angle
            elif c.y > boundary_virtual[3] and not (
                c.direction > 180 and c.direction < 360
            ):
                # reflection_angle = (
                #     reflection_angle if c.direction > 90 else reflection_angle * -1
                # )
                c.direction += reflection_angle

    def locate_grid(this):
        circle_up_grid = int((this.y + 5) / rows)
        circle_down_grid = int((this.y - 5) / rows)
        circle_right_grid = int((this.x + 5) / rows)
        circle_left_grid = int((this.x - 5) / rows)
        if circle_up_grid == circle_down_grid and circle_right_grid == circle_left_grid:
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
        elif circle_right_grid == circle_left_grid:
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            next_move_grid[circle_right_grid][circle_down_grid].append(this)
        elif circle_up_grid == circle_down_grid:
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            next_move_grid[circle_left_grid][circle_up_grid].append(this)
        else:
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            next_move_grid[circle_right_grid][circle_down_grid].append(this)
            next_move_grid[circle_left_grid][circle_up_grid].append(this)
            next_move_grid[circle_left_grid][circle_down_grid].append(this)
        return

    def clear_grid(this):
        circle_up_grid = int((this.y + 5) / rows)
        circle_down_grid = int((this.y - 5) / rows)
        circle_right_grid = int((this.x + 5) / rows)
        circle_left_grid = int((this.x - 5) / rows)
        if circle_up_grid == circle_down_grid and circle_right_grid == circle_left_grid:
            next_move_grid[circle_right_grid][circle_up_grid].remove(this)
        elif circle_right_grid == circle_left_grid:
            next_move_grid[circle_right_grid][circle_up_grid].remove(this)
            next_move_grid[circle_right_grid][circle_down_grid].remove(this)
        elif circle_up_grid == circle_down_grid:
            next_move_grid[circle_right_grid][circle_up_grid].remove(this)
            next_move_grid[circle_left_grid][circle_up_grid].remove(this)
        else:
            next_move_grid[circle_right_grid][circle_up_grid].remove(this)
            next_move_grid[circle_right_grid][circle_down_grid].remove(this)
            next_move_grid[circle_left_grid][circle_up_grid].remove(this)
            next_move_grid[circle_left_grid][circle_down_grid].remove(this)
        return

    def infect_circles(infected_circles):
        new_infected_circles = []
        for infected_circle in infected_circles:
            new_infected_circles = new_infected_circles + infected_circle.infect()
        return new_infected_circles

    def infect(this):
        new_infected = []
        surrounding_circles = this.get_surrounding_circles()
        for surrounding_circle in surrounding_circles:
            if not surrounding_circle.infected:
                if this.dist_from_radius(surrounding_circle, infection_radius) < 0:
                    surrounding_circle.infected = True
                    new_infected.append(surrounding_circle)
        return new_infected

    def get_surrounding_circles(this):
        surrounding_circles = []
        circle_grid_x = int((this.x) / rows)
        circle_grid_y = int((this.y) / rows)
        if (
            circle_grid_x > 0
            and circle_grid_x < rows - 1
            and circle_grid_y > 0
            and circle_grid_y < rows - 1
        ):
            for i in range(3):
                for j in range(3):
                    surrounding_circles += next_move_grid[circle_grid_x - 1 + i][
                        circle_grid_y - 1 + j
                    ]
        return surrounding_circles

    def dist_from_radius(this, circle, radius):
        return ((this.x - circle.x) ** 2 + (this.y - circle.y) ** 2) - (radius + circle.radius) ** 2


def main():
    global FPSCLOCK, DISPLAYSURF
    pyg.init()
    FPSCLOCK = pyg.time.Clock()
    DISPLAYSURF = pyg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pyg.display.set_caption("Test")
    mainLoop()


def mainLoop():
    boundary = (50, 50, 700, 700)
    boundary_virtual = (100, 100, 685, 685)
    circles = []
    nb_circles = 150
    rn.seed(432)
    for i in range(nb_circles - 1):
        direction = rn.random() * 360
        circle = Circle(
            rn.random() * (boundary_virtual[2] - 150) + 120,
            rn.random() * (boundary_virtual[3] - 150) + 120,
            direction,
        )
        circle.locate_grid()
        circles.append(circle)

    circle = Circle(
        rn.random() * (boundary_virtual[2] - 150) + 120,
        rn.random() * (boundary_virtual[3] - 150) + 120,
        direction,
        True,
    )
    circle.locate_grid()
    infected_circles = []
    infected_circles.append(circle)  # adding one infected circle
    circles.append(circle)

    running = True
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False

        Circle.move(circles)
        Circle.collision_boundary(circles, boundary, boundary_virtual)
        new_infected_circles = Circle.infect_circles(infected_circles)
        infected_circles = infected_circles + new_infected_circles
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
