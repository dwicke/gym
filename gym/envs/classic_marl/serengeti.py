"""
Classic predator prey system.
"""

import logging
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from gym.envs.classic_marl import field

logger = logging.getLogger(__name__)

class Lion():
    def __init__(self, maxStep, field):
        print ("created lion")
        self.xpos = 0
        self.ypos = 0
        self.theta = 0
        self.maxStep = maxStep
        self.field = field
    

    def reset(self, xpos, ypos, theta):
        self.xpos = xpos
        self.ypos = ypos
        self.theta = theta
    

    def getX(self):
        return self.xpos


    def getY(self):
        return self.ypos
    


    def step(self, action):
        ##dir = self.rotate(self.maxStep, 0, math.random()*2*math.pi)
        direction = self.rotate(self.maxStep, 0, action)
        oldx = self.xpos
        oldy = self.ypos
        self.xpos = self.field.stx(self.xpos + direction[0])
        self.ypos = self.field.sty(self.ypos + direction[1])


    

    def colidedWith(self, l):
        vx, vy = self.field.tv(self.xpos, l.getX(), self.ypos, l.getY())
        if math.sqrt(vx*vx + vy*vy) <= 2.0:
                return 0.0
        
        return 0.0
    


    def rotate(self, x, y, theta):
        sinTheta = math.sin(theta)
        cosTheta = math.cos(theta)
        xp = cosTheta * x + -sinTheta * y
        yp = sinTheta * x + cosTheta * y
        return [xp, yp]


class Gazelle():

    def __init__(self, maxFieldLength, lions, field, stepSize):
        self.xpos = 0
        self.ypos = maxFieldLength / 2
        self.maxFieldLength = maxFieldLength
        self.lions = lions
        self.field = field
        self.stepSize = stepSize
        self.dead = -1
        self.deathRange = 2

    def reset(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.dead = -1

    def step(self, lions):
        if self.dead == 1:
            return
        
        xp = 0.0
        yp = 0.0
        for l in lions:
            vx, vy = self.field.tv(l.getX(), self.xpos, l.getY(), self.ypos)
            vLen = math.sqrt(vx*vx + vy*vy)
            scale = (self.maxFieldLength - vLen) / vLen
            xp = xp + vx * scale
            yp = yp + vy * scale
        
        xp = -1*xp
        yp = -1*yp

        len = math.sqrt(xp*xp + yp*yp)
        if len > 0.01:
            xp = xp * (self.stepSize / len)
            yp = yp * (self.stepSize / len)
        else:
            print("Gazelle is not moving!")
        
        self.xpos = self.field.stx(self.xpos + xp)
        self.ypos = self.field.sty(self.ypos + yp)


    ## returns -1 if not dead
    ## returns 1 if dead
    def isDead(self, lions):
        print("Checking if Gazelle is dead")
        for l in lions:
            vx, vy = self.field.tv(self.xpos, l.getX(), self.ypos, l.getY())
            if math.sqrt(vx*vx + vy*vy) <= self.deathRange:
                self.dead = 1
                return True
            
        
        self.dead = -1
        return False
    


    def getX(self):
        return self.xpos
    

    def getY(self):
        return self.ypos


class SerengetiEnv(gym.Env):


    def __init__(self):
        self.a = [-1111, 0,1,1,0] ## converted from lua...
    	self.numLions = 4
        self.lions = []
    	self.width = 4
    	self.height = 4

        self.maxLen = math.sqrt((self.width/2)*(self.width/2) + (self.height/2)*(self.height/2))
        self.lionJump = 1
        self.gazelleJump = 3
        self.minPosition = 0
        self.maxPosition = 4
        self.field = field.ContinuousField(self.width, self.height)
        self.terminal = False

        for i in range(0, self.numLions ):
            self.lions.append(Lion(self.lionJump, self.field))
      
        self.gazelle = Gazelle(self.maxLen, self.lions, self.field, self.gazelleJump)

    	self.action_space = spaces.Box(0,2*math.pi, self.numLions) ## the direction the lion will face
        self.observation_space = spaces.Box(np.array([0,0]),np.array([self.width, self.height]))

        self._seed()
        self.reset()
        self.viewer = None

        self.steps_beyond_done = None

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def _step(self, action):
    	## The action is the angle of the agents want to face
        reward = -1

        self.gazelle.step(self.lions)

        i = 0
        for l in self.lions:
            l.step(action[i])
            i = i + 1
        

        for i in range(0, self.numLions):
            for j in range(i+1, self.numLions):
                reward = reward + self.lions[i].colidedWith(self.lions[j])


        if self.gazelle.isDead(self.lions):
            self.terminal = True
            reward = 1
        

        coords = [self.numLions + 1]
        
        for l in self.lions:
            coords.append([l.getX(), l.getY()])
            i = i + 1
        coords.append([self.gazelle.getX(), self.gazelle.getY()])
        

        return coords, reward, self.terminal, {}


    def _reset(self):
        
        i = 1
        for l in self.lions:
            l.reset(self.maxPosition * (i % 2) + 3 * -1 * (i % 2), (self.maxPosition) * self.a[i] + 3 * -1 * self.a[i], math.pi / 2)
            i = i + 1
    	
        self.gazelle.reset(self.maxPosition / 4,self.maxPosition / 2)


        coords = [self.numLions + 1]
        for l in self.lions:
            coords.append([l.getX(), l.getY()])
        coords.append([self.gazelle.getX(), self.gazelle.getY()])

        return coords
    def _render(self, mode='human', close=False):
        return

