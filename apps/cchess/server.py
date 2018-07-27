import cchess

class Config:
    fog='Yes'
    backC='White'
    gridC='Black'
    p1token='Blue'
    p2token='Red'
    p1text='White'
    p2text='White'
    class Labels:
        fog='Fog of War'
        backC='Background'
        gridC='Grid Colour'
        p1token='Player 1 Token'
        p1text='Player 1 Text'
        p2token='Player 2 Token'
        p2text='Player 2 Text'
    class Options:
        fog='Yes','No'
        backC=('White','Red','Black','Green','Blue','Grey')
        gridC=backC
        p1token=backC
        p1text=backC
        p2token=backC
        p2text=backC
    def isValid(self):
        if self.gridC==self.backC: return 0
        if self.p1token==self.p2token: return 0
        if self.p1token==self.p1text: return 0
        if self.p2token==self.p2text: return 0
        return 1
    
        

class Server:
    def __init__(self,config):
        self.board=cchess.Board()
        self.config=config
        self.board.reset()
        self.board.player=0
        self.players=[None,None]
        self.winner=None
    def setName(self,client,name):
        client.name=name
        self._updateStatusBars()
        self._updateAdminStatus()
    def onJoin(self,client):
        client.name=client.addr
        client.onJoin()
        if None in self.players:
            i=self.players.index(None)
            self.players[i]=client
            client.setPlayerNum(i)
        client.setBoard(self.board)
        client.setConfig(self.config)
        self._updateStatusBars()
        self._updateAdminStatus()
    def onDisconnect(self,client):
        if len(self.clients)==0:
            self.adminServer.stopApp(self)
        elif client in self.players:
            self.players[self.players.index(client)]=None
            self._updateStatusBars()
            self._updateAdminStatus()
        

    def doMove(self,client,x1,y1,x2,y2):
        if not self.clients[self.board.player]==client: return
        p=self.board.at(x1,y1)
        if p==None:
            print 'someone tried to move',x1,y2,x2,y2
            return
        self.board.place(p,x2,y2)
        for i in 1,0:
            if self.board.win(i):
                self.winner=self.players[i]
                self.allClients.endGame()
                self.adminServer.stopApp(self)
                
        self.allClients.setBoard(self.board)
        self._updateStatusBars()
    def _updateAdminStatus(self):
        p1='?'
        p2='?'
        if self.players[0]!=None: p1=self.players[0].name
        if self.players[1]!=None: p2=self.players[1].name
        self.status='%s vs %s' % (p1,p2)
        self.adminServer.resendAppStatus()
        self.allClients.setTitle('Chinese Chess: %s' % self.status)
    def _updateStatusBars(self):
        if self.winner!=None:
            self.allClients.setStatusBar('%s won!' % self.winner.name)
        else:
          for c in self.clients:
            if c==self.players[self.board.player]:
                c.setStatusBar('Your Turn')
            elif self.players[self.board.player]==None:
                c.setStatusBar('Waiting for an opponent to join')
            else:
                c.setStatusBar('Waiting for %s to play' % self.players[self.board.player].name)
                
                
  
