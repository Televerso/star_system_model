from platform import system
from tkinter import *
from tkinter import ttk
import re
from tkinter.tix import LabelEntry
from tkinter.ttk import Labelframe

import numpy as np
import pygame
from pygame import *
from math import *

pygame.init()

WIN_WIDTH = 800
WIN_HEIGHT = 640
PLANET_WIDTH = 20
PLANET_HEIGHT = 20
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
SPACE_COLOR = "#000022"
COLOR_LIST = [
[255,255,0],
[0,0,255],
[0,255,0],
[255,0,0],
[255,0,255],
[0,255,255],
[128,0,255],
[128,128,128],
[255,128,0],
[128,255,0]
]
N_PARAMS = 5
PARAM_LIST = [
[WIN_WIDTH // 2, WIN_HEIGHT // 2, 0, 0, 5000], # The sun
    [100, 290, 0.1, 3, 100], # Planet 1
    [WIN_WIDTH-100, WIN_HEIGHT-290, -0.1, -3, 200], # Planet 2
    [WIN_WIDTH // 2, WIN_HEIGHT, 3, 0, 50], # Planet 3
    [WIN_WIDTH // 2, 0, -4, -0.1, 50] # Planet 4
]

FRAMERATE = 30
timer = pygame.time.Clock()

FONT = pygame.font.Font(None, 32)
LABEL_FONT = pygame.font.Font(None, 16)
COLOR_TEXT_INACTIVE = pygame.Color('lightskyblue3')
COLOR_TEXT_ACTIVE = pygame.Color('dodgerblue2')

class ParameterDialogueWindow(Tk):
    def __init__(self, n):
        super().__init__()
        self.title("Ввод параметров")
        self.geometry("700x300")

        self.label = Label(text="Ввод параметров системы:")  # создаем текстовую метку
        self.label.pack(anchor="n", fill="x")  # размещаем метку в окне

        self.frame = ttk.Frame(borderwidth=1, relief=SOLID, padding=[8, 10])
        weight = 1

        for i in range(n):
            self.columnconfigure(i, weight=weight)
        for param in range(N_PARAMS):
            self.rowconfigure(param, weight=weight)

        check = (self.register(self.is_valid), "%P")

        self.errmsg = StringVar()

        self.entry_list = [[ttk.Entry(self.frame, validate="key", validatecommand=check) for i in range(N_PARAMS)] for j in range(n)]
        self.param_list = [{"mass": 0.0,
                       "x": 0.0,
                       "y": 0.0,
                       "vx": 0.0,
                       "vy": 0.0,
                       "vx12": 0.0,
                       "vy12": 0.0,
                       "ax": 0.0,
                       "ay": 0.0,
                       "color": pygame.Color(COLOR_LIST[i])} for i in range(len(self.entry_list))]

        ttk.Label(self.frame, text='x').grid(row=0, column=1)
        ttk.Label(self.frame, text='y').grid(row=0, column=2)
        ttk.Label(self.frame, text='vx').grid(row=0, column=3)
        ttk.Label(self.frame, text='vy').grid(row=0, column=4)
        ttk.Label(self.frame, text='Масса').grid(row=0, column=5)

        for i in range(0, n):
            ttk.Label(self.frame, text=str("Тело №")+str(i+1)).grid(row=i+1, column=0)

        for i in range(0, n):
            for param in range(0, N_PARAMS):
                self.entry_list[i][param].grid(row = i+1, column = param+1)
                self.entry_list[i][param].insert(0, str(PARAM_LIST[i][param]))

        self.frame.pack(fill="x", expand=True)

        self.btn = ttk.Button(self, text="Ввод")
        self.btn["command"] = self.click_button
        self.btn.pack(anchor="s")

    def is_valid(self, newval):
        result = re.match("^-?\d+\.?\d*$", newval) is not None
        if not result and len(newval) <= 12:
            self.errmsg.set("Номер телефона должен быть в формате +xxxxxxxxxxx, где x представляет цифру")
        else:
            self.errmsg.set("")
        return result

    def click_button(self):
        for i in range(len(self.entry_list)):
            self.param_list[i]["x"] = float(self.entry_list[i][0].get())
            self.param_list[i]["y"] = float(self.entry_list[i][1].get())
            self.param_list[i]["vx"] = float(self.entry_list[i][2].get())
            self.param_list[i]["vy"] = float(self.entry_list[i][3].get())
            self.param_list[i]["mass"] = float(self.entry_list[i][4].get())
        self.close()
        return self

    def open(self):
        self.mainloop()

    def close(self):
        param_list = self.param_list
        self.destroy()
        return param_list

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_TEXT_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        box_text = ''
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_TEXT_ACTIVE if self.active else COLOR_TEXT_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    box_text = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)
        return box_text

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

class TimeClock:
    def __init__(self, time_step_loc):
        self.time_passed = 0
        self.n_steps = 0
        self.time_step = time_step_loc

    def tick(self):
        self.time_passed += self.time_step
        self.n_steps += 1

    def set_time_step(self, time_step):
        self.time_step = time_step

    def get_time_passed(self):
        return self.time_passed

    def get_time_step(self):
        return self.time_step

    def get_n_steps(self):
        return self.n_steps

    def reset(self):
        self.time_passed = 0
        self.n_steps = 0

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
                                                                                                self.timer.get_time_step())
        self.planets = new_star_system.planets
        return new_star_system

    def update_verle(self):
        new_star_system = StarSystem(self.timer)
        for planet in self.planets:
            new_star_system.add(planet.copy())

        if (self.timer.get_n_steps() < 1):
            for i in range(len(self.planets)):
                for j in range(len(self.planets)):
                    if i == j:
                        continue
                    else:
                        new_star_system.planets[i] = new_star_system.planets[i].interact_eulerkramer(self.planets[j],
                                                                                               self.timer.get_time_step()/3)
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

    def update_biman(self):
        new_star_system = StarSystem(self.timer)
        for planet in self.planets:
            new_star_system.add(planet.copy())

        prev_accs_arr = np.empty(shape=[len(self.planets),len(self.planets),2])

        if (self.timer.get_n_steps() < 2):
            for i in range(len(self.planets)):
                for j in range(len(self.planets)):
                    if i == j:
                        continue
                    else:
                        new_star_system.planets[i] = new_star_system.planets[i].interact_eulerkramer(self.planets[j],
                                                                                               self.timer.get_time_step())
                        r = sqrt((self.planets[i].x - self.planets[j].x) ** 2 + (self.planets[j].y - self.planets[i].y) ** 2)
                        prev_accs_arr[i,j,0] = self.planets[j].mass * (self.planets[j].x - self.planets[i].x) / r ** 3
                        prev_accs_arr[i, j, 1] = self.planets[j].mass * (self.planets[j].y - self.planets[i].y) / r ** 3
                new_star_system.planets[i].prev_state = self.planets[i]
        else:
            for i in range(len(self.planets)):
                for j in range(len(self.planets)):
                    if i == j:
                        continue
                    else:
                        r = sqrt(
                            (self.planets[i].x - self.planets[j].x) ** 2 + (self.planets[j].y - self.planets[i].y) ** 2)
                        prev_accs_arr[i, j, 0] = self.planets[j].mass * (self.planets[j].x - self.planets[i].x) / r ** 3
                        prev_accs_arr[i, j, 1] = self.planets[j].mass * (self.planets[j].y - self.planets[i].y) / r ** 3
                        new_star_system.planets[i] = new_star_system.planets[i].interact_biman_spatial(self.planets[j],
                                                                                               self.timer.get_time_step())
                        new_star_system.planets[i] = new_star_system.planets[i].interact_biman_vel(new_star_system.planets[j],
                                                                                                       self.timer.get_time_step(),
                                                                                                   prev_accs_arr[i,j,0], prev_accs_arr[i,j,1])
        self.planets = new_star_system.planets
        return new_star_system

    def update_collision(self):
        in_update = [False,0,0]
        for i in range(len(self.planets)):
            for j in range(len(self.planets)):
                if i >= j: continue
                else:
                    r = sqrt((self.planets[i].x - self.planets[j].x) ** 2 + (self.planets[i].y - self.planets[j].y) ** 2)
                    margin_range = (sqrt(self.planets[i].mass/2) + sqrt(self.planets[j].mass/2))/2
                    if r < margin_range:
                        in_update[0] = True
                        in_update[1] = i
                        in_update[2] = j

        if in_update[0]:
            new_star_system = StarSystem(self.timer)
            for i in range(len(self.planets)):
                if i == in_update[1]: continue
                if i == in_update[2]: continue
                else: new_star_system.add(self.planets[i].copy())

            mass = self.planets[in_update[1]].mass + self.planets[in_update[2]].mass
            x = ((self.planets[in_update[1]].x * self.planets[in_update[1]].mass +
                                  self.planets[in_update[2]].x * self.planets[in_update[2]].mass) /
                                 mass)
            y = ((self.planets[in_update[1]].y * self.planets[in_update[1]].mass +
                                  self.planets[in_update[2]].y * self.planets[in_update[2]].mass) /
                                 mass)
            vx = ((self.planets[in_update[1]].prev_state.vx * self.planets[in_update[1]].mass +
                  self.planets[in_update[2]].prev_state.vx * self.planets[in_update[2]].mass) /
                  (mass))
            vy = ((self.planets[in_update[1]].prev_state.vy * self.planets[in_update[1]].mass +
                   self.planets[in_update[2]].prev_state.vy * self.planets[in_update[2]].mass) /
                  (mass))
            ax = 0
            ay = 0
            color_planet = pygame.Color(0, 0, 0)
            color_planet.r = int((self.planets[in_update[1]].color.r * self.planets[in_update[1]].mass +
                   self.planets[in_update[2]].color.r * self.planets[in_update[2]].mass) /
                  mass)
            color_planet.g = int((self.planets[in_update[1]].color.g * self.planets[in_update[1]].mass +
                               self.planets[in_update[2]].color.g * self.planets[in_update[2]].mass) /
                              mass)
            color_planet.b = int((self.planets[in_update[1]].color.b * self.planets[in_update[1]].mass +
                               self.planets[in_update[2]].color.b * self.planets[in_update[2]].mass) /
                              mass)

            new_star_system.add(PlanetaryObject(x = x, y = y, vx = vx, vy = vy, ax = ax, ay = ay, mass = mass, curr_color = color_planet))
            self.planets = new_star_system.planets
            self.update_eulerkramer()
            return new_star_system
        else:
            return self

class PlanetaryObject:
    def __init__(self, mass:float, x=0.0, y=0.0, vx=0.0, vy=0.0, ax=0.0, ay=0.0, curr_color = Color(COLOR_LIST[0])):
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
        self.color = Color(curr_color)
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
        new_state.prev_state=self
        self.prev_state = None
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
        new_state.prev_state = self
        self.prev_state = None
        return new_state

    def interact_halfstep(self, planet, step):
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

    def interact_biman_spatial(self, planet, step):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)

        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        r_prev = sqrt((self.prev_state.x - planet.prev_state.x) ** 2 + (self.prev_state.y - planet.prev_state.y) ** 2)

        ax_prev = planet.mass * (planet.prev_state.x - self.prev_state.x) / r_prev ** 3
        ay_prev = planet.mass * (planet.prev_state.y - self.prev_state.y) / r_prev ** 3

        # New pos based on speed
        new_state.x = self.x + self.vx * step - (1/6)*(4*new_state.ax-ax_prev)*(step**2)
        new_state.y = self.y + self.vy * step - (1/6)*(4*new_state.ay-ay_prev)*(step**2)
        new_state.prev_state = self
        self.prev_state = None
        return new_state

    def interact_biman_vel(self, planet, step, prev_acc_x, prev_acc_y):
        new_state = PlanetaryObject(self.mass, self.x, self.y, self.vx, self.vy, self.ax, self.ay, self.color)

        r = sqrt((self.x - planet.x) ** 2 + (self.y - planet.y) ** 2)

        new_state.ax = planet.mass * (planet.x - self.x) / r ** 3
        new_state.ay = planet.mass * (planet.y - self.y) / r ** 3

        r_prev = sqrt((self.prev_state.x - planet.prev_state.x) ** 2 + (self.prev_state.y - planet.prev_state.y) ** 2)

        ax_prev = planet.mass * (planet.prev_state.x - self.prev_state.x) / r_prev ** 3
        ay_prev = planet.mass * (planet.prev_state.y - self.prev_state.y) / r_prev ** 3

        new_state.vx = self.vx + (1 / 6) * (2 * new_state.ax + 5*ax_prev - prev_acc_x)*step
        new_state.vy = self.vy + (1 / 6) * (2 * new_state.ay + 5 * ay_prev - prev_acc_y) * step

        new_state.prev_state = self
        self.prev_state = None
        return new_state

