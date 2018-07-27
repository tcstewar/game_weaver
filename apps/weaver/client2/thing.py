from javax import swing
from java import awt

import math
from useableScreenSize import getScreenBounds

class LineColorScheme:
    owner=None #awt.Color(127,127,127)
    target1=awt.Color(255,0,0)
    target2=awt.Color(0,0,255)
    block1=awt.Color(0,0,0)
    block2=awt.Color(180,180,180)

class ColorScheme:
    border=awt.Color(80,80,80)
    highlight=awt.Color(0,0,0)
    card=awt.Color(127,127,127)
    name=awt.Color(255,255,255)
    timer=awt.Color(255,255,255)
    number=awt.Color(0,0,0)



class WhiteColorScheme(ColorScheme):
    card=awt.Color(255,255,255)
    name=awt.Color(127,127,127)
    timer=awt.Color(127,127,127)
class PlayerColorScheme(ColorScheme):
    card=awt.Color(180,0,180)
class BlueColorScheme(ColorScheme):
    card=awt.Color(0,0,255)
class RedColorScheme(ColorScheme):
    card=awt.Color(255,0,0)
class GreenColorScheme(ColorScheme):
    card=awt.Color(0,80,0)
class BlackColorScheme(ColorScheme):
    card=awt.Color(0,0,0)
    number=awt.Color(127,127,127)
    border=awt.Color(200,200,200)
    highlight=awt.Color(180,180,180)
class DyingColorScheme(ColorScheme):
    card=awt.Color(80,80,80)
    number=awt.Color(120,120,120)
    border=awt.Color(200,200,200)
    highlight=awt.Color(255,255,255)
    name=awt.Color(140,140,140)
    timer=awt.Color(120,120,120)
    
    
    
schemes={
        'w': WhiteColorScheme,
        'b': BlackColorScheme,
        'g': GreenColorScheme,
        'u': BlueColorScheme,
        'r': RedColorScheme,
        '': ColorScheme
        }
    
        
    

class Fonts:
    small=awt.Font('SansSerif',awt.Font.PLAIN,10)

def intersect(x1,y1,x2,y2,x3,y3,x4,y4):
  try:
    d=(y2-y1)*(x4-x3)-(y4-y3)*(x2-x1)
    n=(y3-y1)*(x2-x1)*(x4-x3)-x3*(y4-y3)*(x2-x1)+x1*(y2-y1)*(x4-x3)
    nx=n/d
    try:
        ny=(y2-y1)*(nx-x1)/(x2-x1)+y1
    except ZeroDivisionError:
        ny=(y4-y3)*(nx-x3)/(x4-x3)+y3

    if nx>x1 and nx>x2: return None
    if nx<x1 and nx<x2: return None
    if ny>y1 and ny>y2: return None
    if ny<y1 and ny<y2: return None
    if nx>x3 and nx>x4: return None
    if nx<x3 and nx<x4: return None
    if ny>y3 and ny>y4: return None
    if ny<y3 and ny<y4: return None
    return (nx,ny)
  except ZeroDivisionError:
      return None
  except OverflowError:
      return None

    



