'''
Created on Oct 29, 2015

@author: chris
'''
import pyglet
from pyglet.text import Label
from pyglet.text.layout import TextLayout
from pyglet.text.document import FormattedDocument
from pyglet.gl import *
import gui
from gui import GUI_BG_RENDER_ORDER, GUI_FG_RENDER_ORDER
from layout import Widget,Frame,VerticalLayout,\
                            HALIGN_RIGHT, Spacer, ButtonLabel
from util import createRect, createHollowRect
from util.profile import timefunc
from gui.layout import LayoutLabel
from dialogs import CityEvalDialog, BudgetDialog
from gui.dialogs import MainMenuDialog

bgGroup = pyglet.graphics.OrderedGroup(GUI_BG_RENDER_ORDER)
mgGroup = pyglet.graphics.OrderedGroup(GUI_BG_RENDER_ORDER + 1)
fgGroup = pyglet.graphics.OrderedGroup(GUI_FG_RENDER_ORDER)
highlightGroup = pyglet.graphics.OrderedGroup(GUI_FG_RENDER_ORDER+1)


fontName = gui.config.get('control_panel', 'FONT')
fontSize = 16



class Message(object):
    SHOW_TIME = 8 # in seconds
    def __init__(self, msg, startTime, start=0, num=0):
        self.string = msg
        self.time = int(startTime)
        self.index = start
        self.num = num
    
    def isExpired(self, secs):
        return int(secs) > self.time + self.SHOW_TIME * 2
    
    def __len__(self):
        return len(self.string)
    

'''
    displays messages to user. 
'''
class MessageQueue(Widget):
    MSG_DELETE_FREQ = 0.5 # in seconds
    def __init__(self, padding=0):
        super(MessageQueue,self).__init__()
        
        self.font = gui.config.get('control_panel', 'MSG_QUEUE_FONT')
        self.titleLabelText = gui.config.get('control_panel_strings', 'MSG_QUEUE_TITLE')
        
        bgColorStr = gui.config.get('control_panel', 'MSG_QUEUE_BG_COLOR')
        self.bgColor = map(int, tuple(bgColorStr.split(',')))
        
        self.titleLabel = None
        self.textLayout = None
        self.msgs = list()
        self.dt = 0
        self.halfSecs = 0
        self.bgRect = None
        self.border = None
        self.doc = FormattedDocument()
        self.padding = padding

        self.currentPos = 0
        self.numMsgs = 0
        
        self.engine = None
    
    def delete(self):
        if self.textLayout is not None:
            self.textLayout.delete()
        if self.titleLabel is not None:
            self.titleLabel.delete()
            self.title = None
        if self.bgRect is not None:
            self.bgRect.delete()
            self.bgRect = None
        if self.border is not None:
            self.border.delete()
            self.border = None
    
    def size(self, frame):
        super(MessageQueue,self).size(frame)
        
        
        if self.textLayout is not None:
            self.textLayout.delete()
        if self.titleLabel is not None:
            self.titleLabel.delete()
            self.titleLabel = None
        
        self.width = frame.width or 200
        self.height = 200
        
        if self.textLayout is None:
            self.textLayout = TextLayout(self.doc,
                                         width=self.width,
                                         batch=self.savedFrame.batch,
                                         group=fgGroup,
                                         multiline=True)
            self.savedFrame.setNeedsLayout()
        else:
            self.textLayout.width = self.width
        
        if self.titleLabel is None:
            self.titleLabel = Label(self.titleLabelText,
                                    x=self.x+10,y=self.y+10,
                                    batch=self.savedFrame.batch,
                                    group=fgGroup,
                                    color=(0,0,0,255),
                                    font_name=self.font,
                                    font_size=14)
        else:
            self.titleLabel.x = self.x + 10
            self.titleLabel.y = self.y + 10
        
    
    def layout(self, x, y):
        super(MessageQueue,self).layout(x,y)
        self.textLayout.x = self.x + self.padding
        self.textLayout.y = self.y - self.padding
        self.textLayout.width = self.width
        self.textLayout.height = self.height
        self.titleLabel.x = self.x + 10
        self.titleLabel.y = self.y + 10
        
        self.createBackground()
        
    def createBackground(self):
        if self.bgRect is not None:
            self.bgRect.delete()
            self.bgRect = None
        if self.border is not None:
            self.border.delete()
            self.border = None
        
        self.bgRect = createRect(self.x, self.y,
                             self.width, self.height,
                             self.bgColor,
                             self.savedFrame.batch,
                             mgGroup)
        
        self.border = createRect(self.x, self.y + self.height,
                             self.width, 1,
                             (0,0,0,255),
                             self.savedFrame.batch,
                             highlightGroup)
        
        
    def deleteMsg(self, item):
        self.msgs.remove(item)
        self.doc.delete_text(item.index, item.index + len(item))
        for msg in self.msgs:
            if msg.num > item.num:
                msg.num -= 1
                msg.index -= len(item)
        
    def addMessage(self, message):
        if len(self.msgs) and message == self.msgs[0].string:
            return
        
        message = message + '\n'
        item = Message(message, self.halfSecs)
        
        
        self.doc.set_style(0, len(self.doc.text), {'font_name' : self.font,
                                                   'bold' : False})
        for msg in self.msgs:
            msg.num += 1
            msg.index += len(item)
        
        self.msgs.insert(0,item)
        self.doc.insert_text(0, message, {'font_name' : self.font,
                                                   'bold' : True})
        
        if self.textLayout is not None:
            while (self.textLayout.content_height >= self.height 
                   - self.titleLabel.content_height + 14):
                item = self.msgs[len(self.msgs)-1]
                self.deleteMsg(item)
        
    def update(self, dt):
        self.dt += dt
        if self.dt >= self.MSG_DELETE_FREQ:
            # expired messages are collected on 0.5 sec freq
            self.halfSecs += 1
            self.dt = self.dt % self.MSG_DELETE_FREQ
            toRemove = []
            for item in self.msgs:
                if item.isExpired(self.halfSecs):
                    toRemove.append(item)
            if len(toRemove):
                for item in toRemove:
                    self.deleteMsg(item)



