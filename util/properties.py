'''
Created on Oct 18, 2015

@author: chris
'''
import re



class Properties(object):
    '''
    Properties class that separate lines in a files based on
    whitespace into key, value pairs. key must be at start of line.
    setting properties is not tested.
    '''
    def __init__(self):
        self._props = {}
        self._keyMap = {}
        self._origProps = {}
        self.spaceR = re.compile(r'(?<![\\])(\s)')
        
    def containsKey(self, key):
        if key in self._props:
            return True
        else:
            return False
    
    def getPropertyFlat(self, key):
        try:
            return self.unEscape(self._props[key])
        except KeyError:
            return None
    
    def getProperty(self, key):
        try:
            return self._props[key]
        except KeyError:
            return None
    
    def setProperty(self, key, value):
        # not tested!
        if type(key) is str and type(value) is str:
            self.processPair(key, value)
        else:
            raise TypeError('both key and value should be strings!')
        
    def size(self):
        return len(self._props)
        
    def propertyNames(self):
        return list(self._props.keys())
    
    def __getitem__(self, name):
        return self.getProperty(name)
    
    def __setitem(self, name, value):
        self.setProperty(name, value)
        
    def __getattr(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            if hasattr(self._props,name):
                return getattr(self._props, name)
        
    def __parse(self, lines):
        ''' parse list of lines and create an 
            internal property dictionary '''
        
        lineNum = 0
        i = iter(lines)
        
        for line in i:
            lineNum += 1
            # skip null lines
            if not line: continue
            # skip lines which are comments
            if line[0] == '#': continue
            
            sepIdX = -1
            start, end = 0, len(line)
            m = self.spaceR.search(line, start, end)
            if m:
                first, last = m.span()
                sepIdX = last - 1
            
            if sepIdX != -1:
                key, value = line[:sepIdX], line[sepIdX+1:]
            else:
                key, value = line,''
            self.processPair(key, value)
        
    def processPair(self, key, value):
        oldKey = key
        oldValue = value
        
        #
        keyParts = self.spaceR.split(key)
        
        strippable = False
        lastPart = keyParts[-1]
        
        if lastPart.find('\\ ') != -1:
            keyParts[-1] = lastPart.replace('\\','')

        # If no backspace is found at the end, but empty
        # space is found, strip it
        elif lastPart and lastPart[-1] == ' ':
            strippable = True
        
        key = ''.join(keyParts)
        if strippable:
            key = key.strip()
            oldKey = oldKey.strip()
        
        oldValue = self.unEscape(oldValue)
        value = self.unEscape(value)
        
        self._props[key] = value.strip()
        
        if key in self._keyMap:
            oldKey = self._keyMap.get(key)
            self._origProps[oldKey] = oldValue.strip()
        else:
            self._origProps[oldKey] = oldValue.strip()
            self._keyMap[key] = oldKey
        
    
    def load(self, stream):
        '''if type(stream) is not file:
            raise TypeError('Argument should be a file object!')'''
        if stream.mode != 'r':
            raise ValueError('Stream should be opened in read-only mode')
        
        try:
            lines = stream.readlines()
            self.__parse(lines)

        except IOError as e:
            raise
        
        
    def unEscape(self, value):
        newValue = value.replace('\:', ':')
        newValue = newValue.replace('\=','=')
        return newValue