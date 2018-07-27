from mtg import *

from mtg_land import Land

class Artifact(Spell):
    pass

class AnkhOfMishra(Artifact):
    cost='2'
    def doneCast(self):
        self.addOverride(Land.cast,self.doCast)
    def doCast(self,card,player,baseFnc):
        baseFnc(card,player)
        card.owner.doDamage(2,self)

class LifeOnSpellArtifact(Artifact):
    cost='1'
    def doneCast(self):
        self._queue={}
        self.addOverride(Configurable.cast,self.onCast)
        self.addOverride(Spell.cast,self.onCast)
    def onCast(self,card,player,baseFnc):
        baseFnc(card,player)
        if card.color==self.spellColor:
            args=(id(card),)
            e=Event(self,'Time Limit',spellForLifeDelay,self.timeOut,args=args)
            a=Ability(self,'Gain Life',self.gainLife,args=args,secret=1,manaCost='1',delay=0.1)
            self._queue[id(card)]=(e,a)
    def timeOut(self,id):
        if id not in self._queue.keys(): return
        e,a=self._queue[id]
        del self._queue[id]
        a.remove()
    def gainLife(self,id):
        if id not in self._queue.keys(): return
        e,a=self._queue[id]
        del self._queue[id]
        a.remove()
        e.cancel()
        self.owner.gainHealth(1)
        
class WoodenSphere(LifeOnSpellArtifact):
    spellColor='g'
class CrystalRod(LifeOnSpellArtifact):
    spellColor='u'
class IronStar(LifeOnSpellArtifact):
    spellColor='r'
class IvoryCup(LifeOnSpellArtifact):
    spellColor='w'
class ThroneOfBone(LifeOnSpellArtifact):
    spellColor='b'

class SoulNet(LifeOnSpellArtifact):
    cost='1'
    def doneCast(self):
        self._queue={}
        self.addOverride(Creature.die,self.onCast)
        self.addOverride(Spell.cast,self.onCast)
    def onCast(self,card,baseFnc):
        baseFnc(card)
        args=(id(card),)
        e=Event(self,'Time Limit',spellForLifeDelay,self.timeOut,args=args)
        a=Ability(self,'Gain Life',self.gainLife,args=args,secret=1,manaCost='1',delay=0.1)
        self._queue[id(card)]=(e,a)

class SolRing(Artifact):
    cost='1'
    def doneCast(self):
        Ability(self,'2 Mana',self.gain2Mana,tap=1,delay=0.1)
    def gain2Mana(self):
        self.owner.addMana('xx')
    
class LibraryOfLeng(Artifact):
    cost='1'
    def doneCast(self):
        self.addOverride(MtGPlayer.checkCardCount,(lambda player,baseFnc: None))

class HowlingMine(Artifact):
    cost='2'
    def doneCast(self):
        self.addOverride(MtGPlayer.doDrawCard,self.drawExtra)
    def drawExtra(self,player,baseFunc):
        player._hand.addCard(player._deck.draw())
        baseFunc(player)

class BlackLotus(Artifact):
    cost='0'
    def doneCast(self):
        Ability(self,'3 White',self.doIt,args=('w',),delay=0.1,tap=1,sacrifice=1)
        Ability(self,'3 Red',self.doIt,args=('r',),delay=0.1,tap=1,sacrifice=1)
        Ability(self,'3 Black',self.doIt,args=('b',),delay=0.1,tap=1,sacrifice=1)
        Ability(self,'3 Blue',self.doIt,args=('u',),delay=0.1,tap=1,sacrifice=1)
        Ability(self,'3 Green',self.doIt,args=('g',),delay=0.1,tap=1,sacrifice=1)
    def doIt(self,color):
        self.owner.addMana(color*3)

class Mox(Artifact):
    cost='0'
    def doneCast(self):
        Ability(self,'Get 1 %s'%self.moxColor,self.doIt,delay=0.1,tap=1)
    def doIt(self):
        self.owner.addMana(self.moxColor)

class MoxEmerald(Mox):
    moxColor='G'
class MoxRuby(Mox):
    moxColor='R'
class MoxJet(Mox):
    moxColor='B'
class MoxPearl(Mox):
    moxColor='W'
class MoxSapphire(Mox):
    moxColor='B'
    
    
    
