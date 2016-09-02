
class ContinuousField():
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def stx(self, x, width=None):
		width = width or self.width
		if x >= 0:
			if x < width:
				return x
			return x - width
		return x + width;

	def tdx(self, x1, x2, width = None):
		width = width or self.width
		if abs(x1- x2) <= (width / 2):
			return x1 - x2
		
		dx = self.stx(x1, width) - self.stx(x2, width)
		if dx * 2 > width:
			return dx - width
		
		if dx * 2 < -width:
			return dx + width
		
		return dx



	def sty(self, y, height = None):
		height = height or self.height
		if y >= 0:
			if y < height:
				return y
			return y - height
		
		return y + height;


	def tdy(self, y1, y2, height):
		if abs(y1- y2) <= (height / 2):
			return y1 - y2
		
		dy = self.sty(y1, height) - self.sty(y2, height)
		if dy * 2 > height:
			return dy - height
		
		if dy * 2 < -height:
			return dy + height
		
		return dy

	def tv(self, x1, x2, y1, y2):
		return self.tdx(x1,x2, self.width), self.tdy(y1, y2, self.height)
