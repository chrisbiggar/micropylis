from collections import OrderedDict


'''
contains the data pertinent to each game speed.


animationCoefficient:
    animation duration is set to 0.2.
    animationCoefficient is multiplied to time to produce
    the animation speed desired. 
    divide duration by coefficient to get actual animation duration
    TODO make animation duration stuff more sensical
'''

class Speed(object):
    def __init__(self, animCoefficient, delay):
        self.animCoefficient = animCoefficient
        self.delay = delay
        self.lastTs = 0
        self.name = None # set by key string in speeds


speeds = OrderedDict((('Paused',Speed(0, 999)),
                       ('Slow',Speed(0.34, 0.6)),
                       ('Normal',Speed(1.5, 0.3)),
                       ('Fast',Speed(5, 0.1)),
                       ('Super Fast',Speed(10, 0.02))))

for speedKey in speeds.keys():
    speeds[speedKey].name = speedKey