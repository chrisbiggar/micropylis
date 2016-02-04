from random import randint


class CityEval(object):

    def __init__(self, engine):
        self.engine = engine

        ''' % of population approving the mayor. derived from cityScore '''
        self.cityYes = 0

        ''' Percentage of population "disapproving" the mayor. Derived from cityScore. '''
        self.cityNo = 0

        ''' City assessment value '''
        self.cityAssValue = 0

        ''' Player's score, 0-1000 '''
        self.cityScore = 0

        ''' Change in cityscore since last eval '''
        self.deltaCityScore = 0

        ''' City pop as of current eval '''
        self.cityPop = 0

        ''' Change in city pop since last eval '''
        self.deltaCityPop = 0

        ''' Classification of city size 0==village, 1==town, etc. '''
        self.cityClass = 0 # 0...5

        ''' City's top 4 (or fewer) problems as reported by citizens '''
        self.problemOrder = None

        ''' Number of votes given for the various problems identified by problemOrder[]. '''
        self.problemVotes = None

        ''' Score for various problems '''
        self.problemTable = None

    def cityEvaluation(self):
        if self.engine.totalPop != 0:
            self.calculateAssValue()
            self.doPopNum()
            self.doProblems()
            self.calculateScore()
            self.doVotes()
        else:
            self.evalInit()
        self.engine.dispatch_event("on_evaluation_changed")

    def evalInit(self):
        self.cityScore = 500
        

    def calculateAssValue(self):
        pass

    def doPopNum(self):
        pass

    def doProblems(self):
        pass

    def calculateScore(self):
        pass

    def doVotes(self):
        pass