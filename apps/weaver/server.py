
import things
import eventTimer

import mtg




     
class Server:
    def __init__(self,config):
        self.thingToClient={}
        self.timer=eventTimer.Timer()
        self.playerClass=mtg.MtGPlayer
        
    def onJoin(self,client):
        client.thing=self.playerClass(self,client)
        self.thingToClient[client.thing]=client
        for t in self.thingToClient.keys():
            t.sendInfo(client)
            for c in t._owned:
                c.sendInfo(client)
            
    def onDisconnect(self,client):
        if len(self.clients)==0:
            self.adminServer.stopApp(self)
            self.timer.stopTimer()
        
    def setName(self,client,name):
        if name.strip()=='': name='Player'
        client.thing.name=name

    def doAction(self,client,actionid):
        action=things.getFromId(actionid)
        if action!=None and isinstance(action,things.Action):
            if action.thing.isOwnedBy(client):
                action.trigger()

    def requestInfo(self,client,thingid):
        thing=things.getFromId(thingid)
        if thing!=None:
            thing.sendInfo(client)

    def trySetValue(self,client,thingid,key,value):
        thing=things.getFromId(thingid)
        if thing!=None and hasattr(thing,key) and key[0]!='_':
            if type(value)==type(()) and len(value)==1:
                value=things.getFromId(value[0])
            oldVal=getattr(thing,key)
            if type(value)==type(oldVal) or (oldVal==None and isinstance(value,things.Thing)):
                if thing.isOwnedBy(client):
                    thing.trySetValue(key,value)
                
        

                
