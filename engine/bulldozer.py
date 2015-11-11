'''
Created on Oct 24, 2015

@author: chris
'''
from toolStroke import ToolStroke
import micropolistool


class Bulldozer(ToolStroke):
    def __init__(self, engine, xPos, yPos):
        super(Bulldozer,self).__init__(engine,
                                       micropolistool.MicropylisTool.BULLDOZER,
                                       xPos, yPos)
        
    def applyArea(self, eff):
        pass
    
    