'''
Created on Nov 5, 2015

@author: chris
'''



import math
from PIL import Image



class MakeToolIcons(object):
    STD_SIZE = 16
    def __init__(self, iconWidth, iconHeight, gridWidth):
        self.iconWidth = iconWidth
        self.iconHeight = iconHeight
        self.gridWidth = gridWidth
        self.basePath = "build/graphics/tools/"
        self.destImg = None
    
    
    def generateToolGrid(self, specFilename, outputName):
        specFile = open(self.basePath + specFilename)
        toolOrder = []
        for line in specFile:
            toolOrder.append(line.strip())
        
        numTools = len(toolOrder) 
        iconWidth = self.iconWidth
        columns = self.gridWidth
        rows = numTools / self.gridWidth
        if numTools % 2 == 1:
            rows += 1
        self.destImg = Image.new("RGB", 
                                 (columns*iconWidth, rows*self.iconHeight))
        
        i = 0
        for tool in toolOrder:
            try:
                path = self.basePath + tool + ".png"
                toolIcon = Image.open(path)
            except IOError:
                raise IOError("ioerror:" +  path + "not found.")
            destX = (i % self.gridWidth) * iconWidth
            destY = int(i / self.gridWidth) * self.iconHeight
            self.drawTo(toolIcon, destX, destY)
            i += 1
        
        self.destImg.save(outputName + ".png")
        print "Tool Icon Sheet Created at: " + outputName + ".png"
    
    def drawTo(self, icon, destX, destY):
        box = (destX, destY, 
                destX + self.iconWidth, destY + self.iconHeight)
        self.destImg.paste(icon, box)
        


if __name__ == '__main__':
    outputName = "res/toolicons"
    mkT = MakeToolIcons(38, 38, 2)
    mkT.generateToolGrid("toolsorder", outputName)
    
    
    
    
    
    
    
    
    