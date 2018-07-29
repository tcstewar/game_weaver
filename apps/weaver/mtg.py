from things import Thing,Player,Action,Event

import random

playerStartHealth=20
playerStartMana=''


untapDelay=30
landDelay=30
manaBurnDelay=15
cardDrawDelay=30
summoningSicknessDelay=20
creatureUntapDelay=20
attackDelay=20
blockDelay=10
castingDelay=20
healingDelay=15
counterDelay=10
configureDelay=15
discardDelay=25
sorceryDelay=30
dyingDelay=10
abilityDelay=15
spellForLifeDelay=10

def set_debug_timing():
    global untapDelay, landDelay, manaBurnDelay, cardDrawDelay, summoningSicknessDelay, creatureUntapDelay, attackDelay, blockDelay, counterDelay, castingDelay

    untapDelay=1
    landDelay=1
    manaBurnDelay=100
    cardDrawDelay=30
    summoningSicknessDelay=1
    creatureUntapDelay=1
    attackDelay=20
    blockDelay=10
    counterDelay=5
    castingDelay=1

class Damageable:
    pass
        
                

class Card(Thing):
    def __init__(self,owner):
        Thing.__init__(self,owner._server)
        if hasattr(self,'name'):
            self.name=self.name
        else:
            n=self.__class__.__name__
            i=1
            while i<len(n):
                if n[i] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    n=n[:i]+' '+n[i:]
                    i+=1
                i+=1
            self.name=n
        if hasattr(self,'color'):
            self.color=self.color
        elif self.cost[-1].lower() in 'rgubw':
            self.color=self.cost[-1].lower()
        else:
            self.color=''
        self.tapped=0
        self._isDoneCasting=0
        self._abilities={}
    def tap(self):
        self.tapped=1
        self.untapEvent=Event(self,'Untapping',untapDelay,self.untap)        
    def untap(self):
        if hasattr(self,'untapEvent'): self.untapEvent.cancel()
        self.tapped=0

class Ability:
    def __init__(self,card,name,func,args=(),secret=0,manaCost='',delay=abilityDelay,tap=0,sacrifice=0):
        self.func=func
        self.args=args
        self.manaCost=manaCost
        self.tap=tap
        self.card=card
        self.name=name
        self.delay=delay
        self.sacrifice=sacrifice
        cost=manaCost
        if tap:
            if cost=='': cost='T'
            else: cost+=',T'
        if sacrifice:
            if cost=='': cost='Sac'
            else: cost+=',Sac'
        self.action=Action(card,'%s:%s'%(cost,name),self.tryAbility,secret=secret)
    def tryAbility(self):
        if self.card.tapped: return
        if getattr(self.card,'dead',0):return
        if self.card.owner.hasMana(self.manaCost):
            self.card.owner.drainMana(self.manaCost)
            if self.tap:
                self.card.tap()
            self.start()
    def start(self):
        Event(self.card,self.name,self.delay,self.doIt)
    def doIt(self):
        apply(self.func,self.args)
        if self.sacrifice: self.card.destroy()
    def remove(self):
        self.action.remove()

class TargettedAbility(Ability):
    def start(self):
        self.card.target=None
        self.card.setEditable('target',self.trySetTarget,())
        self.setupEvent=Event(self.card,'Configure',configureDelay,self.timeOut)
    def doneSetup(self):
        self.setupEvent.cancel()
    def timeOut(self):
        self.card.setNoneditable('target')
    def trySetTarget(self,target):
        if target==None: return
        if target==self: return
        if self.card.canSetTarget(target):
            self.setTarget(target)
    def setTarget(self,target):
        self.card.setNoneditable('target')
        self.card.target=target
        self.doneSetup()
        Ability.start(self)        
        
    
            
    
    
#Card._isDoneCasting=0
class Configurable(Card):
    def canCast(self,player):
        return player.hasMana(self.cost)
    def cast(self,player):
        player.drainMana(self.cost)
        self.owner=player
        self.setupEvent=Event(self,'Configure Spell',configureDelay,self.timeOut)
    def doneSetup(self):
        self.setupEvent.cancel()
    def timeOut(self):
        self.destroy()

