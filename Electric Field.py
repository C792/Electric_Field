import pygame
import sys
import os
from pygame.locals import *

pygame.init()
pygame.font.init()

FPS = 45
fpsclock = pygame.time.Clock()

HEIGHT = 600
WIDTH  = 800
MOREPATH = ''

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("전기장 그리기")
try:
    pygame.display.set_icon(pygame.image.load(f"./{MOREPATH}electric field.png"))
except:
    MOREPATH = 'parkhong/'
    pygame.display.set_icon(pygame.image.load(f"./{MOREPATH}electric field.png"))
    

FIELD_DENSITY = 20
PARTICLE_SIZE = 32
DEFAULTCHARGE = 1
PLUS = pygame.transform.scale(
    pygame.image.load(f"./{MOREPATH}PLUS.png"), (PARTICLE_SIZE, PARTICLE_SIZE)
)
MINUS = pygame.transform.scale(
    pygame.image.load(f"./{MOREPATH}MINUS.png"), (PARTICLE_SIZE, PARTICLE_SIZE)
)
NEUTRAL = pygame.transform.scale(
    pygame.image.load(f"./{MOREPATH}NEUTRAL.png"), (PARTICLE_SIZE, PARTICLE_SIZE)
)

def sigmoid(x):
    return 20 * (1 / (1 + 2.71828 ** (-x * 100000 + 3)))

class vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return vector(self.x + other.x, self.y + other.y)

    def __mul__(self, num):
        return vector(num * self.x, num * self.y)

    def __neg__(self):
        return vector(-self.x, -self.y)

    def __sub__(self, other):
        return vector(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"<{self.x}, {self.y}>"

    def __abs__(self):
        return (self.x**2 + self.y**2) ** 0.5

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def unit(self):
        return self * (1 / abs(self))

    def st(self):
        return self.x + WIDTH // 2, HEIGHT // 2 - self.y


class Field_arrow:
    Objlist = []

    def __init__(self, pos):
        self.pos = pos
        self.field = vector(0, 0)
        self.Objlist.append(self)

    def update(self):
        self.field = vector(0, 0)
        for p in Particle.Objlist:
            r = self.pos - p.pos
            if not abs(r):
                return
            self.field += vector.unit(r) * p.charge * abs(r) ** -2
        if not abs(self.field):
            return
        self.field = vector.unit(self.field) * sigmoid(abs(self.field))

    def show(self):
        pygame.draw.aaline(
            DISPLAY,
            (120, 120, 120),
            vector.st(self.pos),
            vector.st(self.pos + self.field * 0.8),
            2,
        )
        pygame.draw.aaline(
            DISPLAY,
            (0, 0, 0),
            vector.st(self.pos + self.field * 0.8),
            vector.st(self.pos + self.field),
            2,
        )


def make_field():
    for x in range(-WIDTH // 2, WIDTH // 2, FIELD_DENSITY):
        for y in range(-HEIGHT // 2, HEIGHT // 2, FIELD_DENSITY):
            Field_arrow(vector(x, y))


make_field()


class Particle:
    Objlist = []

    def __init__(self, charge, mass, pos):
        self.charge = charge
        self.m = mass
        self.pos = pos
        self.Objlist.append(self)
        self.dragging = False

    def show(self):
        if self.charge > 0:
            DISPLAY.blit(
                PLUS,
                (
                    self.pos.x + WIDTH // 2 - PARTICLE_SIZE // 2,
                    HEIGHT // 2 - self.pos.y - PARTICLE_SIZE // 2,
                ),
            )
        elif self.charge < 0:
            DISPLAY.blit(
                MINUS,
                (
                    self.pos.x + WIDTH // 2 - PARTICLE_SIZE // 2,
                    HEIGHT // 2 - self.pos.y - PARTICLE_SIZE // 2,
                ),
            )
        else:
            DISPLAY.blit(
                NEUTRAL,
                (
                    self.pos.x + WIDTH // 2 - PARTICLE_SIZE // 2,
                    HEIGHT // 2 - self.pos.y - PARTICLE_SIZE // 2,
                ),
            )

class ForceLine(Particle):
    Objlist = []

    def __init__(self, pos):
        self.pos = pos
        self.vel = 0
        self.acc = 0

Particle(DEFAULTCHARGE, 1, vector(-100, 0))
Particle(DEFAULTCHARGE, 1, vector(100, 0))
LCTRL = False
while 1:
    event = pygame.event.poll()
    if event.type == QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == MOUSEBUTTONDOWN:
        if event.button == 1 and LCTRL:
            Particle(
                1, 1, vector(event.pos[0] - WIDTH // 2, HEIGHT // 2 - event.pos[1])
            )


        for p in Particle.Objlist:
            if (
                abs(
                    p.pos
                    - vector(event.pos[0] - WIDTH // 2, HEIGHT // 2 - event.pos[1])
                )
                <= PARTICLE_SIZE // 2 + 1
            ):
                if event.button == 1:
                    p.dragging = True
                elif event.button == 2:
                    Particle.Objlist.remove(p)
                elif event.button == 3:
                    if LCTRL:
                        p.charge += 1
                    else:
                        p.charge *= -1
                break
    elif event.type == MOUSEBUTTONUP:
        for p in Particle.Objlist:
            p.dragging = False

    elif event.type == KEYDOWN:
        if event.key == K_LCTRL:
            LCTRL = True
    elif event.type == KEYUP:
        if event.key == K_LCTRL:
            LCTRL = False
    DISPLAY.fill((255, 255, 255))

    for p in Particle.Objlist:
        if p.dragging:
            mousepos = pygame.mouse.get_pos()
            p.pos = vector(mousepos[0] - WIDTH // 2, HEIGHT // 2 - mousepos[1])
        p.show()
        for f in Field_arrow.Objlist:
            r = f.pos - p.pos
            # if not abs(r):
            #     continue

    for a in Field_arrow.Objlist:
        a.update()
        a.show()

    for p in Particle.Objlist:
        p.show()

    pygame.display.update()
    fpsclock.tick(FPS)