class DemandIndicator(Widget):
    def __init__(self):
        super(DemandIndicator,self).__init__()
        self.bgColor = (100,140,128,160)
        self.bgRect = None
        self.border = None
        
    def delete(self):
        if self.bgRect is not None:
            self.bgRect.delete()
            self.bgRect = None
        if self.border is not None:
            self.border.delete()
            self.border = None

    def size(self, frame):
        super(DemandIndicator,self).size(frame)
        
        self.width = 78
        self.height = 78
    
    def layout(self,x,y):
        super(DemandIndicator,self).layout(x,570)
        self.createBackground()

        
    def createBackground(self):
        self.delete()
        
        self.bgRect = createRect(self.x, self.y,
                             self.width, self.height,
                             self.bgColor,
                             self.savedFrame.batch,
                             mgGroup)
        
        self.border = createHollowRect(self.x, self.y,
                             self.width, self.height,
                             (0,0,0,255),
                             self.savedFrame.batch,
                             highlightGroup)
        
class View(pyglet.event.EventDispatcher):
    def __init__(self, controlPanel, layout):
        self.layout = layout
        self.controlPanel = controlPanel
    
    def getLayout(self):
        return self.layout
        
class CityMenu(View):
    def __init__(self, controlPanel, microWindow):
        self.microWindow = microWindow
        
        self.months = []
        for (name,month) in gui.config.items('month_strings'):
            self.months.append(month)
        self.populationText = gui.config.get('control_panel_strings', 
                                             'POPULATION')
        self.fundsText = gui.config.get('control_panel_strings', 'FUNDS')
        self.speedText = " Speed"
        
        self.lastCityTime = -4 # one month in past
        
        super(CityMenu,self).__init__(controlPanel, self.createLayout())
        
    def createLayout(self):
        self.demandIndicator = DemandIndicator()
        mainMenuText = gui.config.get('control_panel_strings', 'MAIN_MENU')
        self.mainMenuButton = ButtonLabel(text=mainMenuText,
                                         fontName=fontName,
                                         fontSize=fontSize,
                                         action=self.mainMenuAction)
        self.speedButton = ButtonLabel("",
                                       fontName=fontName,
                                      fontSize=fontSize,
                                      action=self.speedAction)
        self.dataViewButton = ButtonLabel(text="Data View",
                                      fontName=fontName,
                                      fontSize=fontSize,
                                      action=self.dataViewAction)
        self.fundsButton = ButtonLabel(fontName=fontName,
                                      fontSize=fontSize,
                                      action=self.fundsAction)
        self.dateButton = ButtonLabel(fontName=fontName,
                                      fontSize=fontSize,
                                     action=self.dateAction)
        self.populationButton = ButtonLabel(fontName=fontName,
                                           fontSize=fontSize, 
                                           action=self.populationAction)
        return VerticalLayout([self.demandIndicator,
                                 self.mainMenuButton,
                                 self.speedButton,
                                 self.dataViewButton,
                                 self.fundsButton,
                                 self.dateButton,
                                 self.populationButton],
                                align=HALIGN_RIGHT,
                                padding=6,
                                fillWidth=True)
        
    def reset(self, eng):
        self.on_funds_changed(eng.budget.funds)
        self.on_census_changed(0)
        self.lastCityTime = eng.cityTime - 4
        self.on_date_changed(eng.cityTime)
        
    def speedAction(self):
        self.microWindow.incrementSpeed()
        
    def dataViewAction(self):
        self.controlPanel.switchMenu('DataVisualsMenu')
            
    def mainMenuAction(self):
        MainMenuDialog.toggle()
        
    def dateAction(self):
        pass
        
    def fundsAction(self):
        BudgetDialog.toggle()
        
    def populationAction(self):
        CityEvalDialog.toggle()
        
    def speed_changed(self, newSpeed):
        self.speedButton.set_text(newSpeed.name + self.speedText)
                                        
    def on_date_changed(self, cityTime):
        if cityTime - self.lastCityTime >= 4:
            self.lastCityTime = cityTime
            d = self.formatGameDate(cityTime)
            if self.dateButton is not None:
                self.dateButton.set_text(d)
        
    def formatGameDate(self, cityTime):
        year = 1900 + cityTime / 48
        month = self.months[(cityTime % 48) / 4]
        #d = "Week " + str((cityTime % 4) + 1)
        return "{} {}".format(month,year)
    
    def on_census_changed(self, population):
        if self.populationButton is not None:
            self.populationButton.set_text(self.populationText + " " + str(population))

    def on_funds_changed(self, funds):
        t = self.fundsText + str(funds)
        if self.fundsButton is not None:
            self.fundsButton.set_text(t)
    
    

