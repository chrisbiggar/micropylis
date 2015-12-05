'''
Created on Oct 20, 2015

@author: chris
'''
from bulldozer import Bulldozer
from engine.roadLikeTool import RoadLikeTool
from engine.BuildingTool import BuildingTool
from engine.toolStroke import ToolStroke

# Tool types:
BULLDOZER,WIRE,ROADS,RAIL,RESIDENTIAL,COMMERCIAL,INDUSTRIAL,FIRE\
,POLICE,STADIUM,PARK,SEAPORT,POWERPLANT,NUCLEAR,AIRPORT,QUERY = range(16)

class MicropylisTool(object):
    def __init__(self, name, type_, size, cost):
        self.name = name
        self.type = type_
        self.size = size
        self.cost = cost
    
    @classmethod
    def factory(cls, toolType):
        toolType = toolType.upper()
        try:
            class_ = types[toolType]
        except KeyError:
            print "toolType not found: " + toolType
            return None
        return class_
        
    def getWidth(self):
        return self.size
    
    def getHeight(self):
        return self.getWidth()
    
    def beginStroke(self, engine, xPos, yPos):
        if self.type == BULLDOZER:
            return Bulldozer(engine, xPos, yPos)
        elif self.type == WIRE or\
                self.type == ROADS or\
                self.type == RAIL:
            return RoadLikeTool(engine, self, xPos, yPos)
        elif self.type == FIRE or\
                self.type == FIRE or\
                self.type == FIRE or\
                self.type == FIRE or\
                self.type == FIRE or\
                self.type == FIRE or\
                self.type == FIRE:
            return BuildingTool(engine, self, xPos, yPos)
        else:
            return ToolStroke(engine, self, xPos, yPos)
            
    
    def apply(self, engine, xPos, yPos):
        return self.beginStroke(engine, xPos, yPos).apply()
    
    def getToolCost(self):
        return self.cost



types = dict()
types['BULLDOZER'] = MicropylisTool('BULLDOZER', BULLDOZER, 1, 10)
types['WIRE'] = MicropylisTool('WIRE', WIRE, 1, 5) # 25 underwater
types['ROADS'] = MicropylisTool('ROADS', ROADS, 1, 10) # 50 overwater
types['RAIL'] = MicropylisTool('RAIL', RAIL, 1, 20) # 100 underwater
types['RESIDENTIAL'] = MicropylisTool('RESIDENTIAL', RESIDENTIAL, 3, 100)
types['COMMERCIAL'] = MicropylisTool('COMMERCIAL', COMMERCIAL, 3, 100)
types['INDUSTRIAL'] = MicropylisTool('INDUSTRIAL', INDUSTRIAL, 3, 100)
types['POLICE'] = MicropylisTool('POLICE', POLICE, 3, 500)
types['FIRE'] = MicropylisTool('FIRE', FIRE, 3, 500)
types['STADIUM'] = MicropylisTool('STADIUM', STADIUM, 3, 500)
types['PARK'] = MicropylisTool('PARK', PARK, 1, 500)
types['SEAPORT'] = MicropylisTool('SEAPORT', SEAPORT, 4, 3000)
types['POWERPLANT'] = MicropylisTool('POWERPLANT', POWERPLANT, 3, 3000)
types['NUCLEAR'] = MicropylisTool('NUCLEAR', NUCLEAR, 3, 5000)
types['AIRPORT'] = MicropylisTool('AIRPORT', AIRPORT, 3, 10000)
types['QUERY'] = MicropylisTool('QUERY', QUERY, 1, 0)