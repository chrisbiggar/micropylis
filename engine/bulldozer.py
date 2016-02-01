'''
Created on Oct 24, 2015

@author: chris
'''
import micropolistool
from toolStroke import ToolStroke


class Bulldozer(ToolStroke):
    def __init__(self, engine, xPos, yPos):
        super(Bulldozer, self).__init__(engine,
                                        micropolistool.types['BULLDOZER'],
                                        xPos, yPos)

    def applyArea(self, eff):
        pass
