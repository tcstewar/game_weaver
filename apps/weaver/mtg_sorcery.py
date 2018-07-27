from mtg import *
from mtg_land import Land


class Sorcery(Spell):
    _castDelay=sorceryDelay
    def doneCast(self):
        self.onCast()
        self.destroy()

class TargettedSorcery(Targetted):
    def doneCast(self):
        Targetted.doneCast(self)
        self.destroy()

class Armageddon(Sorcery):
    cost='3W'
    def onCast(self):
        for l in self.getAllInPlay(Land):
            l.destroy()

class WrathOfGod(Sorcery):
    cost='2WW'
    def onCast(self):
        for c in self.getAllInPlay(Creature):
            c.destroy()

class Disintegrate(TargettedPumpable):
    cost='R'
    def canSetTarget(self,target):
        return isinstance(target,Damageable)
    def onCast(self):
        self.target.doDamage(self.amount,self)

