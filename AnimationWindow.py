import random as rn
import math
import pygame as pyg
from pygame.locals import *
import numpy as np
import time as t
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (41, 128, 185)
RED = (255, 0, 0)
GREY = (30, 30, 30)
LIGHT_GREEN = (144, 238, 144)
GREEN = (0, 100, 0)


RADIUS = 5
VELOCITY = 1

NUMBER_OF_POPULATIONS = 1
NUMBER_OF_INFECTED = 1
MAX_INFECTION_DURATION = 300  # in frames
MIN_INFECTION_DURATION = 100  # in frames

BOUNDARY_WIDTH_NO_TRAVEL = 700
BOUNDARY_HEIGHT_NO_TRAVEL = 700
BOUNDARY_WIDTH_TRAVEL = 300
BOUNDARY_HEIGHT_TRAVEL = 300


FRAMES_PER_DAY = 20
OFFSET = 70


class Constants:
    POPULATION = 50
    INFECTION_RADIUS = 8
    SOCIAL_DISTANCE_RADIUS = 10
    INFECTION_PROBABILITY = 0.7
    SOCIAL_DISTANCING_EFFECIENCY = 1
    PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING = 1


populations = []
all_population = []
# susceptible_population = []
# infected_population = 0
# infection_radius_animation = [None] * Constants.POPULATION
# recovered_population = 0
# vaccinated1_population = []
# vaccinated2_population = []
# possible_collisions = []


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class AnimationWindow:
    frame = 0
    running = True

    FPS = 60
    window_width = 800
    window_height = 1000

    grid_size = 2 * Constants.SOCIAL_DISTANCE_RADIUS + 15

    cols = int(window_width / grid_size)
    rows = int(window_height / grid_size)

    grid = []

    def __init__(this, travel):
        this.travel = travel
        this.infected_population_counter = 0
        this.recovered_population_counter = 0
        global FPSCLOCK, DISPLAYSURF
        pyg.display.set_caption("Test")
        pos_x = 1920 - AnimationWindow.window_width
        pos_y = 32
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%i,%i" % (pos_x, pos_y)
        pyg.init()
        FPSCLOCK = pyg.time.Clock()
        DISPLAYSURF = pyg.display.set_mode(
            (AnimationWindow.window_width, AnimationWindow.window_height)
        )

        if travel:
            x_padding = (AnimationWindow.window_width - BOUNDARY_WIDTH_TRAVEL * 2) / 3
            y_padding = (AnimationWindow.window_height - BOUNDARY_HEIGHT_TRAVEL * 3) / 4

            for i in range(3):
                for j in range(2):
                    boundary = (
                        x_padding * (j + 1) + BOUNDARY_WIDTH_TRAVEL * j,
                        y_padding * (i + 1) + BOUNDARY_HEIGHT_TRAVEL * i,
                        BOUNDARY_HEIGHT_TRAVEL,
                        BOUNDARY_WIDTH_TRAVEL,
                    )
                    population = Population(
                        Constants.POPULATION,
                        NUMBER_OF_INFECTED if i == 2 and j == 1 else 0,
                        Constants.PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING,
                        boundary,
                    )
                    populations.append(population)
        else:
            x_padding = (AnimationWindow.window_width - BOUNDARY_WIDTH_NO_TRAVEL) / 2
            y_padding = (AnimationWindow.window_height - BOUNDARY_HEIGHT_NO_TRAVEL) / 2
            boundary = (
                x_padding,
                y_padding,
                BOUNDARY_WIDTH_NO_TRAVEL,
                BOUNDARY_HEIGHT_NO_TRAVEL,
            )
            population = Population(
                Constants.POPULATION,
                NUMBER_OF_INFECTED,
                Constants.PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING,
                boundary,
            )
            populations.append(population)

        AnimationWindow.grid = [
            [[] for j in range(AnimationWindow.rows)]
            for i in range(AnimationWindow.cols)
        ]

    def main_loop(this):
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                return False

        DISPLAYSURF.fill(WHITE)

        # drawGrid()
        this.infected_population_counter = 0
        this.recovered_population_counter = 0
        for population in populations:
            # print(len(populations))
            pyg.draw.rect(DISPLAYSURF, BLACK, population.boundary, 2)
            population.draw(DISPLAYSURF)
            InfectionRadiusAnimation.draw(population, DISPLAYSURF)
            population.move()
            population.recovery()
            population.collision()
            population.collision_boundary()
            this.infected_population_counter += len(population.infected_population)
            this.recovered_population_counter += len(population.recovered_population)
            # print(len(susceptible_population),len(infected_population),len(recovered_population))
            if AnimationWindow.frame % FRAMES_PER_DAY == 0:
                population.Update_Infection_Probability(AnimationWindow.frame)
            # if AnimationWindow.frame == 0:
            #     population.Vaccinate(0.5)

        pyg.display.update()
        FPSCLOCK.tick(AnimationWindow.FPS)

        AnimationWindow.frame += 1

        return True


