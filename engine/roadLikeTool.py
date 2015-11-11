'''
Created on Oct 24, 2015

@author: chris
'''
import micropolistool
from toolStroke import ToolStroke
from engine.cityRect import CityRect
from engine.translatedToolEffect import TranslatedToolEffect
from tileConstants import *
from engine.toolResult import ToolResult


class RoadLikeTool(ToolStroke):

    def __init__(self, engine, tool, xPos, yPos):
        super(RoadLikeTool,self).__init__(engine, tool, xPos, yPos)
        
    '''
        overrides ToolStroke
    '''
    def applyArea(self, eff):
        while True:
            if self.applyForward(eff) == False:
                break
            #if self.applyBackward(eff) == False:
            #    break
            
            
    def applyForward(self, eff):
        anyChange = False
        
        b = self.getBounds()
        for y in range(b.height):
            for x in range(b.width):
                tte = TranslatedToolEffect(eff, b.x+x, b.y+y)
                anyChange = anyChange or self.applySingle(tte)
        return anyChange
    
            
    def applyBackward(self, eff):
        anyChange = False
        
        b = self.getBounds()
        for y in range(b.height-1, 0, -1):
            for x in range(b.width-1, 0, -1):
                tte = TranslatedToolEffect(eff, b.x+x, b.y+y)
                anyChange = anyChange or self.applySingle(tte)
        
        return anyChange
        
        
    def getBounds(self):
        ''' constrain bounds to be rectangle with
            either width of height equal to one '''
        
        assert self.tool.getWidth() == 1
        assert self.tool.getHeight() == 1
        
        xDest = self.xDest
        xPos = self.xPos
        yDest = self.yDest
        yPos = self.yPos
        
        if abs(xDest - xPos) >= abs(yDest-yPos):
            # horizontal line
            r = CityRect()
            r.x = min(xPos, xDest)
            r.width = abs(xDest - xPos) + 1
            r.y = yPos
            r.height = 1
            return r
        else:
            # vertical line
            r = CityRect()
            r.x = xPos
            r.width = 1
            r.y = min(yPos, yDest)
            r.height = abs(yDest - yPos) + 1
            return r
    
    def applySingle(self, eff):
        if self.tool.type == micropolistool.ROADS:
            return self.applyRoadTool(eff)
        elif self.tool.type == micropolistool.RAIL:
            return self.applyRailTool(eff)
        else:
            raise Exception("Unexpected Tool: " + self.tool.name)
        
    def applyRailTool(self, eff):
        if self.layRail(eff):
            self.fixZone(eff)
            return True
        else:
            return False
    
    def applyRoadTool(self, eff):
        
        if self.layRoad(eff):
            self.fixZone(eff)
            return True
        else:
            return False
        
    def layRail(self, eff):
        RAILCOST = 20
        TUNNELCOST = 100
        
        cost = RAILCOST
        
        tile = eff.getTile(0,0)
        tile = neutralizeRoad(tile)
        
        if (tile == RIVER 
                or tile == REDGE
                or tile == CHANNEL):
            cost = TUNNELCOST
            
            hit = False
            eastT = neutralizeRoad(eff.getTile(1, 0))
            if (eastT == RAILHPOWERV or\
                    eastT == HRAIL or\
                    (eastT >= LHRAIL and\
                     eastT <= HRAILROAD)):
                eff.setTile(0,0, HRAIL)
                hit = True
            if not hit:
                westT = neutralizeRoad(eff.getTile(-1, 0))
                if (westT == RAILHPOWERV or\
                        westT == HRAIL or\
                        (westT > VRAIL and\
                         westT < VRAILROAD)):
                    eff.setTile(0,0, HRAIL)
                    hit = True
            if not hit:
                southT = neutralizeRoad(eff.getTile(0, 1))
                if (southT == RAILVPOWERH or\
                        southT == VRAILROAD or\
                        (southT > HRAIL and\
                         southT < HRAILROAD)):
                    eff.setTile(0,0, VRAIL)
                    hit = True
            if not hit:
                northTile = neutralizeRoad(eff.getTile(0, -1))
                if (northTile == RAILVPOWERH or\
                        northTile == VRAILROAD or\
                        (northTile > HRAIL and\
                         northTile < HRAILROAD)):
                    eff.setTile(0,0, VRAIL)
                    hit = True
            
            if not hit:
                return False
        
        elif tile == LHPOWER:
            eff.setTile(0, 0, RAILVPOWERH)
        
        elif tile == LVPOWER:
            eff.setTile(0, 0, RAILHPOWERV)
            
        elif tile == ROADS:
            eff.setTile(0, 0, VRAILROAD)
            
        elif tile == ROADS2:
            eff.setTile(0, 0, HRAILROAD)
        
        else:
            if tile != DIRT:
                if canAutoBulldozeRRW(tile):
                    cost += 1
                else:
                    return False
            
            eff.setTile(0, 0, LHRAIL)
        
        eff.spend(cost)
        return True
        
    
    def layRoad(self, eff):
        ROADCOST = 10
        BRIDGECOST = 50
        
        cost = ROADCOST
        
        tile = eff.getTile(0,0)
        if tile == RIVER or\
                tile == REDGE or\
                tile == CHANNEL:
            cost = BRIDGECOST
            
            hit = False
            eTile = neutralizeRoad(eff.getTile(1, 0))
            if (eTile == VRAILROAD or\
                    eTile == HBRIDGE or\
                    (eTile >= ROADS and\
                     eTile <= HROADPOWER)):
                eff.setTile(0,0, HBRIDGE)
                hit = True
            if not hit:
                wTile = neutralizeRoad(eff.getTile(-1, 0))
                if (wTile == VRAILROAD or\
                        wTile == HBRIDGE or\
                        (wTile >= ROADS and\
                         wTile <= INTERSECTION)):
                    eff.setTile(0,0, HBRIDGE)
                    hit = True
            if not hit:
                sTile = neutralizeRoad(eff.getTile(0, 1))
                if (sTile == HRAILROAD or\
                        sTile == VROADPOWER or\
                        (sTile >= VBRIDGE and\
                         sTile <= INTERSECTION)):
                    eff.setTile(0,0, VBRIDGE)
                    hit = True
            if not hit:
                nTile = neutralizeRoad(eff.getTile(0, -1))
                if (nTile == HRAILROAD or\
                        nTile == VROADPOWER or\
                        (nTile >= VBRIDGE and\
                         nTile <= INTERSECTION)):
                    eff.setTile(0,0, VBRIDGE)
                    hit = True
            
            if not hit:
                return False
        
        elif tile == LHPOWER:
            eff.setTile(0, 0, VROADPOWER)
        elif tile == LVPOWER:
            eff.setTile(0, 0, HROADPOWER)
        elif tile == LHRAIL:
            eff.setTile(0, 0, HRAILROAD)
        elif tile == LVRAIL:
            eff.setTile(0, 0, VRAILROAD)
        else:
            if tile != DIRT:
                if canAutoBulldozeRRW(tile):
                    cost += 1
                else:
                    return False
            
            eff.setTile(0, 0, ROADS)
        
        eff.spend(cost)
        return True
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        