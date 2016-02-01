'''
Created on Dec 7, 2015

@author: chris
'''


class CityDimension(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def hashCode(self):
        return self.width * 33 + self.height

    def equals(self, obj):
        if isinstance(obj, self.__class__):
            return (self.width == obj.width and
                    self.height == obj.height)
        else:
            return False

    def toString(self):
        return str(self.width) + "x" + str(self.height)
