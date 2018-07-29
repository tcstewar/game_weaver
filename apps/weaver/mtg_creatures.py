from mtg import *
        
class Creature(Spell,Damageable):
    flying=0
    reach = False
    dead=0
    protection=''
    firstStrike=0
    defender = False
    banding = False   # TODO: implement this
    swampwalk = False  # TODO: implement this
    forestwalk = False # TODO: implement this

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
        if not self.defender:
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
        if block.flying and not (self.flying or self.reach): return
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
        if not self.defender:
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
    flying=True

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
    
class BenalishHero(Creature):
    cost = 'W'
    banding = True
    power = 1
    toughness = 1

class BirdsOfParadise(Creature):
    cost = 'G'
    flying = True
    power = 0
    toughness = 1
    def doneCast(self):
        Creature.doneCast(self)
        for c in 'WRBUG':
            Ability(self,'Get %s mana'%c,self.doIt, args=(c), delay=0.1, tap=1)
    def doIt(self, c):
        self.owner.addMana(c)

class BogWraith(Creature):
    cost = '3B'
    power = 3
    toughness = 3
    swampwalk = True

#class ClockworkBeast
#class Clone

class Cockatrice(Creature):
    cost = '3GG'
    power = 2
    toughness = 4
    flying = True

    def doneCast(self):
        Creature.doneCast(self)
        self.addOverride(Creature.doneBlock, self.kill_blocker)

    def doneBlock(self):
        block = self.block
        Creature.doneBlock(self)
        block.destroy()

    def kill_blocker(self, card, base_func):
        if card.block is self:
            base_func(card)
            card.destroy()
        else:
            base_func(card)

class CrawWurm(Creature):
    cost = '4GG'
    power = 6
    toughness = 4

#DemonicHordes

class DragonWhelp(Creature):
    cost = '2RR'
    power = 2
    toughness = 3
    flying = True
    def doneCast(self):
        Creature.doneCast(self)
        self.boost_counter = 0
        self.reset_event = None
        Ability(self, 'Gain +1/+0', self.boost, delay=0.1, manaCost='R')
    def boost(self):
        self.boost_counter += 1
        self.power += 1
        if self.reset_event is None:
            self.reset_event = Event(self, 'Reset', attackDelay*2, self.reset)
    def reset(self):
        if self.boost_counter >= 4:
            self.die()
        self.power -= self.boost_counter
        self.boost_counter = 0



#DragonWhelp
#DrudgeSkeletons
#DwarvenDemolitionTeam
#DwarvenWarriors

class EarthElemental(Creature):
    cost = '3RR'
    power = 4
    toughness = 5

class ElvishArchers(Creature):
    cost = '1G'
    power = 2
    toughness = 1
    firstStrike = True

class FireElemental(Creature):
    cost = '3RR'
    power = 5
    toughness = 4

#ForceOfNature
#FrozenShade

class Fungusaur(Creature):
    cost = '3G'
    power = 2
    toughness = 2

    def doDamage(self, amount, source):
        if not self.dead:
            self.power += 1
            self.toughness += 1

#GaeasLiege

class GiantSpider(Creature):
    cost = '3G'
    power = 2
    toughness = 4
    reach = True

class GrayOgre(Creature):
    cost = '2R'
    power = 2
    toughness = 2

class GrizzlyBears(Creature):
    cost = '1G'
    power = 2
    toughness = 2

class HillGiant(Creature):
    cost = '3R'
    power = 3
    toughness = 3

class HurloonMinotaur(Creature):
    cost = '1RR'
    power = 2
    toughness = 3

class IronclawOrcs(Creature):
    cost = '1R'
    power = 2
    toughness = 2

    def setBlock(self, block):
        if block is not None and block.power >= 2:
            return
        return Creature.setBlock(self, block)

class IronrootTreefolk(Creature):
    cost = '4G'
    power = 3
    toughness = 5

class LlanowarElves(Creature):
    cost = 'G'
    power = 1
    toughness = 1

    def doneCast(self):
        Creature.doneCast(self)
        Ability(self,'Get G mana', lambda: self.owner.addMana('G'), delay=0.1, tap=1)

class MahamotiDjinn(Creature):
    cost = '4UU'
    power = 5
    toughness = 6
    flying = True

class MerfolkOfThePearlTrident(Creature):
    cost = 'U'
    power = 1
    toughness = 1

class MesaPegasus(Creature):
    cost = '1W'
    power = 1
    toughness = 1
    flying = True

class MonsGoblinRaiders(Creature):
    cost = 'R'
    power = 1
    toughness = 1

class ObsianusGolem(Creature):
    cost = '6'
    power = 4
    toughness = 6

class OrcishArtillery(Creature):
    cost = '1RR'
    power = 1
    toughness = 3

    def doneCast(self):
        Creature.doneCast(self)
        TargettedAbility(self,'Do 2 damage to target, 3 to you',self.tim,tap=1)
    def canSetTarget(self,target):
        return isinstance(target,Damageable)
    def tim(self):
        self.target.doDamage(2,self)
        self.owner.doDamage(3, self)

class PearledUnicorn(Creature):
    cost = '2W'
    power = 2
    toughness = 2

class PhantomMonster(Creature):
    cost = '3U'
    power = 3
    toughness = 3
    flying = True

class RocOfKherRidges(Creature):
    cost = '3R'
    power = 3
    toughness = 3
    flying = True

class ScrybSprites(Creature):
    cost = 'G'
    power = 1
    toughness = 1
    flying = True

class ShanodinDryads(Creature):
    cost = 'G'
    power = 1
    toughness = 1
    forestwalk = True

class ThicketBasilisk(Creature):
    cost = '3GG'
    power = 2
    toughness = 4

    def doneCast(self):
        Creature.doneCast(self)
        self.addOverride(Creature.doneBlock, self.kill_blocker)

    def doneBlock(self):
        block = self.block
        Creature.doneBlock(self)
        block.destroy()

    def kill_blocker(self, card, base_func):
        if card.block is self:
            base_func(card)
            card.destroy()
        else:
            base_func(card)

class TimberWolves(Creature):
    cost = 'G'
    power = 1
    toughness = 1
    banding = True

class VerduranEnchantress(Creature):
    cost = '1GG'
    power = 0
    toughness = 2
    def doneCast(self):
        self.addOverride(Enchantment.cast, self.handle_draw)
    def handle_draw(self):
        self.owner.doDrawCard()

class WallOfAir(Creature):
    cost = '1UU'
    power = 1
    toughness = 5
    defender = True

class WallOfIce(Creature):
    cost = '2G'
    power = 0
    toughness = 7
    defender = True

class WallOfStone(Creature):
    cost = '1RR'
    power = 0
    toughness = 8
    defender = True

class WallOfSwords(Creature):
    cost = '3W'
    power = 3
    toughness = 5
    defender = True
    flying = True

class WallOfWood(Creature):
    cost = 'G'
    power = 0
    toughness = 3
    defender = True

class WaterElemental(Creature):
    cost='3UU'
    power=5
    toughness=4


