'''
Created on Oct 29, 2015

@author: chris
'''
from math import floor
import pyglet
from pyglet.text import Label
from pyglet.text.layout import TextLayout
from pyglet.text.document import UnformattedDocument, FormattedDocument
from pyglet.gl import *
import gui
from layout import Widget,Frame,VerticalLayout,\
                            HALIGN_RIGHT, Spacer, ButtonLabel
from util import createRect

bgGroup = pyglet.graphics.OrderedGroup(4)
mgGroup = pyglet.graphics.OrderedGroup(5)
fgGroup = pyglet.graphics.OrderedGroup(6)

MSG_SHOW_TIME = 8 # in seconds
MSG_DELETE_FREQ = 0.5


class Message(object):
    def __init__(self, num, msg, startTime, start):
        self.string = msg
        self.time = int(startTime)
        self.index = start
        self.num = num
    
    def isExpired(self, secs):
        return int(secs) > self.time + MSG_SHOW_TIME * 2
    
    def __len__(self):
        return len(self.string)
    

'''
    displays messages to user. 
'''
class MessageQueue(Widget):
    def __init__(self, fontName=None, padding=0):
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
        self.fontName = fontName
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
                             fgGroup)
        
        
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
        item = Message(0, message, self.halfSecs, 0)
        
        
        self.doc.set_style(0, len(self.doc.text), {'font_name' : self.font,
                                                   'bold' : False})
        for msg in self.msgs:
            msg.num += 1
            msg.index += len(item)
        
        self.msgs.insert(0,item)
        self.doc.insert_text(0, message, {'font_name' : self.font,
                                                   'bold' : True})
        
        if self.textLayout is not None:
            while self.textLayout.content_height >= self.height - self.titleLabel.content_height + 14:
                item = self.msgs[len(self.msgs)-1]
                self.deleteMsg(item)
        
            
    def update(self, dt):
        self.dt += dt
        if self.dt >= MSG_DELETE_FREQ:
            # expired messages are collected on 0.5 sec freq
            self.halfSecs += 1
            self.dt = self.dt % MSG_DELETE_FREQ
            toRemove = []
            for item in self.msgs:
                if item.isExpired(self.halfSecs):
                    toRemove.append(item)
            if len(toRemove):
                for item in toRemove:
                    self.deleteMsg(item)



class DemandIndicator(Widget):
    def __init__(self):
        self.bgRect = None
        self.border = None

    def size(self, frame):
        super(MessageQueue,self).size(frame)
        
        self.width = 120
        self.height = 200
        
        self.createBackground()
        
    
    def layout(self,x,y):
        super(MessageQueue,self).layout(x,y)

        
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
                             self.batch,
                             mgGroup)
        
        '''self.border = createRect(self.x, self.y + self.height,
                             self.width, 1,
                             (0,0,0,255),
                             self.batch,
                             fgGroup)'''



