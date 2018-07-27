from javax import swing
from java import awt

import time
import thread

class EventBarUpdater:
    def __init__(self):
        self.stop=1
        self.bars=[]
        self.timeStep=0.1
        self.barScale=10000
    def add(self,bar):
        self.bars.append(bar)
        if self.stop:
            thread.start_new_thread(self.start,())
    def makeBar(self,delay):
        c=swing.JProgressBar(0,int(delay*self.barScale))
        self.add(c)
        return c
        
    def remove(self,bar):
        self.bars.remove(bar)
    def start(self):
        self.stop=0
        lastTime=time.time()
        while not self.stop and len(self.bars)>0:
            time.sleep(self.timeStep)
            now=time.time()
            delay=now-lastTime
            lastTime=now
            for b in self.bars: b.value+=int(delay*self.barScale)
        self.stop=1
        
        

class ThingAttrTable(swing.JTable,swing.table.TableCellRenderer):
    def __init__(self,model,client):
        swing.JTable.__init__(self,model)
        self.getColumnModel().getColumn(1).setCellEditor(swing.DefaultCellEditor(swing.JComboBox(font=self.font)))
        self.defRenderer=swing.table.DefaultTableCellRenderer()
        self.getColumnModel().getColumn(1).setCellRenderer(self)
        self.choosing=None

        self.normalBackground=awt.Color(255,255,255)
        self.normalForeground=awt.Color(0,0,0)
        self.editableBackground=awt.Color(0,255,0)
        self.editableForeground=awt.Color(0,0,0)
        self.choosingForeground=awt.Color(0,255,0)
        self.choosingBackground=awt.Color(255,0,0)
        
        self.client=client
        
        
    def prepareEditor(self,editor,row,col):
        k=self.model.keys[row]
        if k in self.model.editable.keys():
            c=editor.component
            c.removeAllItems()
            if self.model.editable[k]==():
                self.choosing=(row,col)
                self.client.setCurrentChooser(self,k)
                return
            for k in self.model.editable[k]:
                c.addItem(k)
        return swing.JTable.prepareEditor(self,editor,row,col)
    def getTableCellRendererComponent(self,table,value,isSelected,hasFocus,row,col):
        c=self.defRenderer.getTableCellRendererComponent(table,value,isSelected,hasFocus,row,col)
        if self.model.isCellEditable(row,1):
            if self.choosing==(row,col):
                c.background=self.choosingBackground
                c.foreground=self.choosingForeground
                c.text='Select Target'
            else:
                c.background=self.editableBackground
                c.foreground=self.editableForeground
        else:
                c.background=self.normalBackground
                c.foreground=self.normalForeground
        return c
        

   

class ThingAttrModel(swing.table.AbstractTableModel):
    def __init__(self,thing):
        self.attr={}
        self.keys=[]
        self.thing=thing
        self.editable={}
    def getColumnName(self,col): return ['Attribute','Value'][col]
    def getRowCount(self): return len(self.keys)
    def getColumnCount(self): return 2
    def getValueAt(self,row,col):
        if col==0: return self.keys[row]
        else:
            v=self.attr[self.keys[row]]
            if isinstance(v,Frame):
                v=v.getAttr('name')
            return v
    def get(self,key):
        return self.attr.get(key,None)
    def set(self,key,value):
        self.attr[key]=value
        if key not in self.keys and key!='name':
            self.keys.append(key)
        self.keys.sort()
        self.fireTableDataChanged()
    def isCellEditable(self,row,col):
        if col==1 and self.keys[row] in self.editable.keys(): return 1
        return 0

    def setEditable(self,key,options):
        self.editable[key]=options
    def setNoneditable(self,key):
        if key in self.editable.keys():
            del self.editable[key]
    def setValueAt(self,value,row,col):
        k=self.keys[row]
        if col==1 and k in self.editable.keys():
            if type(self.get(k))==type(1):
                value=int(value)
            if type(self.get(k))==type(0.0):
                value=float(value)
            self.thing.client.server.trySetValue(self.thing.id,self.keys[row],value)
        
        
    

               

class Frame:
    def __init__(self,id,client):
        self.id=id
        self.client=client
        self.events={}
        self.actions={}

        self.frame=swing.JFrame()
        self.frame.contentPane.layout=awt.BorderLayout()

        self.attr=ThingAttrModel(self)
        self.attrTable=ThingAttrTable(self.attr,client)
        self.attrTable.preferredSize=200,75
