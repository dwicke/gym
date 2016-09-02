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
from gym.envs.classic_marl import lion
from gym.envs.classic_marl import gazelle

logger = logging.getLogger(__name__)




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
            self.lions.append(lion.Lion(self.lionJump, self.field))
      
        self.gazelle = gazelle.Gazelle(self.maxLen, self.lions, self.field, self.gazelleJump)

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