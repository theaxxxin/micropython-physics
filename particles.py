##--Micropython--##
##--ESP32 with 1.3Inch OLED Via i2c--##
#
#
# --- First of all, this project could not have been completed without help from various members of the global programming community. As and when people help me, I will add them to this list which I hope will be maintained
# --- Special thanks to Mattia Conti, Deshipu (Radomir Dopieralski), and 20GOTO10 from discord. If you all ever see this, you guys rock!
#
# ----- CODE FINALLY WORKING!----

from machine import Pin, I2C

import sh1106
import math
import time
import random

# ESP32 Pin assignment for display (DONT IGNORE)
i2c = I2C(scl=Pin(14), sda=Pin(27), freq=400000)

# Display Init Sequence ----
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)
display.sleep(False)
display.fill(0)


# ------

class particle:

    def __init__(self, iposition, mass, velocity, index):
        self.position = iposition
        self.mass = mass
        self.velocity = velocity
        self.index = index
        self.isscatter = True
        self.speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        self.update()

    def move(self):
        self.clear()
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.update()

    def update(self):
        #text = "X pos :{0},yPos: {1}".format(self.position[0], self.position[1])
        #print(text)
        ## The code below draws a pixel at the x and y position of the particle when called (Last parameter is colour, can either be 0 or 1)
        display.pixel(int(round(self.position[0])), int(round(self.position[1])), 1)

    def clear(self):
        ## The code below draws a pixel at the x and y position of the particle when called (Last parameter is colour, can either be 0 or 1)
        display.pixel(int(round(self.position[0])), int(round(self.position[1])), 0)

    def intersection(self, particles, nparticles):
        for i in range(nparticles):
            if i != self.index:
                x = self.position[0] - particles[i].position[0]
                y = self.position[1] - particles[i].position[1]
                if x ** 2 + y ** 2 < 1:
                    #print('true')
                    return [True, i]
        #print('false')
        return [False]

    def scatter(self, particles, nparticles):
        where = self.intersection(particles, nparticles)
        if where[0] and particles[where[1]].isscatter:
            # avoid multiple scatters at same moment
            particles[where[1]].isscatter = False
            self.isscatter = False

            # Total and Difference Mass to Simplify Calculation
            totalmass = self.mass + particles[where[1]].mass
            massdiff = self.mass - particles[where[1]].mass

            # store velocity variable to avoid error caused by sequential calculation

            tempvelocity = [self.velocity[0], self.velocity[1]]

            self.velocity[0] = (massdiff * self.velocity[0] + 2 * particles[where[1]].mass *
                                particles[where[1]].velocity[0]) / totalmass
            self.velocity[1] = (massdiff * self.velocity[1] + 2 * particles[where[1]].mass *
                                particles[where[1]].velocity[1]) / totalmass
            particles[where[1]].velocity[0] = (-massdiff * tempvelocity[0] + 2 * self.mass * tempvelocity[
                0]) / totalmass
            particles[where[1]].velocity[1] = (-massdiff * tempvelocity[1] + 2 * self.mass * tempvelocity[
                1]) / totalmass


class fixsurface:

    def __init__(self, positionstart, positionend):
        self.position = positionstart + positionend

        # where the surface starts and ends
        self.positionstart = positionstart
        self.positionend = positionend
        # self.length = math.sqrt((positionend[1]-positionstart[1])**2 + (positionend[0]-positionstart[0]))
        self.xtype = True
        self.m = 0
        self.q = 0
        self.alpha = 0
        self.calculatemq = 0
        self.update()

    def calculatemq(self):
        # Calculate coefficient that descrives the segment as a straig line (Angular Coeffecient)
        deltay = self.positionend[1] - self.positionstart[1]
        deltax = self.positionend[0] - self.positionstart[0]
        if abs(deltax) > 0:
            self.m = deltay / deltax
            self.q - self.positionstart[1] - self.m * self.positionstart[0]
            self.alpha = math.atan(self.m)
        else:
            self.xtype = False
            self.alpha = math.pi / 2

    def update(self):
        display.line(int(round(self.positionstart[0])), int(round(self.positionstart[1])),
                     int(round(self.positionend[0])), int(round(self.positionend[1])), 1)

    def intersection(self, particles, nparticles):
        # Get the position where particles hit the segment
        for i in range(nparticles):
            if self.xtype:
                y = self.m * particles[i].position[0] + self.q
                if abs(y - particles[i].position[1]) < 40:
                    return [True, i]
                else:
                    x = self.positionstart[0]
                    if abs(x - particles[i].position[0]) < 40:
                        return [True, i]

        return [False]

    def scatter(self, particles, nparticles):
        where = self.intersection(particles, nparticles)
        if where[0]:
            tempvx = particles[where[1]].velocity[0]
            tempvy = particles[where[1]].velocity[1]
            particles[where[1]].velocity[0] = math.cos(2 * self.alpha) * tempvx + math.sin(2 * self.alpha) * tempvy
            particles[where[1]].velocity[1] = math.cos(2 * self.alpha) * tempvx + math.cos(2 * self.alpha) * tempvy


Nparticles = 20
rangeparticles = range(Nparticles)
mainparticles = []
for i in rangeparticles:
    mainparticles += [particle([random.uniform(3, 126), random.uniform(3, 61)], 5,
                               [random.uniform(-2, 2), random.uniform(-2, 2)], i)]

# mainparticles += [particle([10, 30], 30, [1, 0], 0)]
# mainparticles += [particle([80, 30], 400, [-1, 0], 1)]


# Create Surfaces
Nsurfaces = 4
rangesurfaces = range(Nsurfaces)
surfaces = []
surfaces += [fixsurface([2, 2], [126, 2])]
surfaces += [fixsurface([126,2], [126, 62])]
surfaces += [fixsurface([126,62], [2, 62])]
surfaces += [fixsurface([2, 62], [2, 2])]

while True:

    # Clear, Scatter, move and update

    for i in rangeparticles:
        # CLEAR PARTICLES
        mainparticles[i].clear()

    for i in rangesurfaces:
        # DRAW SURFACES
        surfaces[i].update()
        surfaces[i].scatter(mainparticles, Nparticles)
    
    for i in rangeparticles:
      
        mainparticles[i].scatter(mainparticles, Nparticles)

    for i in rangeparticles:
        mainparticles[i].isscatter = True
        mainparticles[i].move()

    for i in rangeparticles:
        mainparticles[i].update()
    display.show()








