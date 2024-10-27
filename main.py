from pydoc import plain

import pygame, math
from pygame import *
from math import *

WIN_WIDTH = 800
WIN_HEIGHT = 640
PLANET_WIDTH = 20
PLANET_HEIGHT = 20
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
SPACE_COLOR = "#000022"
DEFAULT_COLOR = "blue"

class StarSystem:
    def __init__(self, planets=None):
        if planets is None:
            planets = []
        self.planets = planets

    def add(self, planet):
        self.planets.append(planet)

    def remove(self, planet):
        self.planets.remove(planet)

    def update(self):
        new_star_system = StarSystem()
        for planet in self.planets:
            new_star_system.add(planet.copy())

        for i in range(len(self.planets)):
            for j in range(len(self.planets)):
                if i == j: continue
                else: new_star_system.planets[i] = new_star_system.planets[i].interact(self.planets[j])
        self.planets = new_star_system.planets
        return new_star_system



class PlanetaryObject:
    def __init__(self, mass:float, x=0.0, y=0.0, vx=0.0, vy=0.0, ax=0.0, ay=0.0, curr_color=DEFAULT_COLOR):
        self.x = x
        self.y = y
        self.mass = mass
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
        self.color = curr_color
        width, height = sqrt(mass/2), sqrt(mass/2)
        self.image = Surface((width, height))
        self.image.fill(Color(SPACE_COLOR))
        draw.circle(self.image, Color(self.color),
                (width // 2, height // 2),
                sqrt(mass/2)/2)

    def copy(self):
        return PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)

    def state(self):
        return {"mass": self.mass,
                "x": self.x,
                "y": self.y,
                "vx": self.vx,
                "vy": self.vy,
                "ax": self.ax,
                "ay": self.ay,
                "color": self.color}

    def interact(self, planet):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)
        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        # New speed based on accel
        new_state.vx += new_state.ax
        new_state.vy += new_state.ay

        # New pos based on speed
        new_state.x += new_state.vx
        new_state.y += new_state.vy
        return new_state

# Stop conditions
CRASH_DIST = 10
OUT_DIST = 1000


def main():
    # PyGame init
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Solar Mechanics v0.1")

    # Space init
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))
    bg.fill(Color(SPACE_COLOR))

    # Timer init
    timer = pygame.time.Clock()

    # Planet init
    planet = PlanetaryObject(x = 100, y = 290, vx = 0.1, vy = 1.5, ax = 0, ay = 0, mass = 100, curr_color = "blue")
    planet1 = PlanetaryObject(x=WIN_WIDTH-100, y=WIN_HEIGHT-290, vx=-0.1, vy=1.5, ax=0, ay=0, mass=200, curr_color="green")
    # Sun
    sun = PlanetaryObject(x = WIN_WIDTH // 2, y = WIN_HEIGHT // 2, vx = 0, vy = 0, ax = 0, ay = 0, mass = 5000, curr_color = "yellow")

    star_system = StarSystem()
    star_system.add(planet)
    star_system.add(planet1)
    star_system.add(sun)

    done = False
    while not done:
        timer.tick(50)
        for e in pygame.event.get():
            if e.type == QUIT:
                done = True
                break

        star_system.update()
        screen.blit(bg, (0, 0))
        for i in range(len(star_system.planets)):
            screen.blit(star_system.planets[i].image, (int(star_system.planets[i].x), int(star_system.planets[i].y)))
        pygame.display.update()

        # if r < CRASH_DIST:
        #     done = True
        #     print("Crashed")
        #     break
        # if r > OUT_DIST:
        #     done = True
        #     print("Out of system")
        #     break

    # Farewell
    print(":-)")


if __name__ == "__main__":
    main()