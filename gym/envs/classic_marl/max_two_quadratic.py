import logging
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from gym.envs.classic_marl import field

logger = logging.getLogger(__name__)



class MaxTwoQuadraticEnv(gym.Env):

	def __init__(self):
		self.stochastic = False
		self.action_space = spaces.Box(-30,30, 2)
		self.observation_space = spaces.Box(1,1,1)
		self.x1,self.y1,self.x2,self.y2 = -15,-15,15,15
		self.h1,self.h2 = 100,20
		self.s1,self.s2 = 3,32.0


	def _seed(self, seed=None):
		self.np_random, seed = seeding.np_random(seed)
		return [seed]

	def _reset(self):
		self.stochastic = False

	def _step(self, action):
		action1 = action[0]
		action2 = action[1]
		
		f1 = h1*(1 - (((action1-x1)/s1)*((action1-x1)/s1)) - (((action2-y1)/s1)*((action2-y1)/s1))) + 50
		f2 = h2*(1 - (((action1-x2)/s2)*((action1-x2)/s2)) - (((action2-y2)/s2)*((action2-y2)/s2))) - 50
	
		ret = max(f1, f2, -150)
		if self.stochastic:
			ret = ret + np.random.normal(0,10)
	
		return ret, ret, True, {}

		def set_x1(self, val):
			self.x1 = val
		def set_x2(self, val):
			self.x2 = val
		def set_y1(self, val):
			self.y1 = val
		def set_y2(self, val):
			self.y2 = val
		def set_h1(self, val):
			self.h1 = val
		def set_h2(self, val):
			self.h2 = val
		def set_s1(self, val):
			self.s1 = val
		def set_s2(self, val):
			self.s2 = val