class Population:
    number_of_populations = 0

    def __init__(
        this,
        number_of_population,
        number_of_infected,
        percentage_of_population_social_distancing,
        boundary,
    ):
        this.id = Population.number_of_populations
        Population.number_of_populations += 1
        this.number_of_population = number_of_population
        this.number_of_infected = number_of_infected
        this.boundary = boundary

        this.all_population = []
        this.susceptible_population = []
        this.infected_population = []
        this.infection_radius_animation = [None] * Constants.POPULATION
        this.recovered_population = []
        this.vaccinated1_population = []
        this.vaccinated2_population = []
        this.possible_collisions = []

        for i in range(number_of_population - number_of_infected):
            social_distancing = True
            rn.seed(t.time())
            if i > percentage_of_population_social_distancing * number_of_population:
                social_distancing = False
            person = Person(
                i,
                rn.uniform(
                    this.boundary[0] + OFFSET,
                    this.boundary[0] + this.boundary[2] - OFFSET,
                ),
                rn.uniform(
                    this.boundary[1] + OFFSET,
                    this.boundary[1] + this.boundary[3] - OFFSET,
                ),
                rn.random() * 360,
                social_distancing,
                this,
            )
            this.all_population.append(person)
            this.susceptible_population.append(person.id)

        for i in range(number_of_infected):
            infected = Person(
                number_of_population - number_of_infected + i,
                rn.uniform(
                    this.boundary[0] + OFFSET,
                    this.boundary[0] + this.boundary[2] - OFFSET,
                ),
                rn.uniform(
                    this.boundary[1] + OFFSET,
                    this.boundary[1] + this.boundary[3] - OFFSET,
                ),
                rn.random() * 360,
                False,
                this,
            )
            this.susceptible_population.append(infected.id)
            infected.Infect(0)
            this.all_population.append(infected)
            InfectionRadiusAnimation(infected.id, this)

        # this.all_population[0].Vaccinate(0)
        # this.all_population[0].Vaccinate(0)
        # this.all_population[1].Vaccinate(0)
        all_population.extend(this.all_population)

    def move(this):
        for i in range(AnimationWindow.cols):
            for j in range(AnimationWindow.rows):
                AnimationWindow.grid[i][j] = []
        for c in this.all_population:
            c.move()
        this.get_possible_collisions()

    def recovery(this):
        for infected in this.infected_population:
            this.all_population[infected].recovery()

    def Vaccinate(this, percentage_vaccination):
        number_of_vaccination = int(this.number_of_population * percentage_vaccination)
        for i in range(number_of_vaccination):
            index = rn.randint(0, this.number_of_population - 1)
            this.all_population[index].Vaccinate(AnimationWindow.frame)

    def draw(this, surface):
        for person in this.all_population:
            person.draw(surface)

    def collision_boundary(this):
        for person in this.all_population:
            person.collision_boundary(this.boundary)

    def collision(this):
        for cell_ind in this.possible_collisions:
            pos_col_arr = AnimationWindow.grid[cell_ind[0]][cell_ind[1]]
            j = 0
            for c1 in pos_col_arr:
                for c2 in pos_col_arr[j + 1 :]:
                    already_collided_in_this_frame = (
                        c2.id in c1.circles_indexes_in_collision
                    ) or (c1.id in c2.circles_indexes_in_collision)

                    sdist_overlap = (c2.id in c1.circles_indexes_sdist_overlap) or (
                        c1.id in c2.circles_indexes_sdist_overlap
                    )

                    sdist_collision = ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (
                        2 * (Constants.SOCIAL_DISTANCE_RADIUS)
                    ) ** 2

                    if Constants.SOCIAL_DISTANCE_RADIUS < Constants.INFECTION_RADIUS:
                        infect_overlap = (
                            c2.id in c1.circles_indexes_infect_overlap
                        ) or (c1.id in c2.circles_indexes_infect_overlap)

                        if ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (
                            2 * (Constants.INFECTION_RADIUS)
                        ) ** 2 and not infect_overlap:  # checking collision according to infection radius

                            c1.circles_indexes_infect_overlap.append(c2.id)
                            c2.circles_indexes_infect_overlap.append(c1.id)

                            proba = rn.random()
                            if c1.infected:
                                if not c2.infected and c2.infection_probability > proba:
                                    c2.Infect(AnimationWindow.frame)
                            elif c2.infected:
                                if not c1.infected and c1.infection_probability > proba:
                                    c1.Infect(AnimationWindow.frame)

                        if ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) > (
                            2 * (Person.radius)
                        ) ** 2:
                            if infect_overlap:
                                c1.circles_indexes_infect_overlap.remove(c2.id)
                                c2.circles_indexes_infect_overlap.remove(c1.id)
                    if (
                        sdist_collision and not already_collided_in_this_frame
                    ):  # checking collision according to social distance radius

                        if not sdist_overlap:
                            proba = rn.random()
                            if (
                                c2.social_distancing_efficiency > proba
                                or c1.social_distancing_efficiency > proba
                            ):
                                Population.bounce(
                                    c1, c2, Constants.SOCIAL_DISTANCE_RADIUS
                                )
                            else:
                                c1.circles_indexes_sdist_overlap.append(c2.id)
                                c2.circles_indexes_sdist_overlap.append(c1.id)
                        else:
                            infect_overlap = (
                                c2.id in c1.circles_indexes_infect_overlap
                            ) or (c1.id in c2.circles_indexes_infect_overlap)

                            if ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) < (
                                2 * (Constants.INFECTION_RADIUS)
                            ) ** 2 and not infect_overlap:  # checking collision according to infection radius

                                c1.circles_indexes_infect_overlap.append(c2.id)
                                c2.circles_indexes_infect_overlap.append(c1.id)

                                proba = rn.random()
                                if c1.infected:
                                    if (
                                        not c2.infected
                                        and c2.infection_probability > proba
                                    ):
                                        c2.Infect(AnimationWindow.frame)
                                elif c2.infected:
                                    if (
                                        not c1.infected
                                        and c1.infection_probability > proba
                                    ):
                                        c1.Infect(AnimationWindow.frame)

                            if ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) > (
                                2 * (Person.radius)
                            ) ** 2:
                                if infect_overlap:
                                    c1.circles_indexes_infect_overlap.remove(c2.id)
                                    c2.circles_indexes_infect_overlap.remove(c1.id)
                    else:
                        if not sdist_collision and sdist_overlap:
                            c1.circles_indexes_sdist_overlap.remove(c2.id)
                            c2.circles_indexes_sdist_overlap.remove(c1.id)

                j += 1

    def bounce(c1, c2, bounce_radius):

        c1.circles_indexes_in_collision.append(c2.id)
        c2.circles_indexes_in_collision.append(c1.id)

        n = [c2.x - c1.x, c2.y - c1.y]  # normal vector
        n_mag = math.sqrt(n[0] ** 2 + n[1] ** 2)
        if n_mag == 0:
            return
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

        over_collision = ((2 * bounce_radius) - n_mag) / 2
        budge_x = n[0] * (over_collision / n_mag)
        budge_y = n[1] * (over_collision / n_mag)

        c1.budge_x = -budge_x
        c1.budge_y = -budge_y

        c2.budge_x = budge_x
        c2.budge_y = budge_y

    def locate_circle_in_grid(c, grid):

        center_loc_in_grid = (
            int(c.x / AnimationWindow.grid_size),
            int(c.y / AnimationWindow.grid_size),
        )
        # print(center_loc_in_grid[0],center_loc_in_grid[1],len(grid))
        grid[center_loc_in_grid[0]][center_loc_in_grid[1]].append(c)
        c.grid_cells.append(center_loc_in_grid)

        if (
            distance(
                c.x,
                c.y,
                ((center_loc_in_grid[0]) * AnimationWindow.grid_size),
                ((center_loc_in_grid[1]) * AnimationWindow.grid_size),
            )
            < Constants.SOCIAL_DISTANCE_RADIUS
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
                ((center_loc_in_grid[0]) * AnimationWindow.grid_size),
                ((center_loc_in_grid[1] + 1) * AnimationWindow.grid_size),
            )
            < Constants.SOCIAL_DISTANCE_RADIUS
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
                ((center_loc_in_grid[0] + 1) * AnimationWindow.grid_size),
                ((center_loc_in_grid[1] + 1) * AnimationWindow.grid_size),
            )
            < Constants.SOCIAL_DISTANCE_RADIUS
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
                ((center_loc_in_grid[0] + 1) * AnimationWindow.grid_size),
                ((center_loc_in_grid[1]) * AnimationWindow.grid_size),
            )
            < Constants.SOCIAL_DISTANCE_RADIUS
        ):
            grid[center_loc_in_grid[0]][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1] - 1].append(c)
            grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]].append(c)

            c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1] - 1))
            c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1]))

        else:
            if (
                c.x - Constants.SOCIAL_DISTANCE_RADIUS
                < center_loc_in_grid[0] * AnimationWindow.grid_size
            ):
                grid[center_loc_in_grid[0] - 1][center_loc_in_grid[1]].append(c)
                c.grid_cells.append((center_loc_in_grid[0] - 1, center_loc_in_grid[1]))

            if (
                c.y - Constants.SOCIAL_DISTANCE_RADIUS
                < center_loc_in_grid[1] * AnimationWindow.grid_size
            ):
                grid[center_loc_in_grid[0]][center_loc_in_grid[1] - 1].append(c)
                c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] - 1))

            if (
                c.y + Constants.SOCIAL_DISTANCE_RADIUS
                > (center_loc_in_grid[1] + 1) * AnimationWindow.grid_size
            ):
                grid[center_loc_in_grid[0]][center_loc_in_grid[1] + 1].append(c)
                c.grid_cells.append((center_loc_in_grid[0], center_loc_in_grid[1] + 1))

            if (
                c.x + Constants.SOCIAL_DISTANCE_RADIUS
                > (center_loc_in_grid[0] + 1) * AnimationWindow.grid_size
            ):
                # print(len(grid),center_loc_in_grid[0] + 1,center_loc_in_grid[1])
                grid[center_loc_in_grid[0] + 1][center_loc_in_grid[1]].append(c)
                c.grid_cells.append((center_loc_in_grid[0] + 1, center_loc_in_grid[1]))

    def get_possible_collisions(this):
        this.possible_collisions.clear()
        i = 0
        for i in range(AnimationWindow.cols):
            j = 0
            for j in range(AnimationWindow.rows):
                leng = len(AnimationWindow.grid[i][j])
                if leng > 1:
                    this.possible_collisions.append((i, j))

    def Update_Infection_Probability(this, current_frame):
        for c in this.all_population:
            c.Update_Infection_Probability(current_frame)

    def Update_Social_Distancing():
        for population in populations:
            population.percentage_of_population_social_distancing = (
                Constants.PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING
            )
            for i in range(Constants.POPULATION):
                if (
                    i
                    < Constants.PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING
                    * population.number_of_population
                ):
                    population.all_population[i].social_distancing = True
                else:
                    population.all_population[i].social_distancing = False


