'''
Created on Sep 24, 2015

All kytten dialog classes are in this module.


@author: chris
'''
from __future__ import division

import os

import pyglet


import kytten
from kytten import FileLoadDialog, FileSaveDialog
from kytten.dialog import Dialog
from kytten.frame import Frame
from kytten.layout import VerticalLayout
from kytten.widgets import Label, Spacer
from pyglet.graphics import Batch

from . import widgets
import gui

from engine import gameLevel

def on_escape(dialog):
    '''
        tears down specified dialog
    '''
    dialog.teardown()


theme = kytten.theme.Theme('res/kyttentheme', override={
    "gui_color": [64, 128, 255, 255],
    "font_size": 16
})

'''
Window needs to set itself here so it can be alerted of change.
Window should call this batch's draw() during on_draw()
'''
window = None
batch = Batch()

'''
SingularDialog

Allows a subclassing dialog to be toggled.
Does not allow multiple instances if you only use the toggle class method
'''


class SingularDialog(Dialog):
    current = None

    def onCreation(self, cls):
        cls.current = self

    def onDestruction(self, cls):
        cls.current = None

    @classmethod
    def toggle(cls):
        print cls.current
        if cls.current is None:
            cls()
        else:
            cls.current.teardown()


'''class ExitConfirmDialog(SingularDialog):
    def __init__(self):
        text = "Are You Sure You Want To Quit?"
        
        def on_ok_click(dialog=None):
            if on_ok is not None:
                on_ok(self)
            self.teardown()

        def on_cancel_click(dialog=None):
            if on_cancel is not None:
                on_cancel(self)
            self.teardown()

        return Dialog.__init__(self, content=Frame(
            VerticalLayout([
                Label(text),
                HorizontalLayout([
                    Button(ok, on_click=on_ok_click),
                    None,
                    Button(cancel, on_click=on_cancel_click)
                ]),
            ])),
            window=window, batch=batch, group=group,
            theme=theme, movable=True,
            on_enter=on_ok_click, on_escape=on_cancel_click)'''

'''
MainDialog

New, save, load, options, etc...
nothing interesting here.
'''


class MainMenuDialog(SingularDialog):
    def __init__(self):
        self.onCreation(self.__class__)
        frame = self.createLayout()
        super(MainMenuDialog, self).__init__(frame,
                                             window=window,
                                             batch=batch,
                                             anchor=kytten.ANCHOR_CENTER,
                                             theme=theme,
                                             on_escape=on_escape)

    def createLayout(self):
        title = Label(text="Micropylis")
        if window.cityLoaded():
            options = ["Back", "New City", "Load City",
                       "Save City", "Options", "Credits", "Quit"]
        else:
            options = ["New City", "Load City",
                       "Options", "Credits", "Quit"]
        self.menu = widgets.ClickMenu(
            options, on_select=self.on_select_menu,
            option_padding_x=76, option_padding_y=16)

        return Frame(VerticalLayout([title, Spacer(height=2), self.menu]))

    def on_select_menu(self, choice):
        def on_load_select(filePath):
            window.loadCity(filePath)
            loadDialog.teardown()
            self.teardown()

        def on_save_select(filePath):
            # window.saveCity(filePath)
            print("save city as " + filePath)
            saveDialog.tearDown()
            self.teardown()

        if choice == "Back":
            self.on_cancel()
        elif choice == "New City":
            window.newCity(gameLevel.MIN_LEVEL)
            self.teardown()
        elif choice == "Load City":
            loadDialog = FileLoadDialog(
                os.getcwd() + '\cities',
                extensions=['.cty'],
                window=window,
                on_select=on_load_select,
                batch=batch,
                theme=theme,
                on_escape=on_escape)
        elif choice == "Save City":
            saveDialog = FileSaveDialog(
                os.getcwd() + '\cities',
                extensions=['.cty'],
                window=window,
                on_select=on_save_select,
                batch=batch,
                theme=theme,
                on_escape=on_escape)
        elif choice == "Quit":
            window.on_close()

    def on_cancel(self):
        on_escape(self)

    def teardown(self):
        Dialog.teardown(self)
        self.onDestruction(self.__class__)


'''
CityEvalDialog

Shows statistics about current city.
'''


class CityEvalDialog(SingularDialog):
    def __init__(self):
        self.onCreation(self.__class__)
        self.window = window
        frame = self.createLayout()
        super(CityEvalDialog, self).__init__(frame,
                                             window=window,
                                             batch=batch,
                                             anchor=kytten.ANCHOR_CENTER,
                                             theme=theme,
                                             on_escape=on_escape)

    def createLayout(self):
        title = Label(text="City Evaluation")
        self.menu = widgets.ClickMenu(
            options=["Stuff here"],
            on_select=self.on_select_menu)

        return Frame(VerticalLayout([title, Spacer(height=2), self.menu]))

    def on_select_menu(self, choice):
        if choice == "Back To City":
            self.on_cancel()

    def on_cancel(self):
        on_escape(self)

    def teardown(self):
        Dialog.teardown(self)
        self.onDestruction(self.__class__)

