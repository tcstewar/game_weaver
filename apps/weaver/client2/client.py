

gameName='R-t M:tG'
import simpleCS

import gui
import thing

class Client:
    def shutdown(self):
        simpleCS.stopClient(self)
        self.frame.dispose()
        self.frame=None
        
    def setId(self,id):
        self.frame=gui.MainFrame(self,gameName)
        self.thingStore=thing.ThingStore(self.frame,self.server)
        t=self.thingStore.get(id)
        self.frame.setSelf(t)
        self.server.setName(self.adminName)

    def destroy(self,id):
        t=self.thingStore.get(id)
        self.thingStore.destroy(t)
        

        
    def setAttr(self,id,key,value):
#        print id,key,value
        t=self.thingStore.get(id)
        if type(value)==type(()) and len(value)==1: value=self.thingStore.get(value[0])
        if not t.has('name'):
            self.server.requestInfo(id)
            
        t.set(key,value)
        if key=='isPlayer':
            self.frame.initPlayer(t)
            self.frame.calcTitle()
        if key=='owner':
            self.frame.field.initThing(t)
        if key=='name' and t.has('isPlayer') and t.get('isPlayer'):
            self.frame.calcTitle()
    def setEditable(self,id,key,options):
        t=self.thingStore.get(id)
        t.setEditable(key,options)
    def setNoneditable(self,id,key):
        t=self.thingStore.get(id)
        t.setNoneditable(key)

        
    def newEvent(self,id,index,name,delay):
        thing=self.thingStore.get(id)
        thing.newEvent(index,name,delay)
    def endEvent(self,id,index):
        thing=self.thingStore.get(id)
        thing.endEvent(index)
    def restartEvent(self,id,index):
        thing=self.thingStore.get(id)
        thing.restartEvent(index)
        
    def setAction(self,thingid,actionid,name):
        thing=self.thingStore.get(thingid)
        thing.setAction(actionid,name)
    def clearAction(self,thingid,actionid):
        thing=self.thingStore.get(thingid)
        thing.clearAction(actionid)
    
