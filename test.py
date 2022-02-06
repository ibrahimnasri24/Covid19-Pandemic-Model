import random as rn
import math
from tabnanny import check
import pygame as pyg
from pygame.locals import *
import numpy as np

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 800

infection_radius = 10
social_dist_radius = 15
rows, cols = (int(WINDOWWIDTH / social_dist_radius), int(WINDOWHEIGHT / social_dist_radius))
next_move_grid = [[[] for j in range(rows)] for i in range(cols)]

possible_collisions = []


BLUE = (41, 128, 185)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Class Circles


class Circle:
    radius = 5
    v_magnitude = 5

    def __init__(this, x, y, direction, infected=False, thickness=0):
        this.x = x
        this.y = y
        this.infected = infected
        this.thickness = thickness
        this.direction = direction
        this.v = [math.cos(math.radians(direction)) * this.v_magnitude, math.sin(math.radians(direction)) * this.v_magnitude]

    def move(circles):
        for c in circles:
            c.clear_grid()
            # rn.seed(c.x)
            # c.direction += rn.normalvariate(0, 0.7) * 7
            # c.direction = c.direction % 360
            # c.v[0] = math.cos(math.radians(c.direction)) * c.v_magnitude
            # c.v[1] = math.sin(math.radians(c.direction)) * c.v_magnitude
            v_norm = math.sqrt(c.v[0]**2 + c.v[1]**2)
            if v_norm > c.v_magnitude:
                c.v[0] *= c.v_magnitude / v_norm
                c.v[1] *= c.v_magnitude / v_norm
            c.x += c.v[0]
            c.y += c.v[1]
            c.locate_grid()
        Circle.social_dist()

    def social_dist():
        nb_possible_collisions = len(possible_collisions)
        # print(nb_possible_collisions)
        i = 0
        while(i < nb_possible_collisions):
            indices = possible_collisions[i]
            # print(indices)
            l = int(indices[0])
            m = int(indices[1])
            circles = next_move_grid[l][m]
            c1 = circles[0]
            n = circles.__len__()
            j=0
            for c2 in circles:
                if j > i:
                    if c1.infected:
                        print("infected")
                        if c1.dist_from_radius(c2, infection_radius) < 0:
                            print("infected")
                            c2.infected = True
                    if c1.dist_from_radius(c2, social_dist_radius) < 0:
                        n = [c2.x - c1.x, c2.y - c1.y] #normal vector
                        n_mag = math.sqrt(n[0]**2 + n[1]**2)
                        if(n_mag > 0):
                            # print("sc")
                            un = [n[0]/n_mag, n[1]/n_mag] #unit normal vector un = n/|n|
                            ut= [-un[1], un[0]] #unit tangential vector which is ut={-uny, unx}
                            #before collision
                            v1n = np.dot(un, c1.v)
                            v1t = np.dot(ut, c1.v)
                            v2n = np.dot(un, c2.v)
                            v2t = np.dot(ut, c2.v)
                            #after collision
                            v1ts = [v1t*ut[0], v1t* ut[1]]
                            v1ns = [v2n*un[0], v2n* un[1]]
                            v2ns = [v1n*un[0], v1n* un[1]]
                            v2ts = [v2t*ut[0], v2t* ut[1]]

                            c1.v = [v1ts[0] + v1ns[0], v1ts[1] + v1ns[1]]
                            c2.v = [v2ns[0] + v2ts[0], v2ns[1] + v2ts[1]]
                j += 1
            i += 1

    def draw(circles, surface):
        for c in circles:
            pyg.draw.circle(
                surface, RED if c.infected else BLUE, (c.x, c.y), c.radius, c.thickness
            )

    def collision_boundary(circles, boundary):
        reflection_strength = 0.5
        for c in circles:
            if c.x - c.radius < boundary[0]:
                c.v[0] += reflection_strength
            if c.x + c.radius > boundary[2]:
                c.v[0] -= reflection_strength 
            if c.y - c.radius < boundary[1]: 
                c.v[1] += reflection_strength
            if c.y + c.radius > boundary[3]:
                c.v[1] -= reflection_strength

    def locate_grid(this):
        circle_up_grid = int((this.y + social_dist_radius) / rows)
        circle_down_grid = int((this.y - social_dist_radius) / rows)
        circle_right_grid = int((this.x + social_dist_radius) / rows)
        circle_left_grid = int((this.x - social_dist_radius) / rows)
        if circle_up_grid == circle_down_grid and circle_right_grid == circle_left_grid:
            old_len = len(next_move_grid[circle_right_grid][circle_up_grid])
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_right_grid][circle_up_grid]) > 1:
                    possible_collisions.append([circle_right_grid, circle_up_grid])
        elif circle_right_grid == circle_left_grid:
            old_len = len(next_move_grid[circle_right_grid][circle_up_grid])
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_right_grid][circle_up_grid]) > 1:
                    possible_collisions.append([circle_right_grid, circle_up_grid])
            
            old_len = len(next_move_grid[circle_right_grid][circle_down_grid])
            next_move_grid[circle_right_grid][circle_down_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_right_grid][circle_down_grid]) > 1:
                    possible_collisions.append([circle_right_grid, circle_down_grid])
        elif circle_up_grid == circle_down_grid:
            old_len = len(next_move_grid[circle_right_grid][circle_up_grid])
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_right_grid][circle_up_grid]) > 1:
                    possible_collisions.append([circle_right_grid, circle_up_grid])
            
            old_len = len(next_move_grid[circle_left_grid][circle_up_grid])
            next_move_grid[circle_left_grid][circle_up_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_left_grid][circle_up_grid]) > 1:
                    possible_collisions.append([circle_left_grid, circle_up_grid])
        else:
            old_len = len(next_move_grid[circle_left_grid][circle_up_grid])
            next_move_grid[circle_left_grid][circle_up_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_left_grid][circle_up_grid]) > 1:
                    possible_collisions.append([circle_left_grid, circle_up_grid])
            
            old_len = len(next_move_grid[circle_right_grid][circle_up_grid])
            next_move_grid[circle_right_grid][circle_up_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_right_grid][circle_up_grid]) > 1:
                    possible_collisions.append([circle_right_grid, circle_up_grid])
            old_len = len(next_move_grid[circle_right_grid][circle_down_grid])
            next_move_grid[circle_right_grid][circle_down_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_right_grid][circle_down_grid]) > 1:
                    possible_collisions.append([circle_right_grid, circle_down_grid])

            old_len = len(next_move_grid[circle_left_grid][circle_down_grid])
            next_move_grid[circle_left_grid][circle_down_grid].append(this)
            if(old_len < 2):
                if len(next_move_grid[circle_left_grid][circle_down_grid]) > 1:
                    possible_collisions.append([circle_left_grid, circle_down_grid])
            # if len(possible_collisions) > 2:
                # print(len(possible_collisions))
        return

    def clear_grid(this):
        possible_collisions.clear()
        circle_up_grid = int((this.y + social_dist_radius) / rows)
        circle_down_grid = int((this.y - social_dist_radius) / rows)
        circle_right_grid = int((this.x + social_dist_radius) / rows)
        circle_left_grid = int((this.x - social_dist_radius) / rows)
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
    offset = 50
    boundary_virtual = (boundary[0] + offset, boundary[1] + offset, boundary[2] - offset + boundary[0], boundary[3] - offset + boundary[1])
    circles = []
    nb_circles = 50
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
        Circle.collision_boundary(circles, boundary_virtual)
        # new_infected_circles = Circle.infect_circles(infected_circles)
        # infected_circles = infected_circles + new_infected_circles
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
