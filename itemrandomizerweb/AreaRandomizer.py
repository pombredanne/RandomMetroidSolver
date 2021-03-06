import random

from itemrandomizerweb.Randomizer import Randomizer
from graph_access import vanillaTransitions, accessPoints, getAccessPoint

def createTransitions(bidir=True):
    tFrom = []
    tTo = []
    apNames = [ap.Name for ap in accessPoints if ap.Internal == False and ap.Boss == False]
    transitions = []

    def findTo(trFrom):
        ap = getAccessPoint(trFrom)
        fromArea = ap.GraphArea
        targets = [apName for apName in apNames if apName not in tTo and getAccessPoint(apName).GraphArea != fromArea]
        if len(targets) == 0: # fallback if no area transition is found
            targets = [apName for apName in apNames if apName != ap.Name]
        return targets[random.randint(0, len(targets)-1)]

    def addTransition(src, dst):
        tFrom.append(src)
        tTo.append(dst)

    while len(apNames) > 0:
        sources = [apName for apName in apNames if apName not in tFrom]
        src = sources[random.randint(0, len(sources)-1)]
        dst = findTo(src)
        transitions.append((src, dst))
        addTransition(src, dst)
        if bidir is True:
            addTransition(dst, src)
        toRemove = [apName for apName in apNames if apName in tFrom and apName in tTo]
        for apName in toRemove:
            apNames.remove(apName)
    return transitions

class AreaRandomizer(Randomizer):
    def __init__(self, locations, settings, seedName, bossTransitions, bidir=True, dotDir=None):
        transitionsOk = False
        attempts = 0
        while not transitionsOk and attempts < 10:
            try:
                self.transitions = createTransitions(bidir)
                super(AreaRandomizer, self).__init__(locations,
                                                     settings,
                                                     seedName,
                                                     self.transitions + bossTransitions,
                                                     bidir,
                                                     dotDir)
                transitionsOk = True
            except RuntimeError:
                transitionsOk = False
                attempts += 1
        if not transitionsOk:
            raise RuntimeError("Impossible seed! (too much fun in the settings, probably)")

    # adapt restrictions implementation to different area layout

    def areaDistance(self, loc, otherLocs):
        return self.areaDistanceProp(loc, otherLocs, 'GraphArea')
