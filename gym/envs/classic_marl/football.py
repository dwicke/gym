import logging
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from gym.envs.classic_marl import field

logger = logging.getLogger(__name__)


math.sign = lambda x: x<0 and -1 or x>0 and 1 or 0 

class Attacker():

    def __init__(self, maxFieldSize, field, xpos, ypos):

        self.xpos = xpos
        self.ypos = ypos
        self.field = field
        self.maxFieldSize = maxFieldSize
        self.maxStep = 1
        self.endzone = 0


    def reset(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos


    def step(self, action, defender):
        dir = self.rotate(self.maxStep, 0, action)
        oldx = self.xpos
        oldy = self.ypos
        self.xpos = self.field.stx(self.xpos + dir[0])
        self.ypos = self.field.sty(self.ypos + dir[1])


        defenderLoc = defender.getDefenderPoints()

        ## if my new x position is greater than the max step size (due to wrapping) then
        if abs(oldx - self.xpos) > self.maxFieldSize:
            ##create the point at which it wraps around

            if oldx < self.xpos:
                ## I have wrapped on the low end to the high end
                ## so then we have x = 0 be the second point
                ## subtract since y decreases going up...
                midpointLow = [0, oldy - abs(oldx - self.xpos)*math.tan(action[0])]
                midpointHigh = [self.maxFieldSize, oldy - abs(oldx - self.xpos)*math.tan(action[0])]
            else:
                ## I have wrapped from the high end to the low end
                midpointLow = [self.maxFieldSize, oldy - abs(oldx - self.xpos)*math.tan(action[0])]
                midpointHigh = [0, oldy - abs(oldx - self.xpos)*math.tan(action[0])]
            


            if len(defenderLoc) == 2:
                intersects = self.checkIntersect([oldx, oldy], midpointLow, defenderLoc[0], defenderLoc[1]) or self.checkIntersect(midpointHigh, [self.xpos, self.ypos], defenderLoc[0], defenderLoc[1])
            else: ## it crosses
                intersects = self.checkIntersect([oldx, oldy], midpointLow, defenderLoc[0], defenderLoc[1]) or self.checkIntersect(midpointHigh, [self.xpos, self.ypos], defenderLoc[0], defenderLoc[1]) or self.checkIntersect([oldx, oldy], midpointLow, defenderLoc[2], defenderLoc[3]) or self.checkIntersect(midpointHigh, [self.xpos, self.ypos], defenderLoc[2], defenderLoc[3])
            

        else: ## does not wrap around
            intersects = self.checkIntersect([oldx, oldy], [self.xpos, self.ypos], defenderLoc[0], defenderLoc[1])

            if len(defenderLoc) > 2:
                intersects = intersects or self.checkIntersect([oldx, oldy], [self.xpos, self.ypos], defenderLoc[2], defenderLoc[3])
           


        ## now check if I have passed through the defender, and which case I must not move
        if intersects == True:
            self.xpos = oldx
            self.ypos = oldy
            return -30, False ## blocked
        

        ## and check to see if I have passed into the endzone and in which case return 1
        if self.ypos < self.endzone:
            return 10.0, True ## reached endzone
            

        return -1.0, False ## unblocked



    def rotate(self, x, y, theta):
        sinTheta = math.sin(theta)
        cosTheta = math.cos(theta)
        xp = cosTheta * x + -sinTheta * y
        yp = sinTheta * x + cosTheta * y
        return [xp, yp]


    ## Checks if two line segments intersect. Line segments are given in form of ({x,y},{x,y}, {x,y},{x,y}).
    ## taken from https://love2d.org/wiki/General_math
    def checkIntersect(self, l1p1, l1p2, l2p1, l2p2):
        checkDir = lambda pt1, pt2, pt3:  math.sign(((pt2[0]-pt1[0])*(pt3[1]-pt1[1])) - ((pt3[0]-pt1[0])*(pt2[1]-pt1[1])))
        return (checkDir(l1p1,l1p2,l2p1) != checkDir(l1p1,l1p2,l2p2)) and (checkDir(l2p1,l2p2,l1p1) != checkDir(l2p1,l2p2,l1p2))
        


    def getX(self):
        return self.xpos

    def getY(self):
        return self.ypos




class Defender():
    def __init__(self, maxFieldSize, attackers, field, ypos, defenderLength):
        self.attackers = attackers
        self.field = field
        self.ypos = ypos
        self.xpos = maxFieldSize / 2.5
        self.defenderLength = defenderLength
        self.maxFieldSize = maxFieldSize

    def reset(self, ypos):
        self.ypos = ypos
        self.xpos = self.maxFieldSize / 2.5

    def step(self):
        ##find the agent closest to the defender and move in the x direction toward it one unit

        sign = 1
        minDist = self.maxFieldSize + 1
        for l in self.attackers:
            if l.getY() - self.ypos < minDist:
                vx = self.field.tdx(l.getX(), self.xpos) ## get the dist in the x direction (while wrapping around)
                if vx != 0.0:
                    sign = vx / abs(vx)
                else:
                    sign = 0.0
                
        
        self.xpos = self.field.stx(self.xpos + sign)

    ## returns a set of four points so defined so that the first two points correspond
    ## to the beginning and end of the first segment and the next two points correspond
    ## to the second segment that wraps around to the other side of the field.
    ## so if not on the other side of the field.
    def getDefenderPoints(self):

        endX = self.field.stx(self.xpos + self.defenderLength)

        if endX < self.xpos:
        ## then I have wrapped around and need to return 4 points
            return [[self.xpos, self.ypos], [self.maxFieldSize, self.ypos],[0, self.ypos], [endX, self.ypos]]
        
        ## otherwise I am just a regular two point line segment
        return [[self.xpos, self.ypos], [endX, self.ypos]]
        
    def getX(self):
        return self.xpos

    def getY(self):
        return self.ypos




class FootballEnv(gym.Env):
    def __init__(self, numAttackers, size, offset, defenderStart, defenderLength):
        self.size = size
        self.offset = offset or 0.0
        self.defenderStart = defenderStart or 5
        self.field = field.ContinuousField(size, size)
        self.defenderLength = defenderLength
        self.numAttackers = numAttackers
        self.winner = -1
        self.attackers = []
        for i in range(1, numAttackers + 1):
          self.attackers.append(Attacker(self.size, self.field, self.size / i, self.size - self.offset))
        
        self.terminal = False

        self.defender = Defender(self.size, self.attackers, self.field, self.defenderStart, self.defenderLength)

        self.action_space = spaces.Box(0,2*math.pi, self.numAttackers) ## the direction the attacker will face
        self.observation_space = spaces.Box(np.array([0,0]),np.array([self.size, self.size]))

        self._seed()
        self.reset()
        self.viewer = None

        self.steps_beyond_done = None


    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _reset(self):
        for i in range(1, self.numAttackers + 1):
            self.attackers[i-1].reset(self.size / i, self.size - self.offset)
        
        self.defender.reset(self.defenderStart)

        coords = []
        for i in range(0, len(self.attackers)):
            coords.append([self.attackers[i].getX(), self.attackers[i].getY()])
        
        coords.append([self.defender.getX(), self.defender.getY()])

        self.terminal = False

        return coords
    


    def _step(self, action):
        self.defender.step()

        t = False
        r = 0.0
     
        i = 0
        for a in self.attackers:
            reward, terminate = a.step(action[i], self.defender)
            if reward < r:
                r = reward
            
            t = t or terminate ## terminated if one of the attackers reached endzone
            if t == True:
                r = reward
                self.winner = i
                break
            i = i + 1
        
        ## now make the input values
        coords = []
        for i in range(0, len(self.attackers)):
            coords.append([self.attackers[i].getX(), self.attackers[i].getY()])

        coords.append([self.defender.getX(), self.defender.getY()])

        self.terminal = t

        return coords, r, self.terminal, {}
    


    def getAttackers(self):
        return self.attackers
    

    def getDefender(self):
        return self.defender
    

    def getIsTerminal(self):
        return self.terminal
    

    def getDefenderPoints(self):
        return self.defender.getDefenderPoints()
    

    def getWinner(self):
        return self.winner
    