class Line(swing.JComponent):
    def __init__(self,source,target,type):
        swing.JComponent.__init__(self)
        self.event=None
        self.color=None
        self.color2=None
        self.sx=0
        self.sy=0
        self.tx=0
        self.ty=0
        self.shapeSize=1
        self.target=None
        self.source=None
        self.type=type
        self.followTarget=0
        self.followAttack=0
        self.shape='circle'
        if source.lines.has_key(type):
            source.lines[type].destroy()
        if target==None: return
        if type=='owner':
            if LineColorScheme.owner==None: return
            self.color=LineColorScheme.owner
        elif type=='attack':
            for e in source.events.values():
                if e.getString()=='Attacking':
                    self.event=e
                    self.shapeSize=7
                    self.event.line=self
                    self.color=LineColorScheme.target1
                    self.color2=LineColorScheme.target2
                    self.percent=0.0
                    break
        elif type=='target':
            for e in source.events.values():
                if e.getString() in ('Attacking','Casting'):
                    self.event=e
                    self.shapeSize=7
                    self.event.line=self
                    self.color=LineColorScheme.target1
                    self.color2=LineColorScheme.target2
                    self.percent=0.0
                    break
            else:
                for e in source.events.values():
                    if e.getString()=='Countering':
                        self.event=e
                        self.shape='block'
                        self.shapeSize=7
                        self.event.line=self
                        self.color=LineColorScheme.block1
                        self.color2=LineColorScheme.block2
                        self.percent=0.0
                        self.followTarget=1
                        break
                else:
                    return
        elif type=='block':
            for e in source.events.values():
                if e.getString()=='Blocking':
                    self.event=e
                    self.shape='block'
                    self.shapeSize=7
                    self.event.line=self
                    self.color=LineColorScheme.block1
                    self.color2=LineColorScheme.block2
                    self.percent=0.0
                    self.followAttack=1
                    break
            else:
                return
                        
        self.source=source
        self.target=target
        self.source.lines[type]=self
        self.target.lines[id(self)]=self
        self.source.parent.add(self,-1000)
        self.resetBounds()
        self.opaque=0
        self.mousePressed=self.onPressed
    def resetBounds(self):
        if self.source==None or self.target==None: return
        if self.source.center==None or self.target.center==None: return
        sx,sy=self.source.getPixelCenter()
        if self.followTarget:
            tl=self.target.lines.get('target',None)
            if tl==None:
                tx,ty=self.target.getPixelCenter()
            else:
                p=tl.event.percentComplete
                b=tl.bounds
                tx=b.x+int(tl.sx+(tl.tx-tl.sx)*p)
                ty=b.y+int(tl.sy+(tl.ty-tl.sy)*p)
        elif self.followAttack:
            tl=self.target.lines.get('attack',None)
            if tl==None:
                tx,ty=self.target.getPixelCenter()
            else:
                p=tl.event.percentComplete
                b=tl.bounds
                tx=b.x+int(tl.sx+(tl.tx-tl.sx)*p)
                ty=b.y+int(tl.sy+(tl.ty-tl.sy)*p)
        else:
            tx,ty=self.target.getPixelCenter()
        x,y,w,h=min(sx,tx),min(sy,ty),abs(sx-tx),abs(sy-ty)
        w+=2*self.shapeSize
        h+=2*self.shapeSize
        x-=self.shapeSize
        y-=self.shapeSize
        self.setBounds(x,y,w,h)
        self.sx=sx-x
        self.sy=sy-y
        self.tx=tx-x
        self.ty=ty-y
    def paintComponent(self,g):
        if self.color2==None or self.event==None:
            g.color=self.color
            g.drawLine(self.sx,self.sy,self.tx,self.ty)
        else:
            p=self.event.percentComplete
            cx=int(self.sx+(self.tx-self.sx)*p)
            cy=int(self.sy+(self.ty-self.sy)*p)
            g.color=self.color2
            g.drawLine(cx,cy,self.tx,self.ty)
            g.color=self.color
            g.drawLine(self.sx,self.sy,cx,cy)
            if self.shape=='circle':
                g.fillOval(cx-self.shapeSize,cy-self.shapeSize,self.shapeSize*2,self.shapeSize*2)
            elif self.shape=='block':    
                g.fillRect(cx-self.shapeSize,cy-self.shapeSize,self.shapeSize*2,self.shapeSize*2)
        if self.followTarget or self.followAttack:
            self.resetBounds()
                
        
    def onPressed(self,event):
        if self.parent.choosing!=None:
            self.parent.doChoice(self.source)
            
            
        

    def destroy(self):
        p=self.parent
        if p!=None:
            self.parent.remove(self)
        if self.source!=None:
            if self.source.lines.has_key(self.type):
                del self.source.lines[self.type]
        if self.target!=None:
            if self.target.lines.has_key(id(self)):
                del self.target.lines[id(self)]
        if self.event!=None:
            self.event.line=None
        if p!=None:
            p.repaint()
  

