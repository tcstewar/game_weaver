from mtg import *
from mtg_enchant import Enchantment
from mtg_artifact import Artifact
from mtg_creatures import Creature

class TargettedInstant(Targetted):
    def doneCast(self):
        Targetted.doneCast(self)
        self.destroy()
    

class Counterspell(TargettedInstant):
    cost='UU'
    def canSetTarget(self,target):
        if target._isDoneCasting: return 0
        return 1
    def getCastEventInfo(self):
        return 'Countering',counterDelay
    def onCast(self):
        if not self.target._isDoneCasting:
            self.target.destroy()

class AncestralRecall(TargettedInstant):
    cost='U'
    def canSetTarget(self,target):
        return isinstance(target,MtGPlayer)
    def onCast(self):
        self.target.doDrawCard()
        self.target.doDrawCard()
        self.target.doDrawCard()

class LightningBolt(TargettedInstant):
    cost='R'
    def canSetTarget(self,target):
        return isinstance(target,Damageable)
    def onCast(self):
        self.target.doDamage(3,self)


class Disenchant(TargettedInstant):
    cost='1W'
    def canSetTarget(self,target):
        if not target._isDoneCasting:
            return 0
        if isinstance(target,Enchantment):
            return 1
        if isinstance(target,Artifact):
            return 1
        return 0
    def onCast(self):
        self.target.destroy()
        
class SwordsToPlowshares(TargettedInstant):
    cost='W'
    def canSetTarget(self,target):
        return isinstance(target,Creature)
    def onCast(self):
        self.owner.gainHealth(self.target.power)
        self.target.destroy()
