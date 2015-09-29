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

theme = kytten.Theme(os.path.join(os.getcwd(), 'theme'), override={
"gui_color": [64, 128, 255, 255],
"font_size": 16
})

class MainDialog(Dialog):
    
    def __init__(self, mainWindow):
        frame = self.createLayout()
        super(MainDialog, self).__init__(frame,
                                    window=mainWindow,
                                    batch=mainWindow.dialogBatch,
                                    anchor=kytten.ANCHOR_TOP_RIGHT, 
                                    theme=theme)
        
    def createLayout(self):
        label = Label("TEST")
        return Frame(VerticalLayout([label]))