class DataVisualsMenu(View):
    def __init__(self, controlPanel, cityView):
        super(DataVisualsMenu,self).__init__(controlPanel,
                                             self.createLayout())
        self.cityView = cityView
        
    def createLayout(self):
        self.titleLabel = LayoutLabel(text="Data Views",
                                      fontName=fontName,
                                      fontSize=fontSize+8)
        self.backLabel = ButtonLabel(text="Back",
                                      fontName=fontName,
                                      fontSize=fontSize - 2,
                                      action=self.backAction)
        self.resLabel = ButtonLabel(text="Residential",
                                      fontName=fontName,
                                      fontSize=fontSize - 2,
                                         action=self.resAction)
        self.comLabel = ButtonLabel(text="Commercial",
                                      fontName=fontName,
                                      fontSize=fontSize - 2,
                                         action=self.comAction)
        self.indLabel = ButtonLabel(text="Industrial",
                                      fontName=fontName,
                                      fontSize=fontSize - 2,
                                         action=self.indAction)
        self.transLabel = ButtonLabel(text="Transportation",
                                      fontName=fontName,
                                      fontSize=fontSize - 2,
                                         action=self.transAction)
        self.rogLabel = ButtonLabel(text='rate of growth',
                                         fontName=fontName,
                                         fontSize=fontSize - 2,
                                         action=self.rogAction)
        self.landValueLabel = ButtonLabel("land value",
                                        fontName=fontName,
                                         fontSize=fontSize - 2,
                                      action=self.landValueAction)
        self.crimeLabel = ButtonLabel("crime",
                                         fontName=fontName,
                                         fontSize=fontSize - 2,
                                     action=self.crimeAction)
        self.pollutionLabel = ButtonLabel("pollution",
                                         fontName=fontName,
                                         fontSize=fontSize - 2,
                                     action=self.pollutionAction)
        self.trafficDensityLabel = ButtonLabel("traffic density",
                                        fontName=fontName,
                                         fontSize=fontSize - 2, 
                                           action=self.trafficDensityAction)
        self.fireLabel = ButtonLabel("fire radius",
                                      fontName=fontName,
                                         fontSize=fontSize - 2, 
                                           action=self.fireAction)
        self.policeLabel = ButtonLabel("police radius",
                                     fontName=fontName,
                                         fontSize=fontSize - 2,
                                           action=self.policeAction)
        return VerticalLayout([self.titleLabel,
                                Spacer(height=2),
                                self.backLabel,
                                Spacer(height=2),
                                self.resLabel,
                                self.comLabel,
                                self.indLabel,
                                self.transLabel,
                                self.rogLabel,
                                self.landValueLabel,
                                self.crimeLabel,
                                self.pollutionLabel,
                                self.trafficDensityLabel,
                                self.fireLabel,
                                self.policeLabel],
                                align=HALIGN_RIGHT,
                                padding=6,
                                fillWidth=True)
        
    def backAction(self):
        self.controlPanel.switchMenu()
    
    def resAction(self):
        pass
    
    def comAction(self):
        pass
    
    def indAction(self):
        pass
    
    def transAction(self):
        pass    
    
    def rogAction(self):
        pass
    
    def landValueAction(self):
        pass
    
    def crimeAction(self):
        pass
    
    def pollutionAction(self):
        pass
    
    def trafficDensityAction(self):
        pass
    
    def fireAction(self):
        pass
    
    def policeAction(self):
        pass
    

