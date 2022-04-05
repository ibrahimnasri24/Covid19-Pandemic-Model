import random as rn
import math
import pygame as pyg
from pygame.locals import *
import numpy as np
import time as t

BLUE = (41, 128, 185)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (30, 30, 30)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class AnimationWindow:
    frame = 0
    running= True

    FPS = 60
    window_width = 800
    window_height = 800

    population = 200
    infection_radius = 8
    social_distance_radius = 10
    percentage_of_population_social_distancing = 0.5

    def __init__(
        this,
        boundary=(50, 50, 700, 700),
    ):
        this.boundary = boundary

    def initialize(this):
        Circle.circles.clear()
        global FPSCLOCK, DISPLAYSURF
        pyg.init()
        FPSCLOCK = pyg.time.Clock()
        DISPLAYSURF = pyg.display.set_mode(
            (AnimationWindow.window_width, AnimationWindow.window_height)
        )
        pyg.display.set_caption("Test")

        rn.seed(t.time())
        social_distancing = True
        for i in range(AnimationWindow.population - 1):
            if (
                i
                > AnimationWindow.percentage_of_population_social_distancing
                * AnimationWindow.population
            ):
                social_distancing = False
            Circle(
                rn.random() * (this.boundary[2] - 150) + 120,
                rn.random() * (this.boundary[3] - 150) + 120,
                rn.random() * 360,
                i,
                social_distancing,
            )

        infected = Circle(
            rn.random() * (this.boundary[2] - 150) + 120,
            rn.random() * (this.boundary[3] - 150) + 120,
            rn.random() * 360,
            AnimationWindow.population - 1,
            False,
            True,
        )

        InfectionCircle(infected.id)

        Circle.grid = [[[] for j in range(Circle.rows)] for i in range(Circle.cols)]

    def main_loop(this, Circle):
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                return False

        DISPLAYSURF.fill(BLACK)

        pyg.draw.rect(DISPLAYSURF, WHITE, this.boundary, 2)
        Circle.draw(Circle.circles, DISPLAYSURF)
        InfectionCircle.draw(DISPLAYSURF)
        # drawGrid()

        Circle.move(Circle.circles)
        Circle.collision()
        Circle.collision_boundary(Circle.circles, this.boundary)

        pyg.display.update()
        FPSCLOCK.tick(AnimationWindow.FPS)

        AnimationWindow.frame+=1

        return True

