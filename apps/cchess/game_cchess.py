from javax import swing
from java import awt
import games
import game_cchess
import game_cchess_boardgui
import cchess
import random

colours={
    'White': (255,255,255),
    'Red':(255,0,0),
    'Black':(0,0,0),
    'Green':(0,255,0),
    'Blue':(0,0,255),
    'Grey':(128,128,128),
    }
colourNames=colours.keys()
colourNames.sort()
def makeColour(name):
    c=colours[name]
    return awt.Color(c[0],c[1],c[2])
    


class Config:
    minPlayers=2
    maxPlayers=2
    fog='No'
    backgroundColour='White'
    gridColour='Black'
    p1token='Blue'
    p2token='Red'
    p1text='White'
    p2text='White'
    options=[('fog','Fog of War',['No','Yes']),
             ('backgroundColour','Background',colourNames), 
             ('gridColour','Grid',colourNames),
             ('p1token','Player 1 Token',colourNames),
             ('p1text','Player 1 Text',colourNames),
             ('p2token','Player 2 Token',colourNames),
             ('p2text','Player 2 Text',colourNames),
            ]
    def isValid(self):
        if self.gridColour==self.backgroundColour: return 0
        if self.p1token==self.p2token: return 0
        if self.p1token==self.p1text: return 0
        if self.p2token==self.p2text: return 0
        return 1
        
        

def setColours(gui,state):
    gui.gridColour=makeColour(state.gridColour)
    gui.backgroundColour=makeColour(state.backgroundColour)
    gui.playerColours=[makeColour(state.p1text),makeColour(state.p2text)]
    gui.pieceColour=[makeColour(state.p1token),makeColour(state.p2token)]
                       


class Gui:
    def __init__(self,gui):
        self.gui=gui
        self.server=gui.client.server
        self.boardFrame=swing.JInternalFrame('Chinese Chess',1,1,1,1,internalFrameClosing=self.onClosing,defaultCloseOperation=swing.JInternalFrame.DO_NOTHING_ON_CLOSE)
        setColours(game_cchess_boardgui,gui.config.state)
        self.board=game_cchess_boardgui.Canvas()
        self.board.setDoMove(self.server.doMove)
        self.board.setBoard(cchess.Board())
        self.boardFrame.contentPane.layout=awt.BorderLayout()
        self.boardFrame.contentPane.add(self.board)
        self.statusBar=swing.JLabel('temp')
        self.boardFrame.contentPane.add(self.statusBar,'South')
        gui.main.add(self.boardFrame)
        
        self.boardFrame.show()
        self.boardFrame.pack()
        self.boardFrame.size=300,300
        self.boardFrame.invalidate()

        self.suggestFrame=games.SuggestionFrame(AI(),self.server,self.gui.main)
        print 'made gui'
    def onClosing(self,event):
        self.server.doClose()
    def setState(self,state):
        self.board.setBoard(state.board)
        self.board.fog=state.fog
        if state.playing:
            self.board.allowPlay(state.myPlayerNum)
        if state.gameOver:
            self.boardFrame.closable=1
            self.board.stopPlay()
        self.setStatusBar(state)
        self.suggestFrame.lookForSuggestions(state)
    def setStatusBar(self,state):
        if state.gameOver:
            if state.youWon: text='You won!'
            else: text='%s won!' % state.winnerName
        elif state.playing and state.myPlayerNum==state.board.player:
            text='Your turn'
        else:
            text='Waiting for %s to play' % state.currentPlayerName
        self.statusBar.text=text
    def dispose(self):
        self.boardFrame.dispose()
        self.suggestFrame.dispose()
        
class Game(games.Game):
    def initialize(self):
        self.board=cchess.Board()
        self.fog=self.config.fog=='Yes'
        self.board.reset()
        self.board.player=0
        self.sendStateToAll()
    def makeState(self,client):
        s=games.State()
        s.board=self.board
        s.fog=self.fog
        if client in self.players:
            s.myPlayerNum=self.players.index(client)
        s.currentPlayerName=self.server.names[self.players[self.board.player]]
        if self.winner:
            s.winnerName=self.server.names[self.winner]
        return s

    def doMove(self,client,x1,y1,x2,y2):
        if not self.players[self.board.player]==client: return
        p=self.board.at(x1,y1)
        if p==None:
            print 'someone tried to move',x1,y2,x2,y2
            return
        self.board.place(p,x2,y2)
        for i in 1,0:
            if self.board.win(i):
                self.winner=self.players[i]
        self.sendStateToAll()


import ai_generic

points={'K':1000,'R':9,'C':9,'N':5,'E':5,'P':3,'G':3}
        
class AI(games.AI):
    name='AI_CChess2'
    decisionThreshold=10
    gameName='Chinese Chess'
    def think(self,state):
        if state.board.player!=state.myPlayerNum: self.addSuggestion(self.thresh,'Wait for your turn',None,None)
        self.board=state.board
        self.moves=state.board.listMoves()


        node=ai_generic.Node(state.board,lambda state: state.listMoves(),lambda s,(p,x,y): s.doMove(p.x,p.y,x,y,returnCopy=1),self.calcScore)

        # add in all possible moves first
        for p,x,y in node.getMoves():
            self.addSuggestion(0,"",self.server.doMove,(p.x,p.y,x,y))

        # Capture pieces
        for p,x,y in node.getMoves():
            a=self.board.at(x,y)
            if a!=None:
                self.addSuggestion(points[a.symbol],"Take the %s" % a.symbol,self.server.doMove,(p.x,p.y,x,y))
        
        # avoid being captured on next turn
        for p,x,y in node.getMoves():
            n2=node.getResult((p,x,y))
            for p2,x2,y2 in n2.getMoves():
              if (x2,y2)==(x,y):  
                a=n2.state.at(x2,y2)
                if a!=None:
                    score=points[a.symbol]
                    n3=n2.getResult((p2,x2,y2))
                    bestTake=0
                    for p3,x3,y3 in n3.getMoves():
                      if (x3,y3)==(x2,y2):  
                        a2=n3.state.at(x3,y3)
                        if a2!=None: bestTake=max(points[a2.symbol],bestTake)
                    self.addSuggestion(bestTake-score,"Don't let opponent take your %s" % a.symbol,self.server.doMove,(p.x,p.y,x,y))
                    break

        # avoid losing King on next turn
        for p,x,y in node.getMoves():
            n2=node.getResult((p,x,y))
            for p2,x2,y2 in n2.getMoves():
                a=n2.state.at(x2,y2)
                if a!=None and a.symbol=='K':
                    self.addSuggestion(-1000,"Don't let opponent take your King",self.server.doMove,(p.x,p.y,x,y))
                    break
                
                   
    def calcScore(self,node):
        if node.state.win(node.state.player): return ai_generic.win
        elif node.state.win(1-node.state.player): return ai_generic.lose
        else:
            score=len(node.getMoves())
            return score
        
    def thinkDontBeTaken(self):
        self.nextBoards={}
        self.nextMoves={}
        for m in self.moves:
            p,x,y=m
            b2=self.board.makeCopy()
            b2.doMove(p.x,p.y,x,y)
            self.nextBoards[m]=b2
            m2=b2.listMoves()
            self.nextMoves[m]=m2
            for p2,x2,y2 in m2:
                if x2==x and y2==y:
                    self.addSuggestion(-2,"captured",self.server.doMove,(p.x,p.y,x,y))
                    break
            
    def nameSuggestion(self,func,args):
        if func==self.server.doMove:
            px,py,x,y=args
            return '%s(%d,%d)->%d,%d' % (self.board.at(px,py).symbol,px,py,x,y)

        


    

    
