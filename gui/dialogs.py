'''
Created on Sep 24, 2015

@author: chris
'''
import os
import pyglet
import kytten
from kytten.widgets import Label
from kytten.layout import VerticalLayout
from kytten.frame import Frame
from kytten.dialog import Dialog
import widgets
import gui
from engine import micropolistool
from engine.micropolistool import MicropylisTool

theme = kytten.theme.Theme('res/kyttentheme', override={
"gui_color": [64, 128, 255, 255],
"font_size": 16
})

class ToolDialog(Dialog):
    def __init__(self, mainWindow):
        self.window = mainWindow
        self.selectedToolLabel = None
        frame = self.createLayout()
        super(ToolDialog, self).__init__(frame,
                                    window=mainWindow,
                                    batch=mainWindow.dialogBatch,
                                    anchor=kytten.ANCHOR_TOP_LEFT, 
                                    theme=theme)
        firstToolId = self.toolSection.options.itervalues().next().id
        self.toolSection.select(firstToolId)
        
    def createLayout(self):
        toolSet = []
        for name in micropolistool.types:
            iconPath = 'res/' + gui.config.get('tools', name + '.icon')
            name = name.lower().title()
            toolSet.append((name, pyglet.image.load(iconPath)))
        
        toolSet.append(('Pan', pyglet.image.load(
                                'res/icpan.png')))
        
        # Create options from images to pass to Palette
        palette_options = [[]]
        palette_options.append([])
        palette_options.append([])
        for i, pair in enumerate(toolSet):
            option = widgets.PaletteOption(name=pair[0], image=pair[1], padding=4)
            # Build column down, 3 rows
            palette_options[i%2].append(option)
        self.toolSection = widgets.PaletteMenu(palette_options, on_select=self.onToolSelect)
        
        self.selectedToolLabel = Label("")
        self.selectedToolPriceLabel = Label("")
        
        return Frame(VerticalLayout([
                            self.selectedToolLabel,
                            self.toolSection,
                            self.selectedToolPriceLabel]))
        
        
    def onToolSelect(self, toolId):
        self.window.selectTool(toolId)
        if self.selectedToolLabel is not None:
            self.selectedToolLabel.set_text(toolId)
            # pan is only tool not in micropolistool types
            if toolId == "Pan" or\
                    MicropylisTool.factory(toolId).getToolCost() == 0:
                self.selectedToolPriceLabel.set_text("Free")
            else:
                self.selectedToolPriceLabel.set_text(str(
                    MicropylisTool.factory(toolId).getToolCost()))
            