'''
BudgetDialog

Shows the city current yearly cash situation.
Allows the tax and funding rates to be modified.
'''


class BudgetDialog(SingularDialog):
    def __init__(self):
        self.onCreation(self.__class__)
        self.window = window
        frame = self.createLayout()
        super(BudgetDialog, self).__init__(frame,
                                           window=window,
                                           batch=batch,
                                           anchor=kytten.ANCHOR_CENTER,
                                           theme=theme,
                                           on_escape=on_escape)

    def createLayout(self):
        title = Label(text="City Budget")
        self.menu = widgets.ClickMenu(
            options=["Stuff here"],
            on_select=self.on_select_menu)

        return Frame(VerticalLayout([title, Spacer(height=2), self.menu]))

    def on_select_menu(self, choice):
        if choice == "Back To City":
            self.on_cancel()

    def on_cancel(self):
        on_escape(self)

    def teardown(self):
        Dialog.teardown(self)
        self.onDestruction(self.__class__)

'''
NewCityDialog

User can set size and difficulty level and ask for
a new map to be generated before starting.
'''


class NewCityDialog(Dialog):
    def __init__(self, mainWindow):
        self.window = mainWindow
        self.selectedToolLabel = None
        frame = self.createLayout()
        super(NewCityDialog, self).__init__(frame,
                                            window=window,
                                            batch=batch,
                                            anchor=kytten.ANCHOR_CENTER,
                                            theme=theme)

    def createLayout(self):
        pass


class LoadCityDialog(Dialog):
    def __init__(self, mainWindow):
        self.window = mainWindow
        self.selectedToolLabel = None
        frame = self.createLayout()
        super(NewCityDialog, self).__init__(frame,
                                            window=mainWindow,
                                            batch=batch,
                                            anchor=kytten.ANCHOR_CENTER,
                                            theme=theme)

    def createLayout(self):
        pass


class SaveCityDialog(Dialog):
    def __init__(self, mainWindow):
        self.window = mainWindow
        self.selectedToolLabel = None
        frame = self.createLayout()
        super(NewCityDialog, self).__init__(frame,
                                            window=mainWindow,
                                            batch=batch,
                                            anchor=kytten.ANCHOR_CENTER,
                                            theme=theme)

    def createLayout(self):
        pass


'''
ToolDialog

Tool selection dialog. Shows a palette of tools.
Name and cost of selected tool is displayed as well.
'''


class ToolDialog(Dialog):
    def __init__(self, mainWindow):
        self.tilesView = mainWindow
        self.selectedToolLabel = None
        self.iconsheetFilename = gui.config.get('tools', 'ICONSHEET_FILENAME')
        frame = self.createLayout()
        super(ToolDialog, self).__init__(frame,
                                         window=mainWindow,
                                         batch=batch,
                                         anchor=kytten.ANCHOR_TOP_LEFT,
                                         theme=theme)
        firstToolId = 'Pan'
        self.toolSection.select(firstToolId)
        self.width = 300

    def createLayout(self):
        iconSize = int(gui.config.get('tools', 'TOOLICONSIZE'))
        iconSheet = pyglet.image.load(self.iconsheetFilename)
        rows = iconSheet.height // iconSize
        columns = iconSheet.width // iconSize
        iconSheet = pyglet.image.TextureGrid(
            pyglet.image.ImageGrid(
                iconSheet, rows, columns))

        toolSet = []
        i = 0
        with open("res/toolsorder") as tOFile:
            for line in tOFile:
                name = line.strip().lower().title()
                row = rows - 1 - (i // columns)
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
            palette_options[i % 8].append(option)
        self.toolSection = widgets.PaletteMenu(palette_options, on_select=self.onToolSelect)

        self.selectedToolLabel = Label("")
        self.selectedToolPriceLabel = Label("")

        return Frame(VerticalLayout([
            self.selectedToolLabel,
            self.selectedToolPriceLabel,
            self.toolSection,
            Spacer(height=4)
        ]))

    def onToolSelect(self, toolId):
        tool = self.tilesView.selectTool(toolId.strip())
        if self.selectedToolLabel is not None:
            self.selectedToolLabel.set_text(toolId)
            # pan is only tool not in micropolistool types
            if toolId == "Pan" or \
                            tool.getToolCost() == 0:
                self.selectedToolPriceLabel.set_text("Free")
            else:
                self.selectedToolPriceLabel.set_text("$" + str(tool.getToolCost()))
