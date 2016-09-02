import math

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
	