class Targetted(Configurable):
    def cast(self,player):
        Configurable.cast(self,player)
        self.target=None
        self.setEditable('target',self.trySetTarget,())
    def trySetTarget(self,target):
        if target==None: return
        if target==self: return
        if self.canSetTarget(target):
            self.setTarget(target)
    def setTarget(self,target):
        self.setNoneditable('target')
        name,delay=self.getCastEventInfo()
        Event(self,name,delay,self.doneCast)
        self.target=target
        self.doneSetup()
    def getCastEventInfo(self):
        return 'Casting',castingDelay
    def canSetTarget(self,target):
        return 0
    def doneCast(self):
        self._isDoneCasting=1
        self.onCast()


class TargettedPumpable(Targetted):
    def cast(self,player):
        Targetted.cast(self,player)
        self.amount=0
        Ability(self,'Pump up',self.doPump,delay=0.1,manaCost='1')
    def doPump(self):
        self.amount+=1
    
    
class Spell(Card):
    _castDelay=castingDelay
    def canCast(self,player):
        return player.hasMana(self.cost)
    def cast(self,player):
        player.drainMana(self.cost)
        self.owner=player
        Event(self,'Casting',self._castDelay,self.doneSpellCast)
    def doneSpellCast(self):
        self._isDoneCasting=1
        self.doneCast()
    
class Enchantment(Spell):
    pass



        
class MtGPlayer(Player,Damageable):
    _isDoneCasting=1
    maxCards=7
    started=False
    def initPlayer(self):
        self.life=playerStartHealth
        for k in dir(mtg_deck):
            v = getattr(mtg_deck, k)
            if isinstance(v, dict) and not k.startswith('_'):
                Action(self, k, lambda k=k: self.set_deck(k), secret=1)

    def set_deck(self, deck_name):
        self._deck=Deck(self,deck_name)
        for k, v in self._actions.items():
            v.remove()
        Action(self, 'Start Game', self.start, args=(False,))
        Action(self, 'Start Game (debug mode)', self.start, args=(True,))

    def start(self, debug):
        for k, v in self._actions.items():
            v.remove()
        self.started = True
        for p in self.getAllInPlay(MtGPlayer):
            if not p.started:
                Event(self, 'waiting for others to start', 0.01, self.start, args=(debug,))
                return
        self._hand=Hand(self)
        self._hasCastLand=0
        self._mana=Mana(self)
        self._isManaBurning=0
        self.discardTimer=None
        for i in range(8):
            self.doDrawCard()
        self.drawCardEvent=Event(self,'Drawing Next Card',cardDrawDelay,self.doDrawCard,repeat=1)

        if debug:
            Action(self, 'Draw card', self.doDrawCard)
            for m in 'BRGWU':
                Action(self, 'Gain %s mana'%m, self.addMana, args=(m,))
            set_debug_timing()
    def addMana(self,mana):
        self._mana.add(mana)
    def doDamage(self,amount,source):
        self.life-=amount
        if self.life<=0:
            self.destroy()
    def gainHealth(self,amount):
        self.life+=amount
    def hasMana(self,mana):
        return self._mana.has(mana)
    def drainMana(self,mana):
        self._mana.drain(mana)
    def doDrawCard(self):
        self._hand.addCard(self._deck.draw())
        self.checkCardCount()
    def checkCardCount(self):
        if self._hand.count()<=self.maxCards and self.discardTimer!=None:
            self.discardTimer.cancel()
            self.discardTimer=None
            self.setNoneditable('discard')
        if self._hand.count()>self.maxCards and self.discardTimer==None:
            self.discardTimer=Event(self,'Forced Discard',discardDelay,self.forceDiscard)
            cardNames=['']
            for c in self._hand.cards.values():
                if c.name not in cardNames:
                    cardNames.append(c.name)
            cardNames.sort()
            self.discard=''
            self.setEditable('discard',self.setDiscard,cardNames)
    def setDiscard(self,cardName):
        if self.discardTimer==None: return
        for c in self._hand.cards.values():
            if c.name==cardName:
                self._hand.discard(c)
                break
        self.checkCardCount()
    def forceDiscard(self):
        self.discardTimer=None
        while self._hand.count()>self.maxCards:
            self._hand.discard(random.choice(self._hand.cards.values()))
            
            
        
    def setCastLand(self):
        if not self._hasCastLand:
            self._hasCastLand=1
            Event(self,'Land Delay',landDelay,self.resetCastLand)
    def resetCastLand(self):
        self._hasCastLand=0
    def startManaBurn(self):
        self.manaBurn=Event(self,'Mana Burn',manaBurnDelay,self.doManaBurn)
        self._isManaBurning=1
    def stopManaBurn(self):
        if self._isManaBurning:
            self.manaBurn.cancel()
            self._isManaBurning=0
    def doManaBurn(self):
        count=self._mana.count()
        self._mana.removeAll()
        self._isManaBurning=0
        self.doDamage(count, None)
        
        
        
        

