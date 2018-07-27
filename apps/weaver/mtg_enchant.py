from mtg import *

from mtg_land import *
from mtg_creatures import Creature
import mtg_land

class Enchantment(Spell):
    pass

class TargettedEnchantment(Targetted,Enchantment):
    def doneCast(self):
        self.enchant=self.target
        self.target=None
        self.addOverride(self.enchant.destroy,self.onEnchantDestroy)
        Targetted.doneCast(self)
    def onEnchantDestroy(self,card,baseFnc):
        self.destroy()
        baseFnc()

class EnchantLand(TargettedEnchantment):
    def canSetTarget(self,target):
        return isinstance(target,Land)

class EnchantCreature(TargettedEnchantment):
    def canSetTarget(self,target):
        return isinstance(target,Creature)


class WildGrowth(EnchantLand):
    cost='G'
    def onCast(self):
        self.addOverride(self.enchant.getMana,self.onTapForMana)
    def onTapForMana(self,card,baseFnc):
        baseFnc()
        if card==self.enchant:
            card.owner.addMana('G')
        
    

class Fastbond(Enchantment):
    cost='G'
    def doneCast(self):
        self.addOverride(Land.canCast,self.checkCast)
        self.addOverride(Land.cast,self.doCast)
    def checkCast(self,card,player,baseF):
        return 1
    def doCast(self,card,player,baseF):
        if self.owner==player and player._hasCastLand:
            player.doDamage(1,self)
        baseF(card,player)
        
class Lifetap(Enchantment):
    cost='UU'
    def doneCast(self):
        self.addOverride(Forest.tap,self.tapWatch)
    def tapWatch(self,card,baseFnc):
        if card.owner!=self.owner:
            self.owner.gainHealth(1)
            baseFnc(card)

class ManaFlare(Enchantment):
    cost='2R'
    def doneCast(self):
        self.addOverride(Land.getMana,self.onTapForMana)
    def onTapForMana(self,card,baseFnc):
        if not card.tapped:
            card.owner.addMana(card.mana)
        baseFnc(card)
        
class ManaBarbs(Enchantment):
    cost='3R'
    def doneCast(self):
        self.addOverride(Land.getMana,self.onTapForMana)
    def onTapForMana(self,card,baseFnc):
        if not card.tapped and card.owner!=None:
            card.owner.doDamage(1,self)
        baseFnc(card)
        
class Pestilence(Enchantment):
    cost='2BB'
    def doneCast(self):
        if len(self.getAllInPlay(Creature))==0: self.destroy()
        else:
            self.addOverride(Creature.destroy,self.onCreatureDestroy)
            Ability(self,'Do 1 damage to all',self.doDamage,manaCost='B')
#            Action(self,'B: Deal 1 damage to all',self.onDoIt)
    def doDamage(self):
        for c in self.getAllInPlay(Creature):
            c.doDamage(1,self)
        for p in self.getAllInPlay(MtGPlayer):
            p.doDamage(1,self)
        
    def onDoIt(self):
        if self.owner.hasMana('b'):
            self.owner.drainMana('b')
            for c in self.getAllInPlay(Creature):
                c.doDamage(1,self)
            for p in self.getAllInPlay(MtGPlayer):
                p.doDamage(1,self)
        
    def onCreatureDestroy(self,card,baseFnc):
        baseFnc(card)
        if len(self.getAllInPlay(Creature))==0:
            self.destroy()

class HolyStrength(EnchantCreature):
    cost='W'
    def onCast(self):
        self.addAttrOverride(self.enchant,'power',lambda t,x: x+1)
        self.addAttrOverride(self.enchant,'toughness',lambda t,x: x+2)

class AspectOfWolf(EnchantCreature):
    cost='1G'
    def onCast(self):
        self.addAttrOverride(self.enchant,'power',self.powerInc)
        self.addAttrOverride(self.enchant,'toughness',self.toughInc)
        self.addOverride(Forest.cast,self.doRecalcCast)
        self.addOverride(Forest.destroy,self.doRecalcDestroy)
    def powerInc(self,card,x):
        i=len([c for c in self.getAllInPlay(Forest) if c.owner==self.owner])
        return x+i/2
    def toughInc(self,card,x):
        i=len([c for c in self.getAllInPlay(Forest) if c.owner==self.owner])
        return x+(i+1)/2

    
    def doRecalcCast(self,card,player,baseFunc):
        baseFunc(card,player)
        self.enchant.updateServerValue('power')
        self.enchant.updateServerValue('toughness')
    def doRecalcDestroy(self,card,baseFunc):
        baseFunc(card)
        self.enchant.updateServerValue('power')
        self.enchant.updateServerValue('toughness')
        
        
        
    
        
        
    
class BadMoon(Enchantment):
    cost='1B'
    def doneCast(self):
        self.addAttrOverride(Creature,'power',self.incBlack)
        self.addAttrOverride(Creature,'toughness',self.incBlack)
    def incBlack(self,thing,val):
        if thing.color=='b': return val+1
        return val
                            
class Crusade(Enchantment):
    cost='WW'
    def doneCast(self):
        self.addAttrOverride(Creature,'power',self.incWhite)
        self.addAttrOverride(Creature,'toughness',self.incWhite)
    def incWhite(self,thing,val):
        if thing.color=='w': return val+1
        return val

class LandTax(Enchantment):
    cost='W'
    def doneCast(self):
        self.addOverride(Land.cast,self.doRecalcCast)
        self.addOverride(Land.destroy,self.doRecalcDestroy)
        self.draw=''
        self.recalc()
    def doRecalcCast(self,card,player,baseFunc):
        baseFunc(card,player)
        self.recalc()
    def doRecalcDestroy(self,card,baseFunc):
        baseFunc(card)
        self.recalc()
    def recalc(self):
        all=self.getAllInPlay(Land)
        mine=len([x for x in all if x.owner==self.owner])
        for p in self.getAllInPlay(MtGPlayer):
            c=len([x for x in all if x.owner==p])
            if c>mine:
                self.draw=''
                self.setEditable('draw',self.tryDraw,['']+self.calcBasicLandList())
                return
        self.draw=''
        self.setNoneditable('draw')
    def tryDraw(self,landType):
        klass=getattr(mtg_land,landType,None)
        if klass==None: return
        card=self.owner._deck.drawClass(klass)
        if card==None: return
        self.owner._hand.addCard(card)
        self.owner.checkCardCount()
    def calcBasicLandList(self):
        r=[]
        for t in [Plains,Mountain,Forest,Island,Swamp]:
            if t in self.owner._deck.deck:
                r.append(t.__name__)
        return r
                
            
                
            
