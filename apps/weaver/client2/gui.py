from javax import swing
from java import awt

from thing import Thing

import math


class EventBar(swing.JProgressBar):
    def __init__(self,max,thing):
        swing.JProgressBar.__init__(self,0,max)
        self.thing=thing
        self.line=None
    def setValue(self,value):
        swing.JProgressBar.setValue(self,value)
        self.thing.repaint()
        if self.line!=None: self.line.repaint()
        
import thread
import time
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
    def makeBar(self,delay,thing):
        c=EventBar(int(delay*self.barScale),thing)
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
            for b in self.bars:
                b.value+=int(delay*self.barScale)
                
        self.stop=1


import voronoi
class Voronoi(swing.JComponent):
    def __init__(self,field):
        swing.JComponent.__init__(self)
        self.field=field
        self.field.add(self,-2000)
        self.lines=[]
        self.color=awt.Color(0,0,0)
    def recalc(self):
        for p in self.parent.players:
            p.displayBoundaries=[]
        self.lines=[]
        ps=[p.center for p in self.parent.players]
        if None in ps: return
        if len(ps)<2:
            self.bounds=0,0,0,0
        else:
            width=self.field.size.width
            height=self.field.size.height
            self.bounds=0,0,width,height
            rays,lines=voronoi.calcVoronoi(ps)

            for x1,y1,x2,y2,affected in lines:
                x1,y1=self.parent.convertToPixels(x1,y1,absolute=1)
                x2,y2=self.parent.convertToPixels(x2,y2,absolute=1)
                self.lines.append((x1,y1,x2,y2))
                for i in affected:
                    self.parent.players[i].displayBoundaries.append((x1,y1,x2,y2))
            
            for x,y,run,rise,affected in rays:
                x,y=self.parent.convertToPixels(x,y,absolute=1)
                rise,run=self.parent.convertToPixels(rise,run)
                if run==0:
                    if rise>0: x2,y2=x,height
                    else: x2,y2=x,0
                elif rise==0:
                    if run>0: x2,y2=width,y
                    else: x2,y2=0,y
                else:
                    m=float(rise)/run
                    if abs(run)>abs(rise):
                        if run>0:
                            x2=width
                        else:
                            x2=0
                        y2=int(m*(x2-x)+y)
                    else:
                        if rise>0:
                            y2=height
                        else:
                            y2=0
                        x2=int((y2-y)/m+x)

                self.lines.append((x,y,x2,y2))                        
                for i in affected:
                    self.parent.players[i].displayBoundaries.append((x,y,x2,y2))
               
            
        self.repaint()
    def paintComponent(self,g):
        g.color=self.color
 #       print self,'drawing',self.lines
        for x1,y1,x2,y2 in self.lines:
            g.drawLine(x1,y1,x2,y2)
            
        
      
        

