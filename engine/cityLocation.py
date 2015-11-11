'''

QUESTIONS:

hashcode? what is this needed for? 

'''


class CityLocation(object):
    '''
        Coordinates of a location in the city
    '''
    def __init__(self, x, y):
        # lower X correspond to east, higher west
        self.x = x
        # lower Y correspond to north, higher south
        self.y = y
        
    def hashCode(self):
        return self.x * 33 + self.y
        
    def equals(self, loc):
        if loc is CityLocation:
            return self.x == loc.x and self.y == loc.y
        else:
            return False
    
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
        
        