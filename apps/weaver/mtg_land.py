from mtg import *


class Land(Card):
    cost=''
    color=''
    def canCast(self,player):
        return not player._hasCastLand
    def cast(self,player):
        self.owner=player
        self._isDoneCasting=1
        self.a1=Action(self,'Tap for %s' % self.mana,self.getMana)
        player.setCastLand()
    def getMana(self):
        if self.tapped: return
        if self.owner!=None:
            self.owner.addMana(self.mana)
        self.tap()

class Plains(Land):
    name='Plains'
    mana='W'
class Mountain(Land):
    name='Mountain'
    mana='R'
class Island(Land):
    name='Island'
    mana='U'
class Forest(Land):
    name='Forest'
    mana='G'
class Swamp(Land):
    name='Swamp'
    mana='B'

