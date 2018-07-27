from mtg import *
        
class Creature(Spell,Damageable):
    flying=0
    dead=0
    protection=''
    firstStrike=0
    def doneCast(self):
        self._hasSummoningSickness=1
        self.power=self.getWithoutOverrides('power')
        self.toughness=self.getWithoutOverrides('toughness')
        self.damage=0
        self.block=None
        self.attack=None
        self.dyingEvent=None
        self.healEvent=None
        self.blockEvent=None
        self.attackEvent=None
        self.flying=self.flying


        self.setEditable('block',self.setBlock,())
        Event(self,'Summoning Sickness',summoningSicknessDelay,self.doneSickness)
    def doneSickness(self):
        self._hasSummoningSickness=0
        self.attack=None
        self.setEditable('attack',self.setTarget,())
    def setTarget(self,attack):
        if self.attack!=None: return
        if self.block!=None: return
        if attack==None: return
        if not isinstance(attack,Player): return
        if attack==self.owner: return
        self.setNoneditable('attack')
        self.setNoneditable('block')
        self.attackEvent=Event(self,'Attacking',attackDelay,self.doneAttack)
        self.attack=attack
        self.tap()
        self.untapEvent.cancel()
    def doneAttack(self):
        self.attack.doDamage(self.power,self)
        self.attack=None
        self.setEditable('attack',self.setTarget,())
        self.setEditable('block',self.setBlock,())
        self.untapEvent=Event(self,'Untapping',untapDelay,self.untap)
    def setBlock(self,block):
        if self.tapped: return
        if self.block!=None: return
        if block==None: return
        if not isinstance(block,Creature): return
        if block.attack==None: return
        if block.flying and not self.flying: return
        if self.color in block.protection: return
        self.blockEvent=Event(self,'Blocking',blockDelay,self.doneBlock)
        self.setNoneditable('attack')
        self.setNoneditable('block')
        self.block=block
    def doneBlock(self):
        if self.block.owner!=None and not self.block.dead:
            bp=self.block.power
            sp=self.power
            if self.firstStrike and not self.block.firstStrike:
                self.block.doDamage(sp,self)
                if not self.block.dead:
                    self.doDamage(bp,self.block)
            elif self.block.firstStrike and not self.firstStrike:
                self.doDamage(bp,self)
                if not self.dead:
                    self.block.doDamage(sp,self)
            else:
                self.block.doDamage(sp,self)
                self.doDamage(bp,self.block)
        self.block=None
        self.setEditable('attack',self.setTarget,())
        self.setEditable('block',self.setBlock,())
    def doDamage(self,amount,source):
        if source!=None and source.color in self.protection: return
        self.damage+=amount
        if self.damage>=self.toughness:
            print 'calling die'
            self.die()
        if not self.healEvent:
            self.healEvent=Event(self,'Healing',healingDelay,self.healAll)
    def healAll(self):
        self.healEvent=None
        self.damage=0
    def gainHealth(self,amount):
        self.damage=max(self.damage-amount,0)
        if self.damage==0 and self.healEvent:
            self.healEvent.cancel()
            self.healEvent=None
    def die(self):
        if self.healEvent!=None:
            self.healEvent.cancel()
            self.healEvent=None
        if self.attackEvent!=None:
            self.attackEvent.cancel()
            self.attackEvent=None
        if self.blockEvent!=None:
            self.blockEvent.cancel()
            self.blockEvent=None
        self.block=None
        self.attack=None
            
        self.dead=1
        if self.dyingEvent==None:
            self.dyingEvent=Event(self,'Dying',dyingDelay,self.goToGraveyard)
    def goToGraveyard(self):
        self.destroy()
        
        

class NonTappingCreature(Creature):
    def setTarget(self,attack):
        if self.attack!=None: return
        if attack==None: return
        if not isinstance(attack,Player): return
        if attack==self.owner: return
        self.setNoneditable('attack')
        self.attack=attack
        self.attackEvent=Event(self,'Attacking',attackDelay,self.doneAttack)
    def doneAttack(self):
        self.attack.doDamage(self.power,self)
        self.attack=None
        Event(self,'Recovering',untapDelay,self.recover)
    def recover(self):
        self.setEditable('attack',self.setTarget,())
    def setBlock(self,block):
        if self.tapped: return
        if block==None: return
        if not isinstance(block,Creature): return
        if block.attack==None: return
        if block.flying and not self.flying: return
        self.setNoneditable('block')
        self.block=block
        self.blockEvent=Event(self,'Blocking',blockDelay,self.doneBlock)
    def doneBlock(self):
        if self.block.owner!=None and not self.block.dead:
            bp=self.block.power
            sp=self.power
            if self.firstStrike and not self.block.firstStrike:
                self.block.doDamage(sp,self)
                if not self.block.dead:
                    self.doDamage(bp,self.block)
            elif self.block.firstStrike and not self.firstStrike:
                self.doDamage(bp,self)
                if not self.dead:
                    self.block.doDamage(sp,self)
            else:
                
                self.block.doDamage(sp,self)
                self.doDamage(bp,self.block)
        self.block=None
        self.setEditable('block',self.setTarget,())
    
class SavannahLions(Creature):
    cost='W'
    power=2
    toughness=1
    
class SerraAngel(NonTappingCreature):
    cost='3WW'
    power=4
    toughness=4
    flying=1

class ScatheZombies(Creature):
    cost='2B'
    power=2
    toughness=2

class AirElemental(Creature):
    cost='3UU'
    power=4
    toughness=4

class ProdigalSorcerer(Creature):
    cost='2U'
    power=1
    toughness=1
    def doneCast(self):
        Creature.doneCast(self)
        TargettedAbility(self,'Do 1 damage to target',self.tim,tap=1)
    def canSetTarget(self,target):
        return isinstance(target,Damageable)
    def tim(self):
        self.target.doDamage(1,self)
    
class WhiteKnight(Creature):
    cost='WW'
    firstStrike=1
    power=2
    toughness=2
    protection='b'

class BlackKnight(Creature):
    cost='BB'
    firstStrike=1
    power=2
    toughness=2
    protection='w'
    
class TundraWolves(Creature):
    cost='W'
    firstStrike=1
    power=1
    toughness=1
    