#        self.frame.contentPane.add(swing.JScrollPane(self.attrTable))
        self.frame.contentPane.add(self.attrTable)

        self.actionList=swing.Box.createVerticalBox()
        self.actionControls={}
        self.frame.contentPane.add(self.actionList,'North')

        self.eventBox=swing.Box.createVerticalBox()
        self.frame.contentPane.add(self.eventBox,'South')

        self.frame.setDefaultCloseOperation(swing.WindowConstants.DO_NOTHING_ON_CLOSE)
        self.frame.windowClosing=self.clickedOnClose
        self.frame.show()
        self.frame.setSize(awt.Dimension(200,200))
        self.frame.validate()
    def setAttr(self,key,val):
        
        self.attr.set(key,val)
        if key=='name':
            self.setName(val)
        if key=='owner':
            mine=self.isOwnedByMe()
            for b in self.actionControls.values(): b.enabled=mine
    def getAttr(self,key):
        return self.attr.get(key)

    def isOwnedByMe(self):
        x=[self]
        while len(x)>0:
            t=x.pop(0)
            if t.id==self.client.id: return 1
            o=t.getAttr('owner')
            if o!=None:
                if type(o) in (type(()),type([])):
                    x.extend(o)
                else:
                    x.append(o)
        return 0
            
    def setName(self,name):
        self.frame.title=name
        if self.id==self.client.id:
            self.frame.title+=' (You)'
    def newEvent(self,index,name,delay):
        if index in self.events.keys():
            self.events[index].setString(name)
            return
        c=self.client.eventBarUpdater.makeBar(delay)
        c.setStringPainted(1)
        c.setString(name)
        self.eventBox.add(c)
        self.events[index]=c
        self.frame.contentPane.validate()
#        self.frame.pack()
    def endEvent(self,index):
        if index not in self.events.keys(): return
        c=self.events[index]
        self.client.eventBarUpdater.remove(c)
        self.eventBox.remove(c)
        del self.events[index]
        self.frame.contentPane.validate()
#        self.frame.pack()
    def restartEvent(self,index):
        if index not in self.events.keys(): return
        self.events[index].value=0
        
    def setAction(self,actionid,name):
        if actionid in self.actionControls.keys():
            self.actionControls[actionid].text=name
        else:
            b=swing.JButton(name,actionPerformed=lambda e,aid=actionid,server=self.client.server: server.doAction(aid))
            if not self.isOwnedByMe(): b.enabled=0
            self.actionControls[actionid]=b
            p=swing.JPanel(layout=awt.BorderLayout())
            p.add(b)
            self.actionList.add(p)
            self.frame.contentPane.validate()
    def clearAction(self,actionid):
        if actionid in self.actionControls.keys():
            b=self.actionControls[actionid]
            p=b.container
            self.actionList.remove(p)
            self.frame.contentPane.validate()

    def setEditable(self,key,options):
        self.attr.setEditable(key,options)
    def setNoneditable(self,key):
        self.attr.setNoneditable(key)
        

    def destroy(self):
        self.frame.dispose()

    def clickedOnClose(self,event):
        self.client.setChosen(self)
        
        
            
        
        
        
        
        

class Client:
    def __init__(self):
        self.frames={}
        self.id=None
        self.eventBarUpdater=EventBarUpdater()
        self.currentChooser=None
    def setId(self,id):
        self.id=id
        self.server.setName(self.adminName)
    def setAttr(self,id,key,value):
        f=self._getFrame(id)
        if self.currentChooser!=None:
            table,k=self.currentChooser
            if table.model.thing==f and key==k:
                self.currentChooser=None
                table.choosing=None
        if type(value)==type(()) and len(value)==1:
            value=self._getFrame(value[0])
        f.setAttr(key,value)
        self.repaint()
    def setName(self,id,name):
        self._getFrame(id).setName(name)
    def _getFrame(self,id):
        if id not in self.frames.keys():
            self.frames[id]=Frame(id,self)
            self.server.requestInfo(id)
        return self.frames[id]

    def newEvent(self,id,index,name,delay):
        self._getFrame(id).newEvent(index,name,delay)
    def endEvent(self,id,index):
        self._getFrame(id).endEvent(index)
    def restartEvent(self,id,index):
        self._getFrame(id).restartEvent(index)
        
    def setAction(self,thingid,actionid,name):
        self._getFrame(thingid).setAction(actionid,name)
    def clearAction(self,thingid,actionid):
        self._getFrame(thingid).clearAction(actionid)

    def setEditable(self,thingid,key,options):
        self._getFrame(thingid).setEditable(key,options)
    def setNoneditable(self,thingid,key):
        self._getFrame(thingid).setNoneditable(key)
        

    def destroy(self,id):
        if id in self.frames.keys():
            f=self.frames[id]
            f.destroy()
            del self.frames[id]

    def setCurrentChooser(self,table,key):
        self.currentChooser=(table,key)

    def setChosen(self,chosen):
        if self.currentChooser!=None:
            table,key=self.currentChooser
            self.server.trySetValue(table.model.thing.id,key,(chosen.id,))
        
        
                      
        
        
        
