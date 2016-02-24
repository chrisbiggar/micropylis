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
        self.name = None  # set by key string in speeds

speeds = OrderedDict((('Paused', Speed(None, 999)),
                       ('Slow', Speed(0.625, 0.6)),
                       ('Normal', Speed(0.125, 0.3)),
                       ('Fast', Speed(0.025, 0.1)),
                       ('Super Fast', Speed(0.025, 0.02))))


for speedKey in speeds.keys():
    speeds[speedKey].name = speedKey