class Person:
    radius = RADIUS
    velocity_magnitude = VELOCITY
    offset = OFFSET
    reflection_strength = VELOCITY / 4

    def __init__(this, id, x, y, direction, social_distancing, population):
        this.id = id
        this.x = x
        this.y = y
        this.direction = direction
        this.population = population
        this.v = [
            math.cos(math.radians(direction)) * Person.velocity_magnitude,
            math.sin(math.radians(direction)) * Person.velocity_magnitude,
        ]
        this.color = BLUE

        this.grid_cells = []
        this.circles_indexes_in_collision = []
        this.circles_indexes_sdist_overlap = []
        this.circles_indexes_infect_overlap = []

        this.budge_x = 0
        this.budge_y = 0

        this.social_distancing = social_distancing
        this.calculate_social_distancing_efficiency()

        this.infected = False
        this.infection_probability = rn.uniform(0, 1) * Constants.INFECTION_PROBABILITY
        this.infection_start_frame = 0
        this.infection_end_frame = 0

        this.recovery_frame = 0

        this.number_of_vaccination = 0
        this.vaccination = {"1": 0, "2": 0}

    def move(this):
        this.grid_cells.clear()
        this.circles_indexes_in_collision.clear()

        wander_step = rn.normalvariate(0, 0.8) * Person.velocity_magnitude * 0.3
        if rn.random() > 0.5:
            this.v[0] += wander_step
        else:
            this.v[1] += wander_step
        v_norm = math.sqrt(this.v[0] ** 2 + this.v[1] ** 2)
        this.v[0] *= this.velocity_magnitude / v_norm
        this.v[1] *= this.velocity_magnitude / v_norm
        this.x += this.v[0] + this.budge_x
        this.y += this.v[1] + this.budge_y

        this.budge_x = 0
        this.budge_y = 0

        Population.locate_circle_in_grid(this, AnimationWindow.grid)

    def recovery(this):
        if AnimationWindow.frame > int(this.infection_end_frame):
            this.Recover()

    def draw(this, surface):
        pyg.draw.circle(surface, this.color, (this.x, this.y), this.radius, 0)

    def collision_boundary(this, boundary):
        if this.x - this.radius < boundary[0] + Person.offset:
            this.v[0] += Person.reflection_strength
        if this.x + this.radius > boundary[2] + boundary[0] - Person.offset:
            this.v[0] -= Person.reflection_strength
        if this.y - this.radius < boundary[1] + Person.offset:
            this.v[1] += Person.reflection_strength
        if this.y + this.radius > boundary[3] + boundary[1] - Person.offset:
            this.v[1] -= Person.reflection_strength

    def Infect(this, current_frame):
        this.infected = True
        this.Remove_From_Corresponding_Array()
        this.population.infected_population.append(this.id)
        # print(infected_population,len(infected_population))
        this.color = RED
        this.infection_start_frame = current_frame
        this.infection_end_frame = current_frame + rn.uniform(
            MIN_INFECTION_DURATION, MAX_INFECTION_DURATION
        )
        InfectionRadiusAnimation(this.id, this.population)

    def Recover(this):
        this.infected = False
        # infected_population.remove(this.id)
        this.Remove_From_Corresponding_Array()
        InfectionRadiusAnimation.Remove(this.id, this.population)
        this.recovery_time = this.infection_end_frame
        this.infection_start_frame = 0
        this.infection_end_frame = 0
        if this.number_of_vaccination == 0:
            this.color = GREY
            this.population.recovered_population.append(this.id)
        elif this.number_of_vaccination == 1:
            this.color = LIGHT_GREEN
            this.population.vaccinated1_population.append(this.id)
        elif this.number_of_vaccination == 2:
            this.color = GREEN
            this.population.vaccinated2_population.append(this.id)

    def Vaccinate(this, current_frame):
        if this.infected or this.number_of_vaccination > 1:
            return
        elif this.number_of_vaccination == 0:
            this.Remove_From_Corresponding_Array()
            this.population.vaccinated1_population.append(this.id)
            this.color = LIGHT_GREEN
            this.vaccination.update({"1": current_frame})
        elif this.number_of_vaccination == 1:
            this.Remove_From_Corresponding_Array()
            this.population.vaccinated2_population.append(this.id)
            this.color = GREEN
            this.vaccination.update({"2": current_frame})
        this.number_of_vaccination += 1
        return

    def Calculate_Infection_Probability(this, current_frame):
        if this.infected:
            return this.infection_probability

        if this.number_of_vaccination == 2:
            duration = this.vaccination["2"] - current_frame
            if duration <= 5 * FRAMES_PER_DAY:
                infection_probability = (
                    rn.uniform(0, 0.15) * Constants.INFECTION_PROBABILITY
                )
            elif duration <= 10 * FRAMES_PER_DAY:
                infection_probability = (
                    rn.uniform(0, 0.25) * Constants.INFECTION_PROBABILITY
                )
            else:
                infection_probability = (
                    rn.uniform(0, 0.3) * Constants.INFECTION_PROBABILITY
                )

        elif this.number_of_vaccination == 1:
            duration = this.vaccination["1"] - current_frame
            if duration <= 5 * FRAMES_PER_DAY:
                infection_probability = (
                    rn.uniform(0, 0.2) * Constants.INFECTION_PROBABILITY
                )
            elif duration <= 10 * FRAMES_PER_DAY:
                infection_probability = (
                    rn.uniform(0, 0.3) * Constants.INFECTION_PROBABILITY
                )
            else:
                infection_probability = (
                    rn.uniform(0, 0.5) * Constants.INFECTION_PROBABILITY
                )

        elif this.number_of_vaccination == 0:
            if this.recovery_frame == 0:
                infection_probability = (
                    rn.uniform(0, 1) * Constants.INFECTION_PROBABILITY
                )
            else:
                duration = this.recovery_frame - current_frame
                if duration <= 5 * FRAMES_PER_DAY:
                    infection_probability = (
                        rn.uniform(0, 0.3) * Constants.INFECTION_PROBABILITY
                    )
                elif duration <= 10 * FRAMES_PER_DAY:
                    infection_probability = (
                        rn.uniform(0, 0.5) * Constants.INFECTION_PROBABILITY
                    )
                else:
                    infection_probability = (
                        rn.uniform(0, 1) * Constants.INFECTION_PROBABILITY
                    )

        return infection_probability

    def calculate_social_distancing_efficiency(this):
        if Constants.SOCIAL_DISTANCING_EFFECIENCY == 1:
            this.social_distancing_efficiency = 1 if this.social_distancing else 0
        else:
            this.social_distancing_efficiency = (
                rn.uniform(0.9, 1) * Constants.SOCIAL_DISTANCING_EFFECIENCY
                if this.social_distancing
                else 0
            )

    def Update_Infection_Probability(this, current_frame):
        this.infection_probability = this.Calculate_Infection_Probability(current_frame)

    def Remove_From_Corresponding_Array(this):
        color = this.color
        if color == BLUE:
            this.population.susceptible_population.remove(this.id)
        elif color == RED:
            this.population.infected_population.remove(this.id)
        elif color == GREY:
            this.population.recovered_population.remove(this.id)
        elif color == LIGHT_GREEN:
            this.population.vaccinated1_population.remove(this.id)
        elif color == GREEN:
            this.population.vaccinated2_population.remove(this.id)
        return


