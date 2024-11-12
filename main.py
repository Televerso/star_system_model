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
FRAMERATE = 30
UPF = 200
timer = pygame.time.Clock()
TIME_STEP = 0.005

class TimeClock:
    def __init__(self, time_step):
        self.time_passed = 0
        self.n_steps = 0
        self.time_step = time_step

    def tick(self):
        self.time_passed += self.time_step
        self.n_steps += 1

    def get_time_passed(self):
        return self.time_passed

    def get_time_step(self):
        return self.time_step

    def get_n_steps(self):
        return self.n_steps

class StarSystem:
    def __init__(self, star_timer : TimeClock, planets=None):
        if planets is None:
            planets = []
        self.planets = planets
        self.timer = star_timer

    def add(self, planet):
        self.planets.append(planet)

    def remove(self, planet):
        self.planets.remove(planet)

    def update_euler(self):
        new_star_system = StarSystem(self.timer)
        for planet in self.planets:
            new_star_system.add(planet.copy())

        for i in range(len(self.planets)):
            for j in range(len(self.planets)):
                if i == j: continue
                else: new_star_system.planets[i] = new_star_system.planets[i].interact_euler(self.planets[j],
                                                                                             self.timer.get_time_step())
        self.planets = new_star_system.planets
        return new_star_system

    def update_eulerkramer(self):
        new_star_system = StarSystem(self.timer)
        for planet in self.planets:
            new_star_system.add(planet.copy())

        for i in range(len(self.planets)):
            for j in range(len(self.planets)):
                if i == j: continue
                else: new_star_system.planets[i] = new_star_system.planets[i].interact_eulerkramer(self.planets[j],
                                                                                                   self.timer.get_time_step())
        self.planets = new_star_system.planets
        return new_star_system

    def update_halfstep(self):
        new_star_system = StarSystem(self.timer)
        for planet in self.planets:
            new_star_system.add(planet.copy())

        for i in range(len(self.planets)):
            for j in range(len(self.planets)):
                if i == j: continue
                else: new_star_system.planets[i] = new_star_system.planets[i].interact_halfstep(self.planets[j],
                                                                                                self.timer.get_time_passed(),
                                                                                                self.timer.get_time_step())
        self.planets = new_star_system.planets
        return new_star_system

    def update_verle(self):
        new_star_system = StarSystem(self.timer)
        for planet in self.planets:
            new_star_system.add(planet.copy())

        if (self.timer.get_n_steps() < 2):
            for i in range(len(self.planets)):
                for j in range(len(self.planets)):
                    if i == j:
                        continue
                    else:
                        new_star_system.planets[i] = new_star_system.planets[i].interact_eulerkramer(self.planets[j],
                                                                                               self.timer.get_time_step()/2)
                new_star_system.planets[i].prev_state = self.planets[i]
        else:
            for i in range(len(self.planets)):
                for j in range(len(self.planets)):
                    if i == j:
                        continue
                    else:
                        new_star_system.planets[i] = new_star_system.planets[i].interact_verle(self.planets[j],
                                                                                               self.timer.get_time_step())
        self.planets = new_star_system.planets
        return new_star_system

class PlanetaryObject:
    def __init__(self, mass:float, x=0.0, y=0.0, vx=0.0, vy=0.0, ax=0.0, ay=0.0, curr_color=DEFAULT_COLOR):
        self.prev_state = None
        self.x = x
        self.y = y
        self.mass = mass
        self.vx = vx
        self.vy = vy
        self.vx12 = 0
        self.vy12 = 0
        self.ax = ax
        self.ay = ay
        self.color = curr_color
        self.width, self.height = sqrt(mass/2), sqrt(mass/2)
        self.image = Surface((self.width, self.height))
        self.image.fill(Color(SPACE_COLOR))
        draw.circle(self.image, Color(self.color),
                (self.width // 2, self.height // 2),
                sqrt(mass/2)/2)

    def copy(self):
        planet = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)
        planet.prev_state = self.prev_state
        return planet

    def state(self):
        return {"mass": self.mass,
                "x": self.x,
                "y": self.y,
                "vx": self.vx,
                "vy": self.vy,
                "vx12": self.vx12,
                "vy12": self.vy12,
                "ax": self.ax,
                "ay": self.ay,
                "color": self.color}

    def interact_euler(self, planet, step):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)
        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        # New speed based on accel
        new_state.vx += new_state.ax*step
        new_state.vy += new_state.ay*step

        # New pos based on speed
        new_state.x += self.vx*step
        new_state.y += self.vy*step
        return new_state

    def interact_eulerkramer(self, planet, step):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)
        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        # New speed based on accel
        new_state.vx += new_state.ax*step
        new_state.vy += new_state.ay*step

        # New pos based on speed
        new_state.x += new_state.vx*step
        new_state.y += new_state.vy*step
        return new_state

    def interact_halfstep(self, planet, passed, step):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)
        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        new_state.vx12 = self.vx12 + new_state.ax*step
        new_state.vy12 = self.vy12 + new_state.ay*step

        new_state.vx = self.vx + new_state.vx12
        new_state.vy = self.vy + new_state.vy12

        # New pos based on speed
        new_state.x += new_state.vx*step
        new_state.y += new_state.vy*step
        return new_state

    def interact_verle(self, planet, step):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)

        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        # New pos based on speed
        new_state.x = 2*self.x - self.prev_state.x + new_state.ax*(step**2)
        new_state.y = 2*self.y - self.prev_state.y + new_state.ay*(step**2)

        new_state.prev_state = self
        self.prev_state = None
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

    # Planet init
    planet = PlanetaryObject(x = 100, y = 290, vx = 0.1, vy = 3, ax = 0, ay = 0, mass = 100, curr_color = "blue")
    planet1 = PlanetaryObject(x=WIN_WIDTH-100, y=WIN_HEIGHT-290, vx=-0.1, vy=-3, ax=0, ay=0, mass=200, curr_color="green")
    # Sun
    sun = PlanetaryObject(x = WIN_WIDTH // 2, y = WIN_HEIGHT // 2, vx = 0, vy = 0, ax = 0, ay = 0, mass = 5000, curr_color = "yellow")

    time_clock = TimeClock(TIME_STEP)

    star_system = StarSystem(time_clock)
    star_system.add(planet)
    star_system.add(planet1)
    star_system.add(sun)

    done = False
    while not done:
        timer.tick(FRAMERATE)
        for e in pygame.event.get():
            if e.type == QUIT:
                done = True
                break
        for i in range(UPF):
            star_system.update_verle()
            time_clock.tick()
        # screen.blit(bg, (0, 0))
        for i in range(len(star_system.planets)):
            screen.blit(star_system.planets[i].image, (int(star_system.planets[i].x-star_system.planets[i].width/2),
                                                       int(star_system.planets[i].y-star_system.planets[i].height/2)))
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