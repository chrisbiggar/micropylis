'''
    CityRect

    Coordinates of a location in the city
'''


class CityRect(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        # upper left corner coords
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def equals(self, rect):
        if isinstance(rect, CityRect):
            return (self.x == rect.x and self.y == rect.y
                    and self.height == rect.height
                    and self.width == rect.width)
        else:
            return False

    def __str__(self):
        return "[" + str(self.x) + "," + str(self.y) + \
               "," + str(self.width) + "," + str(self.height) + "]"