class InfectionRadiusAnimation:
    end_frame = 60
    infection_circle_radius = 2 * Constants.INFECTION_RADIUS
    radius_step = (infection_circle_radius - Person.radius) / AnimationWindow.FPS
    color_step = int((255 - 0) / AnimationWindow.FPS)

    def __init__(this, id, population):
        this.id = id
        this.radius = Person.radius
        this.alpha = 255
        this.population = population
        this.surface = pyg.Surface(
            (
                InfectionRadiusAnimation.infection_circle_radius * 2,
                InfectionRadiusAnimation.infection_circle_radius * 2,
            ),
            pyg.SRCALPHA,
        )
        this.frame = 0
        population.infection_radius_animation[id] = this

    def draw(population, main_surface):
        for infected in population.infection_radius_animation:
            if infected:
                c = population.all_population[infected.id]
                infected.alpha -= InfectionRadiusAnimation.color_step
                pyg.draw.circle(
                    infected.surface,
                    (*RED, infected.alpha),
                    (
                        InfectionRadiusAnimation.infection_circle_radius,
                        InfectionRadiusAnimation.infection_circle_radius,
                    ),
                    infected.radius
                    + (InfectionRadiusAnimation.radius_step * infected.frame),
                    5,
                )
                main_surface.blit(
                    infected.surface,
                    (
                        c.x - InfectionRadiusAnimation.infection_circle_radius,
                        c.y - InfectionRadiusAnimation.infection_circle_radius,
                    ),
                )
                infected.frame += 1
                if infected.frame > InfectionRadiusAnimation.end_frame:
                    infected.frame = 0
                    infected.alpha = 255

    def updateRadius():
        InfectionRadiusAnimation.infection_circle_radius = (
            2 * Constants.INFECTION_RADIUS
        )
        InfectionRadiusAnimation.radius_step = (
            InfectionRadiusAnimation.infection_circle_radius - Person.radius
        ) / AnimationWindow.FPS
        for population in populations:
            if len(population.infected_population) > 0:
                for infected in population.infected_population:
                    if population.infection_radius_animation[infected]:
                        population.infection_radius_animation[
                            infected
                        ].surface = pyg.Surface(
                            (
                                InfectionRadiusAnimation.infection_circle_radius * 2,
                                InfectionRadiusAnimation.infection_circle_radius * 2,
                            ),
                            pyg.SRCALPHA,
                        )

    def Remove(id, population):
        population.infection_radius_animation[id] = None


