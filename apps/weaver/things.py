import override
import aoverride

allIds={}
def getFromId(id):
    return allIds.get(id,None)

class Action:
    def __init__(self,thing,name,func,args=(),secret=0):
        allIds[id(self)]=self
        self.thing=thing
        self.func=override.makeSafeReference(func)
        self.args=args
        self.secret=secret
        self.thing._actions[id(self)]=self

        self.setName(name)

    def setName(self,name):
        self.name=name
        for c in self.thing._server.clients:
            if not self.secret or self.thing.isOwnedBy(c):
                c.setAction(id(self.thing),id(self),name)
            
    def trigger(self):
        apply(self.func,self.args)
    def remove(self):
        if self.thing._server==None: return
        for c in self.thing._server.clients:
            if not self.secret or self.thing.isOwnedBy(c):
                c.clearAction(id(self.thing),id(self))
        if id(self) in self.thing._actions.keys():
            del self.thing._actions[id(self)]
        del allIds[id(self)]
    def sendAction(self,client):
        if not self.secret or self.thing.isOwnedBy(client):
            client.setAction(id(self.thing),id(self),self.name)
    
        

class Event:
    def __init__(self,thing,name,delay,func,args=(),repeat=0):
        self.thing=thing
        self.name=name
        self.func=override.makeSafeReference(func)
        self.args=args
        self.delay=delay
        self.repeat=repeat
        self.thing._events[id(self)]=self
        if self.thing._server!=None:
            self.thing._server.allClients.newEvent(id(thing),id(self),name,delay)
            self.thing._server.timer.addEvent(delay,self.trigger)
        self.cancelled=0
    def sendEvent(self,client):
        client.newEvent(id(self.thing),id(self),self.name,self.delay)
    def trigger(self):
        if self.cancelled: return
        if self.thing._server==None: return
        apply(self.func,self.args)
        if self.thing._server==None: return
        if self.repeat:
            self.thing._server.allClients.restartEvent(id(self.thing),id(self))
            self.thing._server.timer.addEvent(self.delay,self.trigger)
        else:
            self.thing._server.allClients.endEvent(id(self.thing),id(self))
            if id(self) in self.thing._events.keys():
                del self.thing._events[id(self)]
    def cancel(self):
        if self.thing._server==None: return
        self.thing._server.allClients.endEvent(id(self.thing),id(self))
        del self.thing._events[id(self)]
        self.cancelled=1
        

def getAllBaseClasses(klass):
    b=[klass]
    i=0
    while i<len(b):
        c=b[i]
        for bb in c.__bases__:
            if issubclass(bb,Thing):
                b.append(bb)
        i+=1
    return b
    

class Thing(aoverride.AttributeOverrideable):
#class Thing:
    _allList={}
    def __init__(self,server):
        aoverride.AttributeOverrideable.__init__(self)
        allIds[id(self)]=self
        self._server=server
        self._events={}
        self._actions={}
        self._editable={}
        self._owned=[]
        self._overrides=[]
        self._attrOverrides=[]
        self._classAttrOverrides=[]

        for c in getAllBaseClasses(self.__class__):
            if not Thing._allList.has_key(c):
                Thing._allList[c]=[]
            Thing._allList[c].append(self)
        
        self.init()
        
    def init(self):
        pass
    def getAllInPlay(self,klass):
        if issubclass(klass,Player):
            return Thing._allList.get(klass,[])
        else:        
            return [t for t in Thing._allList.get(klass,[]) if getattr(t,'owner',None)]

    def __setattr__(self,key,value):
        if key=='owner':
            if value!=None and not isinstance(value,Thing): raise AttributeError('Owners must be Thing objects')
            oldOwner=getattr(self,'owner',None)
            if oldOwner!=None:
                if self in oldOwner._owned: oldOwner._owned.remove(self)
            if value!=None: value._owned.append(self)
#        if key[0]!='_':
#                if self._server!=None:
#                    self._server.allClients.setAttr(id(self),key,v)
        aoverride.AttributeOverrideable.__setattr__(self,key,value)
        if key[0]!='_':
            self.updateServerValue(key)
#        self.__dict__[key]=value
    def updateServerValue(self,key):
        if self._server!=None:
