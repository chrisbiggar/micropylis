'''
Created on Oct 24, 2015

@author: chris
'''
from engine.toolStroke import ToolStroke



class BuildingTool(ToolStroke):
    
    
    def __init__(self, engine, tool, xPos, yPos):
        super(BuildingTool,self).__init__(engine, tool, xPos, yPos)
        