class Thing(swing.JComponent):
    def __init__(self,id):
        swing.JComponent.__init__(self)
        self.id=id
        self.attr={}
        self.attr['name']=''
        self.attrKeys=[]
        self.center=None
        self.relSize=1.0
        self.mousePressed=self.onPressed
        self.mouseReleased=self.onReleased
        self.mouseDragged=self.onDrag
        self.isSelected=0
        self.cardDisplayListeners=[]
        self.actions={}
        self.events={}
        self.editable={}
        self.lines={}
        self.opaque=1
        self.popup=None
        self.enchantedBy=[]
        self.isReorganizing=0
    def addCardDisplayListener(self,l):
        self.cardDisplayListeners.append(l)
    def removeCardDisplayListener(self,l):
        self.cardDisplayListeners.remove(l)
    def paintComponent(self,g):
        if self.has('tapped') and self.get('tapped'):
            g.translate(self.width/2,self.height/2)
            g.rotate(-math.pi/2)
            g.translate(-self.width/2,-self.height/2)
        
            
        
        
        if self.attr.get('isPlayer',0): scheme=PlayerColorScheme
        elif self.attr.get('dead',0): scheme=DyingColorScheme
        else: scheme=schemes[self.attr.get('color','')]

        g.color=scheme.card
        g.fillRect(0,0,self.size.width,self.size.height)
        
        g.color=scheme.name
        g.font=Fonts.small
        metrics=g.getFontMetrics(g.font)
        if self.size.width>30:
            g.drawString(self.attr['name'],1,metrics.height-5)
        barHeight=2
        yBorder=1
        xBorder=1
        index=len(self.events)-1
        g.color=scheme.timer
        for b in self.events.values():
            val=b.percentComplete
            g.fillRect(xBorder,self.size.height-yBorder-barHeight*(index+1),int((self.size.width-2*xBorder-1)*val),barHeight)
            index-=1

        if self.isSelected:
            g.color=scheme.highlight
        else:
            g.color=scheme.border
        g.drawRect(0,0,self.size.width-1,self.size.height-1)

        toughness=self.attr.get('toughness',None)
        if toughness!=None:
            power=self.attr.get('power',0)
            damage=self.attr.get('damage',0)
            if damage:
                t='%d/%d(%d)' % (power,toughness,toughness-damage)
            else:
                t='%d/%d' % (power,toughness)
        else:
            life=self.attr.get('life',None)
            if life!=None:
                t='%d'%life
            else:
                t=''
        if t!='':
            g.color=scheme.number
            g.drawString(t,self.size.width-metrics.stringWidth(t)-4,self.size.height-4)
        

    def getPixelCenter(self):
        b=self.bounds
        return b.x+b.width/2,b.y+b.height/2
        
    def set(self,key,val):
        if key not in self.attrKeys: self.attrKeys.append(key)
        if key=='enchant':
            oldVal=self.attr.get(key,None)
            if oldVal!=None: oldVal.enchantedBy.remove(self)
        self.attr[key]=val
        if key=='owner' and val!=None:
            Line(self,val,'owner')
        if key=='target':
            Line(self,val,'target')
        if key=='attack':
            Line(self,val,'attack')
        if key=='block':
            Line(self,val,'block')
        if key=='enchant':
            val.enchantedBy.append(self)
            val.reorganizeEnchantments()
            
        for l in self.cardDisplayListeners:
            l.thingChangedAttr(key,val)
        self.repaint()
    def get(self,key):
        return self.attr[key]
    def has(self,key):
        return self.attr.has_key(key)
    def getKeys(self):
        return self.attrKeys
    def setEditable(self,key,options):
        self.editable[key]=options
        for l in self.cardDisplayListeners:
            l.thingChangedAttr(key)
    def setNoneditable(self,key):
        if key in self.editable.keys():
            del self.editable[key]
        for l in self.cardDisplayListeners:
            l.thingChangedAttr(key)
    def reorganizeEnchantments(self):
        if self.parent==None: return
        if self.getCenter()==None: return
        e=self.attr.get('enchant',None)
        if e!=None:
            e.reorganizeEnchantments()
            return
        if self.isReorganizing: return
        self.isReorganizing=1
        dx,dy=self.parent.convertFromPixels(5,10)
        list=[self]
        x,y=self.getCenter()
        x+=dx
        for e in self.enchantedBy:
            y-=dy
            e.setCenter(x,y)
            list.append(e)
        
        list.reverse()
        for c in list:
            self.parent.moveToFront(c)
        self.isReorganizing=0
            
        
        
        
    def setCenter(self,x,y):
        if x>1: x=1.0
        if x<-1: x=-1.0
        if y>1: y=1.0
        if y<-1: y=-1.0

        self.center=(x,y)
        if self.has('owner'): self.fixPlayerBoundaries()
        self.resetBounds()
        self.reorganizeEnchantments()
    def getCenter(self):
        return self.center
    def calcDistance2(self,p):
        x1,y1=self.center
        x2,y2=p.center
        return (x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)
        
    def fixPlayerBoundaries(self):
        if self.center==None: return
        if self.has('enchant'): return
        owner=self.get('owner')
        while owner.has('owner'):
            owner=owner.get('owner')
        if not hasattr(owner,'displayBoundaries'): return
        lines=owner.displayBoundaries

        ox,oy=owner.center
        ox,oy=self.parent.convertToPixels(ox,oy,absolute=1)

        w=self.parent.getThingWidth()*self.relSize
        h=self.parent.getThingHeight()*self.relSize
        itters=0
        moved=1
        while moved and itters<5:
          moved=0  
          cx,cy=self.center
          cx,cy=self.parent.convertToPixels(cx,cy,absolute=1)

          for dx,dy in (-w/2,-h/2),(-w/2,h/2),(w/2,-h/2),(w/2,h/2):
            for x1,y1,x2,y2 in lines:
                x,y=cx+dx,cy+dy

                i=intersect(x1,y1,x2,y2,x,y,ox+dx,oy+dy)
                if i!=None:
                    ix,iy=i
                    nx=cx+ix-x
                    ny=cy+iy-y
                    nx,ny=self.parent.convertFromPixels(nx,ny,absolute=1)
                    self.center=(nx,ny)
                    moved=1
                    break
            if moved: break
          itters+=1
        
            
            
            

        
        
        
    
    def resetBounds(self):
        if self.parent==None: return
        if self.center==None: return
        tw=self.parent.size.width
        th=self.parent.size.height
        cw=tw/2
        ch=th/2
        w=self.parent.getThingWidth()
        h=self.parent.getThingHeight()
        w*=self.relSize
        h*=self.relSize

        x,y=self.center
        cx=cw+tw/2*x
        cy=ch+th/2*y
        self.setBounds(int(cx-w/2),int(cy-h/2),int(w),int(h))
    def setBounds(self,x,y,w,h):
        tw=self.parent.size.width
        th=self.parent.size.height
        if w>tw: w=tw
        if h>th: w=th
        if x<0: x=0
        if y<0: y=0
        if x+w>tw: x=tw-w
        if y+h>th: y=th-h
        swing.JComponent.setBounds(self,x,y,w,h)
        for l in self.lines.values():
            l.resetBounds()
    def onDrag(self,event):
        event.translatePoint(self.getLocation().x,self.getLocation().y)
        self.parent.onDrag(event)
    def onReleased(self,event):
        if event.modifiers&awt.event.InputEvent.BUTTON3_MASK:
            if self.popup==None:
                self.popup=ThingPopup(self)
            self.popup.trigger(event.x,event.y)
        event.translatePoint(self.getLocation().x,self.getLocation().y)
        self.parent.onReleased(event)
        
    def onPressed(self,event):
        if self.parent.choosing!=None:
            self.parent.doChoice(self)
            return
        
        self.parent.moveToFront(self)
        self.dragging=1
        
        self.dragStartX=event.x
        self.dragStartY=event.y
        if not event.isShiftDown():
            self.parent.clearSelectionList()
        self.parent.addToSelectionList(self)
        
        event.translatePoint(self.getLocation().x,self.getLocation().y)
        if self.parent!=None:
            self.parent.onPressed(event,clearList=0)
        
    def setSelected(self,val):
        if val==self.isSelected: return
        self.isSelected=val
        if val:
            self.parent.addToSelectionList(self)
        else:
            self.parent.removeFromSelectionList(self)
        self.repaint()
    def scale(self,val):
        self.relSize*=val
        if self.relSize<0.5: self.relSize=0.5
        if self.relSize>2.0: self.relSize=2.0
        
        self.resetBounds()

    def setAction(self,id,name):
        self.actions[id]=name
        for l in self.cardDisplayListeners:
            l.thingChangedAction(id)
    def clearAction(self,id):
        if id in self.actions.keys():
            del self.actions[id]
            for l in self.cardDisplayListeners:
                l.thingChangedAction(id)

    def newEvent(self,index,name,delay):
        if index in self.events.keys():
            self.events[index].setString(name)
            return
        c=self.parent.eventBarUpdater.makeBar(delay,self)
        c.setStringPainted(1)
        c.setString(name)
        self.events[index]=c
        for l in self.cardDisplayListeners:
            l.thingChangedEvent(index)

        if name=='Attacking' and self.has('attack'):
            Line(self,self.get('attack'),'attack')
        if name=='Casting' and self.has('target'):
            Line(self,self.get('target'),'target')
        if name=='Countering' and self.has('target'):
            Line(self,self.get('target'),'target')
        if name=='Blocking' and self.has('block'):
            Line(self,self.get('block'),'block')
            
        
    def endEvent(self,index):
        if index not in self.events.keys(): return
        c=self.events[index]
        self.parent.eventBarUpdater.remove(c)
        del self.events[index]
        for l in self.cardDisplayListeners:
            l.thingChangedEvent(index)
        self.repaint()
    def restartEvent(self,index):
        if index not in self.events.keys(): return
        self.events[index].value=0

    def destroy(self,thingStore):
        enchant=self.attr.get('enchant',None)
        if enchant!=None: enchant.enchantedBy.remove(self)
        self.setSelected(0)
        p=self.parent
        self.parent.remove(self)
        if self in p.players:
            p.removePlayer(self)
        for l in self.lines.values():
            l.destroy()
        p.repaint()
        

