import random as rn
import math
import pygame as pyg
from pygame.locals import *
import numpy as np

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 800

BLUE = (41, 128, 185)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (30, 30, 30)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

infection_radius = 4
social_distance_radius = 8

boundary = (50, 50, 700, 700)

grid_size= 3 * social_distance_radius

cols = int(WINDOWWIDTH / grid_size)
rows = int(WINDOWHEIGHT / grid_size)
grid = [[[] for j in range(rows)] for i in range(cols)]

possible_collisions = []
possible_collisions_set = set()


class Circle:
    radius = 5
    v_magnitude = 2

    def __init__(this, x, y, direction, infected=False, thickness=0):
        this.x = x
        this.y = y
        this.infected = infected
        this.thickness = thickness
        this.direction = direction
        this.v = [math.cos(math.radians(direction)) * this.v_magnitude, math.sin(math.radians(direction)) * this.v_magnitude]
        this.grid_cells = []
        this.budge_x = 0
        this.budge_y = 0
        this.circles_indexes_in_collision = []

    def move(circles):
        for i in range(cols):
            for j in range(rows):
                grid[i][j] = []

        for c in circles:
            c.grid_cells.clear()
            c.circles_indexes_in_collision.clear()
            rn.seed(c.x)
            wander_step = rn.normalvariate(0, 0.2) * Circle.v_magnitude * 0.55
            if rn.random() > 0.5:
                c.v[0] += wander_step
            else:
                c.v[1] += wander_step
            v_norm = math.sqrt(c.v[0]**2 + c.v[1]**2)
            c.v[0] *= c.v_magnitude / v_norm
            c.v[1] *= c.v_magnitude / v_norm
            c.x += c.v[0] + c.budge_x
            c.y += c.v[1] + c.budge_y

            c.budge_x = 0
            c.budge_y = 0

            c.locate_circle_in_grid(grid)
        Circle.get_possible_collisions()

    def draw(circles, surface):
        for c in circles:
            pyg.draw.circle(surface, RED if c.infected else BLUE, (c.x, c.y), c.radius, c.thickness)

    def collision_boundary(circles, boundary):
        offset=70
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
                
    def collision(circles, nbcircles):
        i=0
        while(i < nbcircles):
            j=i+1
            while(j < nbcircles):
                c1 = circles[i]
                c2 = circles[j]
                
                if(((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (2 * (infection_radius)) ** 2):
                    if c1.infected:
                        c2.infected = True
                    elif c2.infected:
                        c1.infected = True

                if(((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (2 * (social_distance_radius)) ** 2) and i not in c2.circles_indexes_in_collision and j not in c1.circles_indexes_in_collision:
                    n = [c2.x - c1.x, c2.y - c1.y] #normal vector
                    n_mag = math.sqrt(n[0]**2 + n[1]**2)
                    if(n_mag == 0):
                        break
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

                    over_collision = ((2 * social_distance_radius) - n_mag)/2
                    budge_x = n[0]  * (over_collision/n_mag)
                    budge_y = n[1]  * (over_collision/n_mag)

                    c1.budge_x = -budge_x
                    c1.budge_y = -budge_y

                    c2.budge_x = budge_x
                    c2.budge_y = budge_y

                    c1.circles_indexes_in_collision.append(j)
                    c2.circles_indexes_in_collision.append(i)
                j += 1
            i += 1

    def collision2():
        for cell_ind in possible_collisions:
            pos_col_arr = grid[cell_ind[0]][cell_ind[1]]
            n = len(pos_col_arr)
            j=0
            for c1 in pos_col_arr:
                for c2 in pos_col_arr[j+1:]:

                    if(((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (2 * (infection_radius)) ** 2):
                        if c1.infected:
                            c2.infected = True
                        elif c2.infected:
                            c1.infected = True
                    if(((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (2 * (social_distance_radius)) ** 2):
                        n = [c2.x - c1.x, c2.y - c1.y] #normal vector
                        n_mag = math.sqrt(n[0]**2 + n[1]**2)
                        if(n_mag == 0):
                            break
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

                        over_collision = ((2 * social_distance_radius) - n_mag)/2
                        budge_x = n[0]  * (over_collision/n_mag)
                        budge_y = n[1]  * (over_collision/n_mag)

                        c1.budge_x = -budge_x
                        c1.budge_y = -budge_y

                        c2.budge_x = budge_x
                        c2.budge_y = budge_y
                j += 1

    def locate_circle_in_grid(c, grid):

        center_loc_in_grid = (int(c.x / grid_size),int(c.y / grid_size))
        grid[center_loc_in_grid[0]][center_loc_in_grid[1]].append(c)
        c.grid_cells.append(center_loc_in_grid)

        if(distance(c.x, c.y, ((center_loc_in_grid[0]) * grid_size), ((center_loc_in_grid[1]) * grid_size)) < social_distance_radius):
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]    ].append(c)
            grid[center_loc_in_grid[0]    ][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1] - 1].append(c)

            c.grid_cells.append((center_loc_in_grid[0] - 1,center_loc_in_grid[1]    ))
            c.grid_cells.append((center_loc_in_grid[0]    ,center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] - 1,center_loc_in_grid[1] - 1))

        elif(distance(c.x, c.y, ((center_loc_in_grid[0]) * grid_size), ((center_loc_in_grid[1] + 1) * grid_size)) < social_distance_radius):
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]    ].append(c)
            grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1] + 1].append(c)
            grid[center_loc_in_grid[0]    ][center_loc_in_grid[1] + 1].append(c)

            c.grid_cells.append((center_loc_in_grid[0] - 1,center_loc_in_grid[1]    ))
            c.grid_cells.append((center_loc_in_grid[0] - 1,center_loc_in_grid[1] + 1))
            c.grid_cells.append((center_loc_in_grid[0]    ,center_loc_in_grid[1] + 1))
        
        elif(distance(c.x, c.y, ((center_loc_in_grid[0] + 1) * grid_size), ((center_loc_in_grid[1] + 1) * grid_size)) < social_distance_radius):
            grid[center_loc_in_grid[0]    ][center_loc_in_grid[1] + 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1] + 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]    ].append(c)

            c.grid_cells.append((center_loc_in_grid[0]    ,center_loc_in_grid[1] + 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1,center_loc_in_grid[1] + 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1,center_loc_in_grid[1]    ))
        
        elif(distance(c.x, c.y, ((center_loc_in_grid[0] + 1) * grid_size), ((center_loc_in_grid[1]) * grid_size)) < social_distance_radius):
            grid[center_loc_in_grid[0]    ][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]    ].append(c)

            c.grid_cells.append((center_loc_in_grid[0]    ,center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1,center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1,center_loc_in_grid[1]    ))
        
        else:
            if(c.x - social_distance_radius < center_loc_in_grid[0] * grid_size):
                grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]].append(c)
                c.grid_cells.append((center_loc_in_grid[0] - 1,center_loc_in_grid[1]))

            if(c.y - social_distance_radius < center_loc_in_grid[1] * grid_size):
                grid[center_loc_in_grid[0]][center_loc_in_grid[1] - 1].append(c)
                c.grid_cells.append((center_loc_in_grid[0],center_loc_in_grid[1] - 1))

            if(c.y + social_distance_radius > (center_loc_in_grid[1] + 1) * grid_size):
                grid[center_loc_in_grid[0]][center_loc_in_grid[1] + 1].append(c)
                c.grid_cells.append((center_loc_in_grid[0],center_loc_in_grid[1] + 1))
                
            if(c.x + social_distance_radius > (center_loc_in_grid[0] + 1) * grid_size):
                grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]].append(c)
                c.grid_cells.append((center_loc_in_grid[0] + 1,center_loc_in_grid[1]))

    
    def get_possible_collisions():
        possible_collisions.clear()
        i=0
        for i in range(rows):
            j=0
            for j in range(cols):
                leng = len(grid[i][j])
                if leng > 1:
                    possible_collisions.append((i,j))
        

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def main():
    global FPSCLOCK, DISPLAYSURF
    pyg.init()
    FPSCLOCK = pyg.time.Clock()
    DISPLAYSURF = pyg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pyg.display.set_caption("Test")

    mainLoop()