#            try:
                v=getattr(self,key)
                if key=='damage' and hasattr(self,'toughness'):
                    if v>=self.toughness: self.die()
                elif key=='toughness' and hasattr(self,'damage'):
                    if v<=self.damage: self.die()
                if v==None or isinstance(v,Thing) or type(v)==type('') or type(v)==type(1) or type(v)==type(1.1):
                  if isinstance(v,Thing):
                      v=(id(v),)
                  self._server.allClients.setAttr(id(self),key,v)
#            except AttributeError:
#                pass
        else:
            'could not send value for %s since server==None' % key

    def addClassAttrOverride(self,klass,key,func):
        self._classAttrOverrides.append((klass,key,func))
        aoverride.addClassAttributeOverride(klass,key,func)
        for t in self.getAllInPlay(klass):
            t.updateServerValue(key)
            
    def removeClassAttrOverride(self,klass,key,func):
        self._classAttrOverrides.remove((klass,key,func))
        aoverride.removeClassAttributeOverride(klass,key,func)
        for t in self.getAllInPlay(klass):
            t.updateServerValue(key)
        
        
    def addAttrOverride(self,target,key,func):
        if not isinstance(target,aoverride.AttributeOverrideable):
            self.addClassAttrOverride(target,key,func)
            return
        aoverride.AttributeOverrideable.addAttrOverride(target,key,func)
        self._attrOverrides.append((target,key,func))
        target.updateServerValue(key)
    def removeAttrOverride(self,target,key,func):
        if not isinstance(target,aoverride.AttributeOverrideable):
            self.removeClassAttrOverride(target,key,func)
            return
        aoverride.AttributeOverrideable.removeAttrOverride(target,key,func)
        self._attrOverrides.remove((target,key,func))
        target.updateServerValue(key)
    def isOwnedBy(self,client):
        x=[self]
        while len(x)>0:
            t=x.pop(0)
            if hasattr(t,'_client') and t._client==client:
                return 1
            elif hasattr(t,'owner'):
                o=t.owner
                if o==client: return 1
                if type(o) in (type(()),type([])):
                    x.extend(o)
                else:
                    x.append(o)
        return 0
    def sendInfo(self,client):
        for k in self._attr.keys():
            if k[0]!='_':
                v=getattr(self,k)
                if isinstance(v,Action): continue
                if isinstance(v,Event): continue
                if isinstance(v,Thing):
                    v=(id(v),)
                client.setAttr(id(self),k,v)
        for a in self._actions.values():
            a.sendAction(client)
        for e in self._events.values():
            e.sendEvent(client)
    def setEditable(self,key,func,options):
        if key not in self._editable.keys():
          if self._server!=None:
            for c in self._server.clients:
                if self.isOwnedBy(c):
                    c.setEditable(id(self),key,options)
        self._editable[key]=func
    def setNoneditable(self,key):
        if key in self._editable.keys():
          if self._server!=None:  
            for c in self._server.clients:
                if self.isOwnedBy(c):
                    c.setNoneditable(id(self),key)
            del self._editable[key]
            
    def trySetValue(self,key,value):
        if key in self._editable.keys():
            self._editable[key](value)

    def destroy(self):
        for c in getAllBaseClasses(self.__class__):
            if c in Thing._allList[c]:
                Thing._allList[c].remove(self)
        while len(self._overrides)>0:
            b,f=self._overrides.pop()
            override.remove(b,f)
        while len(self._attrOverrides)>0:
            t,k,f=self._attrOverrides[0]
            self.removeAttrOverride(t,k,f)
        while len(self._classAttrOverrides)>0:
            c,k,f=self._classAttrOverrides[0]
            self.removeClassAttrOverride(c,k,f)
        if id(self) not in allIds.keys(): return
        del allIds[id(self)]
        for o in self._owned[:]:
            o.destroy()
        self._server.allClients.destroy(id(self))
        self._server=None
        for a in self._actions.values(): a.remove()
        for e in self._events.values(): e.cancel()
        self._editable.clear()
        if hasattr(self,'owner'):
            self.owner._owned.remove(self)
            self.owner=None



    def addOverride(self,base,func):
        self._overrides.append((base,func))
        override.add(base,func)
            

      
        
class Player(Thing):
    def __init__(self,server,client):
        Thing.__init__(self,server)
        self._client=client
        self._client.setId(id(self))
        self.isPlayer=1
        self.name='Player'
        self.initPlayer()
    def initPlayer(self):
        pass


        
        
        
    
