##--Micropython--##
##--ESP32 with 1.3Inch OLED Via i2c--##
#
#
#--- First of all, this project could not have been completed without help from various members of the global programming community. As and when people help me, I will add them to this list which I hope will be maintained
#--- Special thanks to Mattia Conti, Deshipu (Radomir Dopieralski), and 20GOTO10 from discord. If you all ever see this, you guys rock!
#
#----- CODE FINALLY WORKING!----

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

    def __init__(self, iposition, mass, velocity,index):
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
        text = "X pos :{0},yPos: {1}".format(self.position[0], self.position[1])
        print(text)
        ## The code below draws a pixel at the x and y position of the particle when called (Last parameter is colour, can either be 0 or 1)
        display.pixel(int(round(self.position[0])), int(round(self.position[1])),1)
    
        
    def clear(self):
        ## The code below draws a pixel at the x and y position of the particle when called (Last parameter is colour, can either be 0 or 1)
        display.pixel(int(round(self.position[0])), int(round(self.position[1])),0)
         
        




    def intersection(self, particles, nparticles):
        for i in range(nparticles):
            if i != self.index:
                x = self.position[0] - particles[i].position[0]
                y = self.position[1] - particles[i].position[1]
                if x ** 2 + y ** 2 < 1:
                    print('true')
                    return [True, i]
        print('false')
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


Nparticles = 2
rangeparticles = range(Nparticles)
mainparticles = []
mainparticles += [particle([10,30],30,[1,0],0)]
mainparticles += [particle([80,30],400,[-1,0],1)]

while True:
    
    #Clear, Scatter, move and update
    
    for i in rangeparticles:
        mainparticles[i].clear()
        
        
    for i in rangeparticles:
        mainparticles[i].scatter(mainparticles,Nparticles)
       

    for i in rangeparticles:
        mainparticles[i].isscatter = True
        mainparticles[i].move()

    for i in rangeparticles:
         mainparticles[i].update()
    display.show()


