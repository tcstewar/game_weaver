from javax import swing
from java import awt

import boardCanvas
import cchess
import simpleCS

colours={
    'White': (255,255,255),
    'Red':(255,0,0),
    'Black':(0,0,0),
    'Green':(0,255,0),
    'Blue':(0,0,255),
    'Grey':(128,128,128),
    }
def makeColour(name):
    c=colours[name]
    return awt.Color(c[0],c[1],c[2])



class Client(swing.JFrame):
    def __init__(self):
        swing.JFrame.__init__(self)
        self.title='Chinese Chess'
        self.windowClosing=self.onExit
        
        self.board=boardCanvas.Canvas()
        self.board.setBoard(cchess.Board())
        self.contentPane.layout=awt.BorderLayout()
        self.contentPane.add(self.board)
        self.statusBar=swing.JLabel('...initializing game...')
        self.contentPane.add(self.statusBar,'South')

        self.board.setDoMove(self.doMove)
        
        self.show()
        self.pack()
    def onJoin(self):
        self.server.setName(self.adminName)
    def onExit(self,event):
        simpleCS.stopClient(self)
        self.dispose()
    def setPlayerNum(self,num):
        self.board.allowPlay(num)
    def setBoard(self,board):
        self.board.setBoard(board)
    def setStatusBar(self,text):
        self.statusBar.text=text
    def setConfig(self,config):
        self.board.setFog(config.fog=='Yes')
        boardCanvas.gridColour=makeColour(config.gridC)
        boardCanvas.backgroundColour=makeColour(config.backC)
        boardCanvas.playerColours=[makeColour(config.p1text),makeColour(config.p2text)]
        boardCanvas.pieceColour=[makeColour(config.p1token),makeColour(config.p2token)]
        self.board.repaint()

    def doMove(self,x1,y1,x2,y2):
        self.server.doMove(x1,y1,x2,y2)
        self.statusBar.text='...waiting for server response...'
    def endGame(self):
        self.board.fog=0