class Circle:
    radius = 5
    v_magnitude = 1.2

    grid_size = 2 * AnimationWindow.social_distance_radius + 4

    cols = int(AnimationWindow.window_width / grid_size)
    rows = int(AnimationWindow.window_height / grid_size)

    grid = []

    possible_collisions = []

    circles = []

    def __init__(
        this, x, y, direction, id, social_distancing, infected=False, thickness=0
    ):
        this.x = x
        this.y = y
        this.id = id
        this.social_distancing = social_distancing
        this.infected = infected
        this.thickness = thickness
        this.direction = direction
        this.v = [
            math.cos(math.radians(direction)) * Circle.v_magnitude,
            math.sin(math.radians(direction)) * Circle.v_magnitude,
        ]
        this.grid_cells = []
        this.budge_x = 0
        this.budge_y = 0
        this.circles_indexes_in_collision = []

        Circle.circles.append(this)

    def move(anim_w):
        for i in range(Circle.cols):
            for j in range(Circle.rows):
                Circle.grid[i][j] = []

        for c in Circle.circles:
            c.grid_cells.clear()
            c.circles_indexes_in_collision.clear()
            # rn.seed(c.x)
            wander_step = rn.normalvariate(0, 0.2) * Circle.v_magnitude * 0.55
            if rn.random() > 0.5:
                c.v[0] += wander_step
            else:
                c.v[1] += wander_step
            v_norm = math.sqrt(c.v[0] ** 2 + c.v[1] ** 2)
            c.v[0] *= c.v_magnitude / v_norm
            c.v[1] *= c.v_magnitude / v_norm
            c.x += c.v[0] + c.budge_x
            c.y += c.v[1] + c.budge_y

            c.budge_x = 0
            c.budge_y = 0

            c.locate_circle_in_grid(Circle.grid)

            if c.infected:
                pass

        Circle.get_possible_collisions()

    def draw(circles, surface):
        for c in circles:
            pyg.draw.circle(
                surface, RED if c.infected else BLUE, (c.x, c.y), c.radius, c.thickness
            )

    def collision_boundary(circles, boundary):
        offset = 70
        reflection_strength = 0.7
        for c in circles:
            if c.x - c.radius < boundary[0] + offset:
                c.v[0] += reflection_strength
            if c.x + c.radius > boundary[2] + boundary[0] - offset:
                c.v[0] -= reflection_strength
            if c.y - c.radius < boundary[1] + offset:
                c.v[1] += reflection_strength
            if c.y + c.radius > boundary[3] + boundary[1] - offset:
                c.v[1] -= reflection_strength

    def collision():
        for cell_ind in Circle.possible_collisions:
            pos_col_arr = Circle.grid[cell_ind[0]][cell_ind[1]]
            n = len(pos_col_arr)
            j = 0
            for c1 in pos_col_arr:
                for c2 in pos_col_arr[j + 1 :]:

                    if ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (
                        2 * (AnimationWindow.infection_radius)
                    ) ** 2:
                        if c1.infected:
                            if not c2.infected:
                                InfectionCircle(c2.id) 
                                c2.infected = True
                        elif c2.infected:
                            if not c1.infected:
                                InfectionCircle(c1.id)
                                c1.infected = True

                    already_collided_in_this_frame = (
                        c2.id in c1.circles_indexes_in_collision
                    ) or (c1.id in c2.circles_indexes_in_collision)
                    both_of_them_not_social_distancing = (
                        not c1.social_distancing and not c2.social_distancing
                    )

                    if (
                        ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2)
                        < (2 * (AnimationWindow.social_distance_radius)) ** 2
                        and not already_collided_in_this_frame
                        and not both_of_them_not_social_distancing
                    ):
                        # if(rn.random() < 0.8):
                        #     break

                        c1.circles_indexes_in_collision.append(c2.id)
                        c2.circles_indexes_in_collision.append(c1.id)

                        n = [c2.x - c1.x, c2.y - c1.y]  # normal vector
                        n_mag = math.sqrt(n[0] ** 2 + n[1] ** 2)
                        if n_mag == 0:
                            break
                        un = [
                            n[0] / n_mag,
                            n[1] / n_mag,
                        ]  # unit normal vector un = n/|n|
                        ut = [
                            -un[1],
                            un[0],
                        ]  # unit tangential vector which is ut={-uny, unx}

                        # before collision
                        v1n = np.dot(un, c1.v)
                        v1t = np.dot(ut, c1.v)
                        v2n = np.dot(un, c2.v)
                        v2t = np.dot(ut, c2.v)
                        # after collision
                        v1ts = [v1t * ut[0], v1t * ut[1]]
                        v1ns = [v2n * un[0], v2n * un[1]]
                        v2ns = [v1n * un[0], v1n * un[1]]
                        v2ts = [v2t * ut[0], v2t * ut[1]]

                        c1.v = [v1ts[0] + v1ns[0], v1ts[1] + v1ns[1]]
                        c2.v = [v2ns[0] + v2ts[0], v2ns[1] + v2ts[1]]

                        over_collision = (
                            (2 * AnimationWindow.social_distance_radius) - n_mag
                        ) / 2
                        budge_x = n[0] * (over_collision / n_mag)
                        budge_y = n[1] * (over_collision / n_mag)

                        c1.budge_x = -budge_x
                        c1.budge_y = -budge_y

                        c2.budge_x = budge_x
                        c2.budge_y = budge_y
                j += 1

    def locate_circle_in_grid(c, grid):

        center_loc_in_grid = (int(c.x / Circle.grid_size), int(c.y / Circle.grid_size))
        grid[center_loc_in_grid[0]][center_loc_in_grid[1]].append(c)
        c.grid_cells.append(center_loc_in_grid)

        if (
            distance(
                c.x,
                c.y,
                ((center_loc_in_grid[0]) * Circle.grid_size),
                ((center_loc_in_grid[1]) * Circle.grid_size),
            )
            < AnimationWindow.social_distance_radius
        ):
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]].append(c)
            grid[center_loc_in_grid[0]][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1] - 1].append(c)

            c.grid_cells.append((center_loc_in_grid[0] - 1, center_loc_in_grid[1]))
            c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] - 1, center_loc_in_grid[1] - 1))

        elif (
            distance(
                c.x,
                c.y,
                ((center_loc_in_grid[0]) * Circle.grid_size),
                ((center_loc_in_grid[1] + 1) * Circle.grid_size),
            )
            < AnimationWindow.social_distance_radius
        ):
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]].append(c)
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1] + 1].append(c)
            grid[center_loc_in_grid[0]][center_loc_in_grid[1] + 1].append(c)

            c.grid_cells.append((center_loc_in_grid[0] - 1, center_loc_in_grid[1]))
            c.grid_cells.append((center_loc_in_grid[0] - 1, center_loc_in_grid[1] + 1))
            c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] + 1))

        elif (
            distance(
                c.x,
                c.y,
                ((center_loc_in_grid[0] + 1) * Circle.grid_size),
                ((center_loc_in_grid[1] + 1) * Circle.grid_size),
            )
            < AnimationWindow.social_distance_radius
        ):
            grid[center_loc_in_grid[0]][center_loc_in_grid[1] + 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1] + 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]].append(c)

            c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] + 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1] + 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1]))

        elif (
            distance(
                c.x,
                c.y,
                ((center_loc_in_grid[0] + 1) * Circle.grid_size),
                ((center_loc_in_grid[1]) * Circle.grid_size),
            )
            < AnimationWindow.social_distance_radius
        ):
            grid[center_loc_in_grid[0]][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]].append(c)

            c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1]))

        else:
            if (
                c.x - AnimationWindow.social_distance_radius
                < center_loc_in_grid[0] * Circle.grid_size
            ):
                grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]].append(c)
                c.grid_cells.append((center_loc_in_grid[0] - 1, center_loc_in_grid[1]))

            if (
                c.y - AnimationWindow.social_distance_radius
                < center_loc_in_grid[1] * Circle.grid_size
            ):
                grid[center_loc_in_grid[0]][center_loc_in_grid[1] - 1].append(c)
                c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] - 1))

            if (
                c.y + AnimationWindow.social_distance_radius
                > (center_loc_in_grid[1] + 1) * Circle.grid_size
            ):
                grid[center_loc_in_grid[0]][center_loc_in_grid[1] + 1].append(c)
                c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] + 1))

            if (
                c.x + AnimationWindow.social_distance_radius
                > (center_loc_in_grid[0] + 1) * Circle.grid_size
            ):
                grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]].append(c)
                c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1]))

    def get_possible_collisions():
        Circle.possible_collisions.clear()
        i = 0
        for i in range(Circle.rows):
            j = 0
            for j in range(Circle.cols):
                leng = len(Circle.grid[i][j])
                if leng > 1:
                    Circle.possible_collisions.append((i, j))

