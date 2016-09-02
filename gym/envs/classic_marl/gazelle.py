
import math

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