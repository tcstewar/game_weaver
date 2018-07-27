from javax import swing
from java import awt

from thing import Thing

class CardPanel(swing.JPanel):
    def __init__(self,server):
        swing.JPanel.__init__(self)
        self.server=server
        self.layout=awt.BorderLayout()
        self.actionBox=swing.Box.createVerticalBox()
        self.eventBox=swing.Box.createVerticalBox()
        self.attrBox=swing.Box.createVerticalBox()
        self.attr={}
        self.attrButtons={}

        self.choosingColor=awt.Color(0,255,0)

        self.add(self.attrBox,'North')
        self.add(self.actionBox)
        self.add(self.eventBox,'South')
        self.thing=None
        self.defaultBorder=swing.BorderFactory.createTitledBorder('[Selected Card]')
        self.border=self.defaultBorder
        self.field=None
        self.chooseButton=None

    def thingChangedAction(self,id=None):
        self.actionBox.removeAll()
        if self.thing!=None:
            list=self.thing.actions.items()
            list.sort(lambda a,b: cmp(a[1],b[1]))
            for id,name in list:
                b=swing.JButton(name)
                b.actionPerformed=lambda x,aid=id,server=self.server: server.doAction(aid)
                p=swing.JPanel(layout=awt.BorderLayout())
                p.add(b)
                self.actionBox.add(p)
        self.validate()
                
    def thingChangedEvent(self,id=None):
        self.eventBox.removeAll()
        if self.thing!=None:
            for e in self.thing.events.values():
                self.eventBox.add(e)
        self.validate()
                

    def thingChangedAttr(self,key=None,val=None):
        if self.thing!=None:
            for k in self.thing.getKeys():
                if k=='isPlayer': continue
                if k=='name':
                    if key==None or key==k:
                        self.border=swing.BorderFactory.createTitledBorder(self.thing.get(k))
                    continue
                if k in self.attrs.keys():
                    if k!=key:
                        continue
                    else:
                        p=self.attrs[k]
                        p.removeAll()
                else:
                    p=swing.JPanel(layout=awt.GridLayout(1,2))
                    self.attrBox.add(p)
                    self.attrs[k]=p

                                
                v=self.thing.get(k)

                if k in self.thing.editable.keys():
                    if isinstance(v,Thing):
                        c=swing.JButton(v.get('name'))
                        c.actionPerformed=lambda event,key=k,self=self: self.startChoosingTarget(key)
                        self.attrButtons[k]=c
                        l=swing.JLabel(k)
                        p.add(l)
                        p.add(c)
                    elif v==None and len(self.thing.editable[k])==0:
                        c=swing.JButton('Select %s' % k)
                        if v!=None:
                            c.text=v.name
                        c.actionPerformed=lambda event,key=k,self=self: self.startChoosingTarget(key)
                        self.attrButtons[k]=c
                        p.layout=awt.GridLayout(1,1)
                        p.add(c)
                    else:
                        c=swing.JComboBox()
                        for o in self.thing.editable[k]:
                            c.addItem(o)
                        c.selectedItem=v
                        c.itemStateChanged=lambda event,key=k,self=self: self.onStateChange(event,key)
                        l=swing.JLabel(k)
                        p.add(l)
                        p.add(c)
                else:
                    if isinstance(v,Thing):
                        v=v.get('name')
                    if type(v)==type(1):
                        v="%d" %v
                    if type(v)==type(1.0):
                        v="%3.2f" % v
                    c=swing.JLabel(v)
                    l=swing.JLabel(k)
                    p.add(l)
                    p.add(c)
        self.validate()
    def onStateChange(self,event,key):
        if event.stateChange==awt.event.ItemEvent.SELECTED:
            old=self.thing.get(key)
            new=event.source.selectedItem
            event.source.selectedItem=old
            self.server.trySetValue(self.thing.id,key,new)
    def startChoosingTarget(self,key):
        if self.chooseButton!=None: self.chooseButton.background=self.oldBackground
        if key in self.attrButtons.keys():
            self.chooseButton=self.attrButtons[key]
            self.oldBackground=self.chooseButton.background
            self.chooseButton.background=self.choosingColor
            if self.field!=None:
                self.field.startChoosingTarget(self.thing,key)
    def stopChoosing(self):
        self.chooseButton.background=self.oldBackground
        
            
        
        
        

    def setThing(self,thing):
        if thing==self.thing: return
        self.attrs={}
        self.attrBox.removeAll()
        if self.thing!=None:
            self.thing.removeCardDisplayListener(self)
        self.thing=thing
        if thing!=None:
            self.thing.addCardDisplayListener(self)
        else:
            self.border=self.defaultBorder
        self.thingChangedAttr()
        self.thingChangedAction()
        self.thingChangedEvent()
    
        
        
                                                   
        
                        