def drawGrid():
    for i in range(cols):
        pyg.draw.line(DISPLAYSURF, GREY, (i*grid_size, 0), (i*grid_size, 800))
    for i in range(rows):
        pyg.draw.line(DISPLAYSURF, GREY, (0, i*grid_size), (800, i*grid_size))

def mainLoop():
    time = 0
    frame = 0
    circles = []
    nb_circles = 150
    rn.seed(2343)
    for i in range(nb_circles):
        circle = Circle(
            rn.random() * (boundary[2] - 150) + 120,
            rn.random() * (boundary[3] - 150) + 120,
            rn.random()*360)
        circles.append(circle)

    nb_circles+=1
    circle = Circle(
        rn.random() * (boundary[2] - 150) + 120,
        rn.random() * (boundary[3] - 150) + 120,
        rn.random()*360,True)
    circles.append(circle)

    running = True
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False


        DISPLAYSURF.fill(BLACK)

        pyg.draw.rect(DISPLAYSURF, WHITE, boundary, 2)
        Circle.draw(circles, DISPLAYSURF)
        #drawGrid()

        Circle.move(circles)
        Circle.collision2()
        Circle.collision_boundary(circles, boundary)
        # Circle.collision(circles, nb_circles)

        pyg.display.update()
        FPSCLOCK.tick(FPS)
        frame += 1
        if frame % FPS == 0:
            time += 1
            #print(time)

    pyg.quit()


main()