class Mana:
    def __init__(self,player):
        self.player=player
        player.mana=playerStartMana
    def count(self,color=None):
        if color!=None:
            return self.player.mana.count(color.lower())
        else:
            return len(self.player.mana)
    def add(self,mana):
        if self.player.mana=='':
            self.player.startManaBurn()
        self.player.mana+=mana.lower()
    def has(self,mana):
        pm=self.player.mana
        a=''
        c=0
        for m in mana.lower():
            if m in '1234567890':
                a+=m
            else:
                if len(a)>0:
                    c+=int(a)
                    a=''
                i=pm.find(m)
                if i==-1: return 0
                pm=pm[:i]+pm[i+1:]
        if len(a)>0:
            c+=int(a)
        if c>len(pm):
            return 0
        return 1
    def drain(self,mana):
        pm=self.player.mana
        a=''
        c=0
        for m in mana.lower():
            if m in '1234567890':
                a+=m
            else:
                if len(a)>0:
                    c+=int(a)
                    a=''
                i=pm.find(m)
                if i==-1:
                    print "Could not drain %s from %s" % (mana,self.player.mana)
                else:
                    pm=pm[:i]+pm[i+1:]
        if len(a)>0:
            c+=int(a)
        if c>len(pm):
            print "Could not drain %s from %s" % (mana,self.player.mana)
            pm=''
        else:
            pm=pm[c:]
        self.player.mana=pm
        if pm=='': self.player.stopManaBurn()
        
    def removeAll(self):
        self.player.mana=''
        self.player.stopManaBurn()
        

class Hand:
    def __init__(self,player):
        self.cards={}
        self.actions={}
        self.counter=0
        self.player=player
    def count(self):
        return len(self.cards)
    def addCard(self,card):
        if card==None: return
        i=self.counter
        self.counter+=1
        if card.cost=='':
            verb='Play '
        else:
            verb='%s:' % card.cost
        a=Action(self.player,'%s%s'%(verb,card.name),lambda i=i,self=self: self.cast(i),secret=1)
        self.cards[i]=card
        self.actions[i]=a
    def cast(self,i):
        if i in self.cards.keys():
            c=self.cards[i]
            if c.canCast(self.player):
                a=self.actions[i]
                a.remove()
                c.cast(self.player)
                del self.cards[i]
        self.player.checkCardCount()
    def discard(self,card):
        for i,c in self.cards.items():
            if c==card:
                a=self.actions[i]
                a.remove()
                del self.cards[i]
                break
                
            
        
        
        
        

import mtg_deck            
import random
class Deck:
    def __init__(self,player,deck):
        deck=getattr(mtg_deck,deck)
        self.player=player
        self.deck=[]
        for k,v in deck.items():
            for i in range(v):
                self.deck.append(k)
        random.shuffle(self.deck)
        self.player.deck=len(self.deck)
    def draw(self):
        if len(self.deck)==0:
            self.player.destroy()
            return
        Class=self.deck.pop(0)
        self.player.deck=len(self.deck)
        return Class(self.player)
    def drawClass(self,klass):
        for c in self.deck[:]:
            if c==klass:
                self.deck.remove(c)
                self.player.deck=len(self.deck)
                return klass(self.player)
        return None
    
        