class ThingPopup:
    def __init__(self,thing):
        self.thing=thing
    def trigger(self,x,y):
        menu=swing.JPopupMenu()
        menu.setInvoker(self.thing)

        for a in self.thing.attrKeys:
            if a in self.thing.editable.keys():
                choices=self.thing.editable[a]
                if choices==():
                    menu.add(swing.JMenuItem('Select %s'%a,actionPerformed=lambda x,self=self,a=a: self.setAttrUnknown(a)))
                else:
                    m2=swing.JMenu('Choose %s'%a)
                    for c in choices:
                        m2.add(swing.JMenuItem('%s'%c,actionPerformed=lambda x,server=self.thing.parent.server,id=self.thing.id,a=a,choice=c: server.trySetValue(id,a,choice)))
                    menu.add(m2)
                    
        list=[(name,id) for id,name in self.thing.actions.items()]
        list.sort()
        for name,id in list:
            menu.add(swing.JMenuItem(name,actionPerformed=lambda x,self=self,id=id: self.doAction(id)))

        if menu.componentCount>0:                     
            s=self.thing.getLocationOnScreen()
            x=s.x+x-10
            y=s.y+y-5
            sizeP=menu.preferredSize
            sizeS=getScreenBounds()
            if x+sizeP.width>sizeS.width+sizeS.x:
                x=sizeS.width+sizeS.x-sizeP.width
            if y+sizeP.height>sizeS.height+sizeS.y:
                y=sizeS.height+sizeS.y-sizeP.height
            menu.setLocation(x,y)
            menu.setVisible(1)
    def doAction(self,id):
        self.thing.parent.server.doAction(id)
    def setAttrUnknown(self,attr):
        scp=self.thing.parent.selectedCardPanel
        if scp!=None and scp.thing==self.thing:
            scp.startChoosingTarget(attr)
        else:
            self.thing.parent.startChoosingTarget(self.thing,attr)
        
        
    
        
    
        


class ThingStore:
    def __init__(self,frame,server):
        self.built={}
        self.frame=frame
        self.server=server
    def get(self,id):
        if id in self.built.keys():
            return self.built[id]
        t=Thing(id)
        self.built[id]=t
        self.frame.field.add(t)
        self.server.requestInfo(id)
        return t
    def destroy(self,thing):
        id=thing.id
        thing.destroy(self)
        del self.built[id]
        
        
        
        
        
        
