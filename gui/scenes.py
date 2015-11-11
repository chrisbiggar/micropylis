'''
Created on Oct 24, 2015

@author: chris
'''




class Directory(object):
    def __init__(self):
        self._scenes = dict()
        self._currentScene = None
        
    def setCurrentScene(self, name):
        self._currentScene = self._scenes[name]
    
    def addScene(self, scene):
        self._scenes[scene.name] = scene
        
    
    def update(self, dt):
        if self._currentScene is not None:
            self._currentScene.update(dt)


class Scene(object):
    def __init__(self, name):
        self.name = name
        
        
    def update(self, dt):
        pass