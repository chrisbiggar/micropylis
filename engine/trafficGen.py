from random import randint

from .cityLocation import CityLocation
from .tileConstants import (ROADBASE,LASTRAIL,POWERBASE,LASTPOWER,
                           COMBASE,NUCLEAR,LHTHR,PORT)


class ZoneType(object):
    RESIDENTIAL = 0
    COMMERCIAL = 1
    INDUSTRIAL = 2

'''
    Contains the code for generating city traffic.
'''


class TrafficGen(object):
    MAXTRAFFICDISTANCE = 30

    def __init__(self, city):
        self.city = city
        self.mapX = 0
        self.mapY = 0
        self.sourceZone = None
        self.lastDir = None
        self.positions = list() # stack

        self.perimX = [-1,0,1, 2,2,2, 1,0,-1, -2, 2,-2]
        self.perimY = [-2,-2,-2, -1,0,1, 2,2,2, 1,0,-1]

        self.dx = [0,1,0,-1]
        self.dy = [-1,0,1,0]

    def makeTraffic(self):
        if self.findParameterRoad():
            if self.tryDrive():
                self.setTrafficMem()
                return 1
            return 0
        else:
            return -1

    def setTrafficMem(self):

        while len(self.positions) > 0:
            pos = self.positions.pop()
            self.mapX = pos.x
            self.mapY = pos.y
            assert self.city.testBounds(self.mapX, self.mapY)
            #print "set traffic"
            tile = self.city.getTile(self.mapX, self.mapY)
            if ROADBASE <= tile < POWERBASE:
                #print "add traffic"
                self.city.addTraffic(self.mapX, self.mapY, 50)

    def findParameterRoad(self):
        for z in xrange(0, 12):
            tx = self.mapX + self.perimX[z]
            ty = self.mapY + self.perimY[z]

            if self.roadTest(tx, ty):
                self.mapX = tx
                self.mapY = ty
                return True

        return False

    def roadTest(self, tx, ty):
        if not self.city.testBounds(tx, ty):
            return False

        c = self.city.getTile(tx, ty)

        if c < ROADBASE:
            return False
        elif c > LASTRAIL:
            return False
        elif POWERBASE <= c < LASTPOWER:
            return False
        else:
            return True




    def tryDrive(self):
        self.lastDir = 5
        self.positions = []

        for z in xrange(0, self.MAXTRAFFICDISTANCE):
            if self.tryGo(z):
                if self.driveDone():
                    return True
            else:
                if len(self.positions):
                    self.positions.pop()
                    z += 3
                else:
                    return False

        return False



    def tryGo(self, z):
        rDir = randint(0, 3)

        for d in xrange(rDir, rDir + 4):
            realDir = d % 4
            if realDir == self.lastDir:
                continue

            if self.roadTest(self.mapX + self.dx[realDir],
                             self.mapY + self.dy[realDir]):
                self.mapX += self.dx[realDir]
                self.mapY += self.dy[realDir]
                self.lastDir = (realDir + 2) % 4

                if z % 2 == 1:
                    self.positions.append(CityLocation(self.mapX, self.mapY))

                return True
        return False



    def driveDone(self):
        low = 0
        high = 0
        if self.sourceZone == ZoneType.RESIDENTIAL:
            low = COMBASE
            high = NUCLEAR
        elif self.sourceZone == ZoneType.COMMERCIAL:
            low = LHTHR
            high = PORT
        elif self.sourceZone == ZoneType.INDUSTRIAL:
            low = LHTHR
            high = COMBASE
        else:
            print("unreachable")

        if self.mapY > 0:
            tile = self.city.getTile(self.mapX, self.mapY - 1)
            if low <= tile <= high:
                return True
        if self.mapX + 1 < self.city.getWidth():
            tile = self.city.getTile(self.mapX + 1, self.mapY)
            if low <= tile <= high:
                return True
        if self.mapY + 1 < self.city.getHeight():
            tile = self.city.getTile(self.mapX, self.mapY + 1)
            if low <= tile <= high:
                return True
        if self.mapX > 0:
            tile = self.city.getTile(self.mapX - 1, self.mapY)
            if low <= tile <= high:
                return True

        return False