class ControlPanel(Frame, pyglet.event.EventDispatcher):
    '''
    
    
    '''
    WIDTH = 300
    def __init__(self):
        self.register_event_type('gui_invoke')
        
        self.engine = None
        
        self.months = []
        for (name,month) in gui.config.items('month_strings'):
            self.months.append(month)
        self.mainMenuText = gui.config.get('control_panel_strings', 'MAIN_MENU')
        self.populationText = gui.config.get('control_panel_strings', 'POPULATION')
        self.fundsText = gui.config.get('control_panel_strings', 'FUNDS')
        
        self.fontName = gui.config.get('control_panel', 'FONT')
        self.fontSize = 16
        
        self.minWindowWidth = int(gui.config.get('control_panel', 'MIN_WINDOW_WIDTH'))
        bgColorStr = gui.config.get('control_panel', 'BG_COLOR')
        self.bgColor = map(int, tuple(bgColorStr.split(',')))
        
        #self.batch = pyglet.graphics.Batch()
        self.fgGroup = fgGroup
        self.bg = None
        self.border = None
        layout = self.createLayout()
        super(ControlPanel,self).__init__(layout)
        
        #self.reset(engine)
        self.updateDateLabel()
        self.on_funds_changed()
        self.on_census_changed()
    
    def reset(self, eng):
        self.engine = eng
        if eng:
            eng.push_handlers(self)
            self.lastTime = self.engine.cityTime
        self.on_funds_changed()
        self.on_census_changed()
        
    def size(self,frame):
        self.delete()
        if frame.width < self.minWindowWidth:
            self.disable()
            self.width = 0
        if frame.width >= self.minWindowWidth:
            self.enable()
        if self.active:
            super(ControlPanel,self).size(frame)
            self.width, self.height = self.WIDTH, frame.height
            
    def expand(self, width, height):
        Frame.expand(self, width, height)
        self.width = self.WIDTH
        
    def layout(self, x, y):
        super(ControlPanel,self).layout(x,y)
        if self.active:
            self.createBg()
        
    def createLayout(self):
        self.mainMenuLabel = ButtonLabel(self, text=self.mainMenuText,
                                         fontName=self.fontName,
                                         fontSize=self.fontSize,
                                         action=self.mainMenuLabelAction)
        self.fundsLabel = ButtonLabel(self, fontName=self.fontName, 
                                      fontSize=self.fontSize,
                                      action=self.fundsLabelAction)
        self.dateLabel = ButtonLabel(self, fontName=self.fontName, 
                                     fontSize=self.fontSize,
                                     action=self.dateLabelAction)
        self.populationLabel = ButtonLabel(self,
                                           fontSize=self.fontSize,
                                           fontName=self.fontName, 
                                           action=self.populationLabelAction)
        self.msgs = MessageQueue(fontName=self.fontName, padding=3)
        return VerticalLayout([VerticalLayout([self.mainMenuLabel,
                                                  self.dateLabel,
                                                  self.fundsLabel,
                                                  self.populationLabel],
                                                 align=HALIGN_RIGHT,
                                                 padding=5),
                                  Spacer(height=10),
                                  self.msgs],
                                 align=HALIGN_RIGHT,
                                 padding=0)
        
        
    def mainMenuLabelAction(self):
        self.dispatch_event('gui_invoke', 'main_menu')
        
    def dateLabelAction(self):
        #self.dispatch_event('gui_invoke', 'city_graphs')
        pass
        
    def fundsLabelAction(self):
        self.dispatch_event('gui_invoke', 'budget_menu')
        
    def populationLabelAction(self):
        #print "bah"
        self.dispatch_event('gui_invoke', 'city_eval')
        
    def delete(self):
        if self.bg is not None:
            self.bg.delete()
            self.bg = None
        if self.border is not None:
            self.border.delete()
            self.border = None
        self.content.delete()

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
                                 fgGroup)
        
    
    def addInfoMessage(self, msg):
        self.msgs.addMessage(msg)


    def city_message(self, msg):
        self.msgs.addMessage(msg)


    def on_census_changed(self):
        if self.populationLabel is not None:
            self.populationLabel.set_text(self.populationText + ": 0")

     
    def on_funds_changed(self):
        if self.engine:
            t = self.fundsText + str(self.engine.budget.funds)
        else:
            #print "fundschanged"
            #print self.fundsText
            t = self.fundsText
        if self.fundsLabel is not None:
            self.fundsLabel.set_text(t)
        
    
    def update(self, dt):
        self.msgs.update(dt)
        if (self.engine and
            (self.lastTime != self.engine.cityTime and
                self.lastTime + 4 <= self.engine.cityTime)):
            self.lastTime = self.engine.cityTime
            self.updateDateLabel()
            
    
    def formatGameDate(self, cityTime):
        year = 1900 + cityTime / 48
        month = self.months[(cityTime % 48) / 4]
        #d = "Week " + str((cityTime % 4) + 1)
        return "{} {}".format(month,year)
        
        
    def updateDateLabel(self):
        if self.engine:
            d = self.formatGameDate(self.engine.cityTime)
        else:
            d = "Jan 1990"
        if self.dateLabel is not None:
            self.dateLabel.set_text(d)
        # update population
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    