# TODO pause button
# TODO fix verle with collision

def main():
    # PyGame init
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Solar Mechanics v0.1")

    # Space init
    bg = Surface((WIN_WIDTH-200, WIN_HEIGHT))
    bg.fill(Color(SPACE_COLOR))

    label_bg = Surface((200, WIN_HEIGHT))
    label_bg.fill(Color(Color(200, 200, 200)))

    time_step = 0.005
    time_clock = TimeClock(time_step)

    ups_input_box = InputBox(0, WIN_HEIGHT-260, 80, 40)
    step_input_box = InputBox(0, WIN_HEIGHT-180, 80, 40)
    n_planet_box = InputBox(0, WIN_HEIGHT-100, 80, 40)

    input_boxes = [ ups_input_box, step_input_box, n_planet_box]

    n = 0
    planets = []
    star_system = StarSystem(time_clock)

    upf_system = 1

    ups_label = LABEL_FONT.render(str("Текущий UPS = " + str(upf_system*30)), True, COLOR_TEXT_ACTIVE)
    step_label = LABEL_FONT.render(str("Текущий шаг = " + str(time_step)), True, COLOR_TEXT_ACTIVE)
    system_label = LABEL_FONT.render("Редактирование системы:", True, COLOR_TEXT_ACTIVE)
    n_planet_label = LABEL_FONT.render("Количество планет: " + str(str(n)), True, COLOR_TEXT_ACTIVE)

    labels = [ups_label, step_label, system_label, n_planet_label]

    done = False
    while not done:
        timer.tick(FRAMERATE)
        for e in pygame.event.get():
            if e.type == QUIT:
                done = True
                break

            ups_box_text = ups_input_box.handle_event(e)
            if ups_box_text.isdigit() and (30 < int(ups_box_text) <= 10000):
                upf_system = int(int(ups_box_text)/30)

            step_box_text = step_input_box.handle_event(e)
            if step_box_text.isdigit() and 0 < int(step_box_text) <= 10000:
                time_step = round(int(step_box_text) / 3600, 5)
                time_clock.set_time_step(time_step)

            n_planet_box_text = n_planet_box.handle_event(e)
            if n_planet_box_text.isdigit() and 0 < int(n_planet_box_text) <= 5:
                n = int(n_planet_box_text)
                root = ParameterDialogueWindow(n)
                root.open()
                params = root.param_list
                time_clock = TimeClock(time_step)
                star_system = StarSystem(time_clock)
                for i in range(n):
                    planet = PlanetaryObject(mass=params[i].get("mass"),
                                             x=params[i].get("x"),
                                             y=params[i].get("y"),
                                             vx=params[i].get("vx"),
                                             vy=params[i].get("vy"),
                                             ax=params[i].get("ax"),
                                             ay=params[i].get("ay"),
                                             curr_color=params[i].get("color"))
                    star_system.add(planet)



        for box in input_boxes:
            box.update()

        for i in range(upf_system):
            star_system.update_biman()
            star_system.update_collision()
            time_clock.tick()
        screen.blit(bg, (200, 0))
        for i in range(len(star_system.planets)):
            screen.blit(star_system.planets[i].image, (int(star_system.planets[i].x-star_system.planets[i].width/2),
                                                       int(star_system.planets[i].y-star_system.planets[i].height/2)))


        ups_label = LABEL_FONT.render(str("Текущий UPS = " + str(upf_system*30)), True, COLOR_TEXT_ACTIVE)
        step_label = LABEL_FONT.render(str("Текущий шаг = " + str(time_step)), True, COLOR_TEXT_ACTIVE)
        n_planet_label = LABEL_FONT.render("Количество планет: " + str(str(n)), True, COLOR_TEXT_ACTIVE)

        screen.blit(label_bg, (0, 0))
        screen.blit(ups_label, (10, WIN_HEIGHT - 280))
        screen.blit(step_label, (10, WIN_HEIGHT - 200))
        screen.blit(system_label, (10, WIN_HEIGHT - 120))
        screen.blit(n_planet_label, (10, WIN_HEIGHT - 60))
        for box in input_boxes:
            box.draw(screen)

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