'''class GraphsMenu(View):
    def __init__(self):
        super(GraphsMenu,self).__init__(self.createLayout())
        
    def createLayout(self):
        self.titleLabel = LayoutLabel("Main Menu",
                                      fontName=fontName,
                                      fontSize=fontSize)
        self.rogLabel = ButtonLabel(text='Back',
                                         fontName=fontName,
                                         fontSize=fontSize,
                                         action=self.rogAction)
        self.landValueLabel = ButtonLabel("New City",
                                        fontName=fontName,
                                         fontSize=fontSize,
                                      action=self.landValueAction)
        self.crimeLabel = ButtonLabel("Load City",
                                         fontName=fontName,
                                         fontSize=fontSize,
                                     action=self.crimeAction)
        self.pollutionLabel = ButtonLabel("Save City",
                                         fontName=fontName,
                                         fontSize=fontSize,
                                     action=self.pollutionAction)
        self.trafficDensityLabel = ButtonLabel("Options",
                                        fontName=fontName,
                                         fontSize=fontSize, 
                                           action=self.trafficDensityAction)
        self.fireLabel = ButtonLabel("About",
                                      fontName=fontName,
                                         fontSize=fontSize, 
                                           action=self.fireAction)
        self.policeLabel = ButtonLabel("Quit",
                                     fontName=fontName,
                                         fontSize=fontSize,
                                           action=self.policeAction)
        return VerticalLayout([self.titleLabel,
                                    Spacer(height=2),
                                    self.rogLabel,
                                    self.landValueLabel,
                                    self.crimeLabel,
                                    self.pollutionLabel,
                                    self.trafficDensityLabel,
                                    self.fireLabel,
                                    self.policeLabel])
        
    def rogAction(self):
        #self.dispatch_event('switch_menu', 'CityMenu')
        pass
    
    def landValueAction(self):
        pass
    
    def crimeAction(self):
        pass
    
    def pollutionAction(self):
        pass
    
    def trafficDensityAction(self):
        pass
    
    def fireAction(self):
        pass
    
    def policeAction(self):
        pass'''




