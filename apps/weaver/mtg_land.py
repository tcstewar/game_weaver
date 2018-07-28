from mtg import *


class Land(Card):
    cost=''
    color=''
    def canCast(self,player):
        return not player._hasCastLand
    def cast(self,player):
        self.owner=player
        self._isDoneCasting=1
        for m in self.mana:
            Action(self, 'Tap for %s' % m, self.getMana, args=(m,))
        player.setCastLand()
    def getMana(self, m):
        if self.tapped: return
        if self.owner!=None:
            self.owner.addMana(m)
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
class Badlands(Land):
    name='Badlands'
    mana='BR'
class Bayou(Land):
    name='Bayou'
    mana='BG'
class Plateau(Land):
    name='Plateau'
    mana='RW'
class Savannah(Land):
    name='Savannah'
    mana='GW'
class Scrubland(Land):
    name='Scrubland'
    mana='BW'
class Taiga(Land):
    name='Taiga'
    mana='GR'
class TropicalIsland(Land):
    name='Tropical Island'
    mana='UG'
class Tundra(Land):
    name='Tundra'
    mana='UW'
class UndergroundSea(Land):
    name='Underground Sea'
    mana='BU'
class VolcanicIsland(Land):
    name='Volcanic Island'
    mana='UR'
