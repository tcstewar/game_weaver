from java import awt
from javax import swing
import sys
import copy

playerColours=[awt.Color(0,0,255),awt.Color(0,0,0)]
gridColour=awt.Color(0,0,0)
pieceColour=[awt.Color(200,200,200),awt.Color(200,200,200)]
dangerColour=awt.Color(100,0,0)
safeColour=awt.Color(0,100,0)
fogColour=awt.Color(0,0,0)
backgroundColour=awt.Color(255,255,255)

class Canvas(swing.JComponent):
    def __init__(self):
        swing.JComponent.__init__(self)
        self.background=backgroundColour
        self.board=None
        self.mousePressed=self.pressed
        self.pieceFont=awt.Font('Times New Roman',awt.Font.BOLD,15)
        self.playing=0
        self.selectedPiece=None
        self.doMoveFunc=None
        self.selfColor=None
        self.fog=1
        self.selfColor=-1
        self.preferredSize=250,250
    def setDoMove(self,func):
        self.doMoveFunc=func
    def allowPlay(self,num=None):
        self.playing=1
        self.selfColor=num
    def stopPlay(self):
        self.playing=0
    def setFog(self,fog):
        self.fog=fog
        self.repaint()


    def setPlayer(self,black):
        self.board.player=black


    def pressed(self,event):
        if not self.playing: return
        x,y=self.calcGrid(event.x,event.y)
        if self.selectedPiece!=None:
            ms=self.selectedPiece.moves()
            if (x,y) in ms:
                self.doMove(self.selectedPiece,x,y)
                self.selectedPiece=None
            else:
                self.selectedPiece=None
                self.repaint()
        elif self.playing:
            p=self.board.at(x,y)
            if p!=None and p.black==self.board.player and (self.selfColor==p.black or self.selfColor==None):
                ms=p.moves()
                if len(ms)==0: return
                elif len(ms)==1:
                  x,y=ms[0]
                  self.doMove(p,x,y)
                else:
                  self.selectedPiece=p
                  self.repaint()
                return
            ms=self.board.listMovesTo(x,y,self.board.player)
            if len(ms)==1:
                p,x,y=ms[0]
                self.doMove(p,x,y)

    def doMove(self,p,x,y):
        if self.doMoveFunc!=None:
            self.doMoveFunc(p.x,p.y,x,y)
        else:    
            self.board.place(p,x,y)

    def setBoard(self,board):
        self.board=board
        self.selectedPiece=None
        self.repaint()

    def paintComponent(self,g):
        g.color=backgroundColour
        g.fillRect(0,0,self.size.width,self.size.height)
        self.drawGrid(g)
        if self.fog and self.playing:
            self.drawPiecesFog(g)
        else:    
            self.drawPieces(g)
                   
                
    def drawGrid(self,g):    
        g.color=gridColour
        for i in range(10):
            self.drawGridLine(g,0,i,8,i)
        for i in range(9):
            self.drawGridLine(g,i,0,i,4)
            self.drawGridLine(g,i,5,i,9)
        self.drawGridLine(g,3,0,5,2)    
        self.drawGridLine(g,5,0,3,2)    
        self.drawGridLine(g,3,9,5,7)
        self.drawGridLine(g,5,9,3,7)    
    def drawGridLine(self,g,x1,y1,x2,y2):
        x1,y1=self.calcPoint(x1,y1)
        x2,y2=self.calcPoint(x2,y2)
        g.drawLine(x1,y1,x2,y2)
    def drawBox(self,g,x,y):
        x,y=self.calcPoint(x,y)
        dy,dx=self.size.height/10.0,self.size.width/9.0
        g.fillRect(int(x-dx/2),int(y-dy/2),int(dx)+1,int(dy)+1)
        

    def drawPieces(self,g):        
        g.font=self.pieceFont
        metrics=g.getFontMetrics(self.pieceFont)
        cr=int(min(self.size.height/10.0,self.size.width/9.0)/2.1)

        for black in (0,1):
          for p in self.board.listPieces(black):
              x,y=self.calcPoint(p.x,p.y)
              dx=metrics.charWidth(p.symbol)
              dy=metrics.height/2
              g.color=pieceColour[black]
              g.fillOval(x-cr,y-cr,cr*2,cr*2)
              g.color=playerColours[black]
              g.drawString(p.symbol,x-dx/2,y+dy/2)
        if self.selectedPiece!=None:
          x,y=self.calcPoint(self.selectedPiece.x,self.selectedPiece.y)
          g.color=gridColour
          g.drawOval(x-cr,y-cr,cr*2,cr*2)
          for i,j in self.selectedPiece.moves():
             x,y=self.calcPoint(i,j)
             g.drawOval(x-cr,y-cr,cr*2,cr*2)
                    
    def drawPiecesFog(self,g):        
        g.font=self.pieceFont
        metrics=g.getFontMetrics(self.pieceFont)
        cr=int(min(self.size.height/10.0,self.size.width/9.0)/2.1)

        view=[]
        for p in self.board.listPieces(self.selfColor):
              x,y=self.calcPoint(p.x,p.y)
              dx=metrics.charWidth(p.symbol)
              dy=metrics.height/2
              g.color=pieceColour[self.selfColor]
              g.fillOval(x-cr,y-cr,cr*2,cr*2)
              g.color=playerColours[self.selfColor]
              g.drawString(p.symbol,x-dx/2,y+dy/2)
              view.append((p.x,p.y))
              moves=p.moves()
              view.extend(moves)
        if self.selectedPiece!=None:
          x,y=self.calcPoint(self.selectedPiece.x,self.selectedPiece.y)
          g.color=gridColour
          g.drawOval(x-cr,y-cr,cr*2,cr*2)
          for i,j in self.selectedPiece.moves():
             x,y=self.calcPoint(i,j)
             g.drawOval(x-cr,y-cr,cr*2,cr*2)

        for i in range(9):
            for j in range(10):
                if (i,j) not in view:
                    g.color=fogColour
                    self.drawBox(g,i,j)
                else:
                    p=self.board.at(i,j)
                    if p!=None and p.black!=self.selfColor:
                      x,y=self.calcPoint(p.x,p.y)
                      dx=metrics.charWidth(p.symbol)
                      dy=metrics.height/2
                      g.color=pieceColour[1-self.selfColor]
                      g.fillOval(x-cr,y-cr,cr*2,cr*2)
                      g.color=playerColours[1-self.selfColor]
                      g.drawString(p.symbol,x-dx/2,y+dy/2)

                    
                  

    def calcPoint(self,x,y):
        if self.selfColor==1:
            x=8-x
            y=9-y
        h=self.size.height
        w=self.size.width
        dh=h/10.0
        dw=w/9.0
        return int((x+0.5)*dw),int(h-(y+0.5)*dh)
    def calcGrid(self,x,y):
        h=self.size.height
        w=self.size.width
        dh=h/10.0
        dw=w/9.0
        x,y=int(x/dw),9-int(y/dh)
        if self.selfColor==1:
            x=8-x
            y=9-y
        return x,y    