class ControlPanel(Frame, pyglet.event.EventDispatcher):
    '''
    
    
    '''
    WIDTH = 300
    DEFAULT_MENU = 'CityMenu'
    def __init__(self, microWindow, cityView):
        self.fgGroup = fgGroup
        self.bg = None
        self.border = None
        
        self.msgs = MessageQueue(padding=3)

        self.cityMenu = CityMenu(self, microWindow)
        self.views = {
                      'CityMenu': self.cityMenu,
                      'DataVisualsMenu': DataVisualsMenu(self, cityView)}
        
        self.setLayout(self.DEFAULT_MENU)
        super(ControlPanel,self).__init__(self.content)
        
        self.minWindowWidth = int(gui.config.get('control_panel', 'MIN_WINDOW_WIDTH'))
        bgColorStr = gui.config.get('control_panel', 'BG_COLOR')
        self.bgColor = map(int, tuple(bgColorStr.split(',')))
    
    def reset(self, window, eng):
        if eng:
            self.cityMenu.reset(eng)
            eng.push_handlers(self,self.cityMenu)
            window.push_handlers(self, self.cityMenu)
            
    def speed_changed(self, newSpeed):
        self.addInfoMessage(newSpeed.name + " Speed")
        
    def size(self,frame):
        self.delete()
        if frame.width < self.minWindowWidth:
            self.disable()
            self.width = 0
        if frame.width >= self.minWindowWidth:
            self.enable()
        if self.enabled:
            super(ControlPanel,self).size(frame)
            self.width, self.height = self.WIDTH, frame.height
            
    def expand(self, width, height):
        Frame.expand(self, width, height)
        self.width = self.WIDTH
        
    def layout(self, x, y):
        super(ControlPanel,self).layout(x,y)
        if self.enabled:
            self.createBg()
        #print self.content.content[0].width
        
    def switchMenu(self, viewName=None):
        oldContent = self.content
        oldContent.delete()
        self.setLayout(viewName)
        self.setNeedsLayout()
        
        
    def setLayout(self, viewName):
        if not viewName:
            viewName = 'CityMenu'
        try:
            self.currentView = self.views[viewName].getLayout()
        except KeyError:
            print "Invalid View Name"
            return
        self.content = VerticalLayout([self.currentView,
                                  Spacer(height=10),
                                  self.msgs],
                                 padding=0)
        
        
    def delete(self):
        if self.bg is not None:
            self.bg.delete()
            self.bg = None
        if self.border is not None:
            self.border.delete()
            self.border = None
        super(ControlPanel,self).delete()

        

    def createBg(self):
        self.bg = createRect(self.x, self.y,
                             self.width, self.height,
                             self.bgColor,
                             self.savedFrame.batch,
                             bgGroup)
        self.border = createRect(self.x, self.y, 
                                 1, self.height, 
                                 (0, 0, 0, 255),
                                 self.savedFrame.batch, 
                                 highlightGroup)
        
    def addInfoMessage(self, msg):
        self.msgs.addMessage(msg)

    def city_message(self, msg):
        self.msgs.addMessage(msg)
        
    def update(self, dt):
        self.msgs.update(dt)
            

        
        
        
        
        
        
        
        
        
        
        
        
        
        
    