class Field(swing.JLayeredPane):
    def __init__(self,server):
        swing.JLayeredPane.__init__(self)
        self.server=server
        self.componentResized=self.onResized
        self.defaultThingWidth=50.0
        self.defaultThingHeight=50.0
        self.players=[]
        self.mousePressed=self.onPressed
        self.mouseDragged=self.onDrag
        self.mouseReleased=self.onReleased
        self.dragging=0
        self.mouseWheelMoved=self.onMouseWheel
        self.selectionList=[]
        self.scaleRate=1.3
        self.selectedCardPanel=None
        self.eventBarUpdater=EventBarUpdater()
        self.choosing=None
        self.selfIsDead=0
        self.voronoi=Voronoi(self)
    def clearSelectionList(self):
        for c in self.selectionList:
            c.setSelected(0)
        self.selectionList=[]
        if self.selectedCardPanel!=None:
            if len(self.players)>0 and not self.selfIsDead:
                self.selectedCardPanel.setThing(self.players[0])
            else:
                self.selectedCardPanel.setThing(None)
    def addToSelectionList(self,thing):
        if thing not in self.selectionList: self.selectionList.append(thing)
        thing.setSelected(1)
        if self.selectedCardPanel!=None:
            self.selectedCardPanel.setThing(thing)
    def removeFromSelectionList(self,thing):
        if thing in self.selectionList: self.selectionList.remove(thing)
        thing.setSelected(0)
        if self.selectedCardPanel!=None:
            if len(self.selectionList)==0:
                if len(self.players)>0 and not self.selfIsDead:
                    self.selectedCardPanel.setThing(self.players[0])
                else:
                    self.selectedCardPanel.setThing(None)
            else: self.selectedCardPanel.setThing(self.selectionList[-1])
    def doChoice(self,target):
        if self.choosing==None: return
        if self.selectedCardPanel:
            self.selectedCardPanel.stopChoosing()
        thing,key=self.choosing
        self.server.trySetValue(thing.id,key,(target.id,))
        self.choosing=None
        
    def onDrag(self,event):
        if self.dragging:
            self.dragSelected(event.x-self.dragStartX,event.y-self.dragStartY)
    def onPressed(self,event,clearList=1):
        if clearList: self.clearSelectionList()
        self.dragStartX=event.x
        self.dragStartY=event.y
        self.requestFocus()

        if len(self.selectionList)>0:
            self.dragging=1
            self.dragStart=[]
            for c in self.selectionList:
                self.dragStart.append((c,c.center[0],c.center[1]))

    def onReleased(self,event):
        self.stopDrag()
        self.dragging=0
        
        
    def onResized(self,event):
        for c in self.components:
          if isinstance(c,Thing):  
            c.resetBounds()
        self.voronoi.recalc()
    def convertToPixels(self,x,y,absolute=0):
        x=int(self.size.width*x/2)
        y=int(self.size.height*y/2)
        if absolute:
            x+=self.size.width/2
            y+=self.size.height/2
        return x,y
    def convertFromPixels(self,x,y,absolute=0):
        if absolute:
            x-=self.size.width/2
            y-=self.size.height/2
        x=float(x)/self.size.width*2
        y=float(y)/self.size.height*2
        return x,y
        
    def dragSelected(self,dx,dy):
        dx,dy=self.convertFromPixels(dx,dy)
        draggingPlayer=0
        for c,sx,sy in self.dragStart:
            c.setCenter(sx+dx,sy+dy)
            if not draggingPlayer and c in self.players:
                draggingPlayer=1
        if draggingPlayer:
            self.fixPlayerDistances()
    def fixPlayerDistances(self):
        self.voronoi.recalc()
        for c in self.components:
            if isinstance(c,Thing) and c.has('owner'):
                c.fixPlayerBoundaries()
                c.repaint()
                c.resetBounds()
        
        
            
    def stopDrag(self):
        self.dragging=0
        
            
    def onMouseWheel(self,event):
        scale=(self.scaleRate)**event.wheelRotation

        if len(self.selectionList)==0:
            for c in self.components:
              if isinstance(c,Thing):  
                c.scale(scale)
        else:
            for c in self.selectionList:
                c.scale(scale)
    def getThingWidth(self):
        return self.defaultThingWidth
    def getThingHeight(self):
        return self.defaultThingHeight
    
        
    def initPlayer(self,thing,isMe=0):
        if thing in self.players: return
        if isMe: self.players.insert(0,thing)
        else: self.players.append(thing)

        n=len(self.players)
        
        delta=math.pi*2/n
        for i in range(n):
            x=math.sin(i*delta)*0.9
            y=math.cos(i*delta)*0.9
            self.players[i].setCenter(x,y)
        if isMe and self.selectedCardPanel!=None:
            self.selectedCardPanel.setThing(thing)
        self.fixPlayerDistances()
    def removePlayer(self,thing):
        if thing==self.players[0]:
            self.selfIsDead=1
            if self.selectedCardPanel!=None:
                self.selectedCardPanel.setThing(None)
        self.players.remove(thing)
        self.fixPlayerDistances()

    def initThing(self,thing):
        owner=thing.get('owner')
        c=owner.getCenter()
        if c==None: return
        ox,oy=owner.getCenter()
        dx,dy=self.convertFromPixels(10,5)
        thing.setCenter(ox+dx,oy+dy)
        self.moveToFront(thing)
        if owner==self.players[0]:
            self.clearSelectionList()
            self.addToSelectionList(thing)
    def startChoosingTarget(self,thing,key):
        self.choosing=thing,key

        
           

  
import cardpanel

class InfoArea(swing.Box):
    def __init__(self,server):
        swing.Box.__init__(self,swing.BoxLayout.Y_AXIS)
        self.selectedCardPanel=cardpanel.CardPanel(server)
        self.add(self.selectedCardPanel)

class MainFrame(swing.JFrame):
    def __init__(self,client,gameName):
        swing.JFrame.__init__(self)
        self.server=client.server
        self.client=client
        self.gameName=gameName
        self.players=[]
        self.calcTitle()
        self.windowClosing=self.onClose

        self.field=Field(self.server)
        self.infoArea=InfoArea(self.server)
        self.field.selectedCardPanel=self.infoArea.selectedCardPanel
        self.infoArea.selectedCardPanel.field=self.field
        
        self.split=swing.JSplitPane(swing.JSplitPane.HORIZONTAL_SPLIT,self.infoArea,self.field)
        self.split.oneTouchExpandable=1

        self.contentPane.add(self.split)
        self.size=600,400
        self.show()
#        self.extendedState=awt.Frame.MAXIMIZED_BOTH
        self.split.setDividerLocation(150)

    def calcTitle(self):
        names=[p.get('name') for p in self.players]
        while None in names: names.remove(None)
        self.title=self.gameName+': '+' vs '.join(names)

    def onClose(self,event):
        self.client.shutdown()

    def setSelf(self,thing):
        self.self=thing
        
    def initPlayer(self,thing):
        if thing in self.players: return
        self.field.initPlayer(thing,thing==self.self)
        self.players.append(thing)
        self.calcTitle()
        
        
        
        
        
        
        
        
        