def drawGrid():
    for i in range(AnimationWindow.cols):
        pyg.draw.line(
            DISPLAYSURF,
            GREY,
            (i * AnimationWindow.grid_size, 0),
            (i * AnimationWindow.grid_size, 800),
        )
    for i in range(AnimationWindow.rows):
        pyg.draw.line(
            DISPLAYSURF,
            GREY,
            (0, i * AnimationWindow.grid_size),
            (800, i * AnimationWindow.grid_size),
        )


def updateSliderControls(slider_values):
    Constants.INFECTION_PROBABILITY = slider_values[0]

    if Constants.SOCIAL_DISTANCING_EFFECIENCY != slider_values[1]:
        Constants.SOCIAL_DISTANCING_EFFECIENCY = slider_values[1]
        for person in all_population:
            person.calculate_social_distancing_efficiency()

    Constants.SOCIAL_DISTANCE_RADIUS = slider_values[2]

    Constants.INFECTION_RADIUS = slider_values[3]
    InfectionRadiusAnimation.updateRadius()

    if Constants.PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING != slider_values[4]:
        Constants.PERCENTAGE_OF_POPULATION_SOCIAL_DISTANCING = slider_values[4]
        Population.Update_Social_Distancing()
        for person in all_population:
            person.calculate_social_distancing_efficiency()