class InfectionCircle:
    infected_circles = []
    end_frame = 60
    infection_circle_radius = 17
    # frame_step = (AnimationWindow.infection_radius - Circle.radius) / AnimationWindow.FPS
    radius_step = (infection_circle_radius - Circle.radius) / AnimationWindow.FPS
    color_step = int((255 - 0) / AnimationWindow.FPS)

    def __init__(this, id):
        this.id = id
        this.radius = Circle.radius
        this.alpha = 255
        this.surface = pyg.Surface((InfectionCircle.infection_circle_radius*2,InfectionCircle.infection_circle_radius*2), pyg.SRCALPHA)
        this.frame = 0
        InfectionCircle.infected_circles.append(this)

    def draw(main_surface):
        for infected in InfectionCircle.infected_circles:
            c = Circle.circles[infected.id]
            infected.alpha -= InfectionCircle.color_step
            pyg.draw.circle(
                infected.surface, (*RED, infected.alpha), (InfectionCircle.infection_circle_radius, InfectionCircle.infection_circle_radius), infected.radius + (InfectionCircle.radius_step * infected.frame), 5
            )
            main_surface.blit(infected.surface, (c.x - InfectionCircle.infection_circle_radius, c.y - InfectionCircle.infection_circle_radius))
            infected.frame += 1
            if(infected.frame > InfectionCircle.end_frame):
                infected.frame = 0
                infected.alpha = 255

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def drawGrid():
    for i in range(Circle.cols):
        pyg.draw.line(
            DISPLAYSURF, GREY, (i * Circle.grid_size, 0), (i * Circle.grid_size, 800)
        )
    for i in range(Circle.rows):
        pyg.draw.line(
            DISPLAYSURF, GREY, (0, i * Circle.grid_size), (800, i * Circle.grid_size)
        )

def main(t, result):
    print("openning window")
    anim_w = AnimationWindow()
    anim_w.initialize()
    while(AnimationWindow.running):
        AnimationWindow.running = anim_w.main_loop(Circle)
        # print("main: ",result)
        result[0] = AnimationWindow.frame
        result[1] = len(InfectionCircle.infected_circles) / AnimationWindow.population * 100