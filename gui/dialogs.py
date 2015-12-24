'''
Created on Sep 24, 2015

@author: chris
'''
import pyglet
import kytten
from kytten.widgets import Label
from kytten.layout import VerticalLayout
from kytten.frame import Frame
from kytten.dialog import Dialog
import widgets
import gui

theme = kytten.theme.Theme('res/kyttentheme', override={
"gui_color": [64, 128, 255, 255],
"font_size": 16
})


class NewCityDialog(Dialog):
    def __init__(self, mainWindow):
        self.tilesView = mainWindow
        self.selectedToolLabel = None
        frame = self.createLayout()
        super(NewCityDialog, self).__init__(frame,
                                    window=mainWindow,
                                    batch=mainWindow.dialogBatch,
                                    anchor=kytten.ANCHOR_CENTER, 
                                    theme=theme)        
        
    def createLayout(self):
        pass


class ToolDialog(Dialog):
    def __init__(self, mainWindow):
        self.tilesView = mainWindow
        self.selectedToolLabel = None
        self.iconsheetFilename = gui.config.get('tools','ICONSHEET_FILENAME')
        frame = self.createLayout()
        super(ToolDialog, self).__init__(frame,
                                    window=mainWindow,
                                    batch=mainWindow.dialogBatch,
                                    anchor=kytten.ANCHOR_TOP_LEFT, 
                                    theme=theme)
        firstToolId = self.toolSection.options.itervalues().next().id
        self.toolSection.select(firstToolId)
        self.width = 300
        
    def createLayout(self):
        iconSize =  int(gui.config.get('tools','TOOLICONSIZE'))
        iconSheet = pyglet.image.load(self.iconsheetFilename)
        rows = iconSheet.height / iconSize
        columns = iconSheet.width / iconSize
        iconSheet = pyglet.image.TextureGrid(
                        pyglet.image.ImageGrid(
                            iconSheet, rows, columns))
        
        toolSet = []
        i = 0
        with open("res/toolsorder") as tOFile:
            for line in tOFile:
                name = line.strip().lower().title()
                row = rows - 1 - (i / columns)
                column = i % columns
                toolSet.append((name, iconSheet[row, column]))
                i += 1

        # Create options from images to pass to Palette
        palette_options = [[]]
        for i in xrange(rows - 1):
            palette_options.append([])
        for i, pair in enumerate(toolSet):
            option = widgets.PaletteOption(name=pair[0], image=pair[1], padding=2)
            # Build column down, 3 rows
            palette_options[i%8].append(option)
        self.toolSection = widgets.PaletteMenu(palette_options, on_select=self.onToolSelect)
        
        self.selectedToolLabel = Label("")
        self.selectedToolPriceLabel = Label("")
        
        return Frame(VerticalLayout([
                            self.selectedToolLabel,
                            self.toolSection,
                            self.selectedToolPriceLabel]))
        
        
    def onToolSelect(self, toolId):
        tool = self.tilesView.selectTool(toolId.strip())
        if self.selectedToolLabel is not None:
            self.selectedToolLabel.set_text(toolId)
            # pan is only tool not in micropolistool types
            if toolId == "Pan" or\
                    tool.getToolCost() == 0:
                self.selectedToolPriceLabel.set_text("Free")
            else:
                self.selectedToolPriceLabel.set_text("$" + str(tool.getToolCost()))

            