def Travel():
    population_index_source = rn.randint(0, 5)
    population_index_destination = population_index_source
    while population_index_destination == population_index_source:
        population_index_destination = rn.randint(0, 5)
    traveling_person_index = rn.randint(0, Constants.POPULATION)
    traveling_person = populations[population_index_source].all_population.pop(
        traveling_person_index
    )
    old_id = traveling_person.id
    new_id = populations[population_index_destination].number_of_population
    traveling_person.id = new_id
    traveling_person.population = populations[population_index_destination]
    populations[population_index_destination].number_of_population += 1
    populations[population_index_destination].all_population.append(traveling_person)

    if old_id in populations[population_index_source].susceptible_population:
        populations[population_index_source].susceptible_population.remove(old_id)
        populations[population_index_destination].susceptible_population.append(new_id)
    elif old_id in populations[population_index_source].infected_population:
        populations[population_index_source].infected_population.remove(old_id)
        populations[population_index_destination].infected_population.append(new_id)
    elif old_id in populations[population_index_source].infection_radius_animation:
        populations[population_index_source].infection_radius_animation[old_id] = None
        InfectionRadiusAnimation(new_id, populations[population_index_source])
    elif old_id in populations[population_index_source].recovered_population:
        populations[population_index_source].recovered_population.remove(old_id)
        populations[population_index_destination].recovered_population.append(new_id)
    elif old_id in populations[population_index_source].vaccinated1_population:
        populations[population_index_source].vaccinated1_population.remove(old_id)
        populations[population_index_destination].vaccinated1_population.append(new_id)
    elif old_id in populations[population_index_source].vaccinated2_population:
        populations[population_index_source].vaccinated2_population.remove(old_id)
        populations[population_index_destination].vaccinated2_population.append(new_id)
    populations[population_index_source].number_of_population -= 1

    print(
        f"Travel: source: {population_index_source} dest: {population_index_destination}"
    )


def main(result, slider_values, vaccination_control, travel):
    anim_w = AnimationWindow(travel)
    updateSliderControls(slider_values)
    Travel()
    while AnimationWindow.running:
        AnimationWindow.running = anim_w.main_loop()
        result[0] = AnimationWindow.frame
        result[1] = (
            anim_w.infected_population_counter
            / (Constants.POPULATION * Population.number_of_populations)
        ) * 100
        # print(len(infected_population))
        result[2] = (
            (
                Constants.POPULATION * Population.number_of_populations
                - anim_w.recovered_population_counter
            )
            / (Constants.POPULATION * Population.number_of_populations)
        ) * 100

        updateSliderControls(slider_values)
        if vaccination_control[0] == 1:
            vaccination_control[0] = 0
            vaccination_percentage = vaccination_control[1] / 100
            for population in populations:
                population.Vaccinate(vaccination_percentage)

        if result[3] == 1:
            break


def testing_main():
    anim_w = AnimationWindow(True)
    Travel()
    while AnimationWindow.running:
        AnimationWindow.running = anim_w.main_loop()


testing_main()
