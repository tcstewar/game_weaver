class Piece:
    board=None
    def __init__(self,black):
        self.black=black    
    def rLook(self,x,y):
        if self.black:
            x,y=8-x,9-y
        return self.board.at(x,y)    
    def rPos(self):
        x,y=self.x,self.y
        if self.black:
            x,y=8-x,9-y
        return x,y
    def moves(self):
        r=[]
        for dx,dy in self.rMoves():
            if self.black:
                r.append((self.x-dx,self.y-dy))
            else:
                r.append((self.x+dx,self.y+dy))
        return r
    def canMove(self,dx,dy,allowCapture=1,mustCapture=0,canCaptureOwn=0):
        if self.black: dx,dy=-dx,-dy
        tx,ty=self.x+dx,self.y+dy
        if 0<=tx<=8 and 0<=ty<=9:
            p=self.board.at(tx,ty)
            if (p==None and not mustCapture) or (allowCapture and p!=None and (p.black!=self.black or canCaptureOwn)):
                return 1
        return 0
        
    
            

class King(Piece):
    symbol='K'
    def rMoves(self):        
        rx,ry=self.rPos()
        r=[]
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            if self.canMove(dx,dy):
                x,y=rx+dx,ry+dy
                if 0<=y<=2 and 3<=x<=5:
                  r.append((dx,dy))
        return r

class Guard(Piece):
    symbol='G'
    def rMoves(self):        
        rx,ry=self.rPos()
        r=[]
        for dx,dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            if self.canMove(dx,dy):
                x,y=rx+dx,ry+dy
                if 0<=y<=2 and 3<=x<=5:
                  r.append((dx,dy))
        return r


class Pawn(Piece):
    symbol='P'
    def rMoves(self):
        r=[]
        rx,ry=self.rPos()
        if self.canMove(0,1): r.append((0,1))
        if ry>=5:
          if self.canMove(1,0): r.append((1,0))
          if self.canMove(-1,0): r.append((-1,0))
        return r  

class Rook(Piece):
    symbol='R'
    def rMoves(self):        
        rx,ry=self.rPos()
        r=[]
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            tx,ty=dx,dy
            while self.canMove(tx,ty,allowCapture=0):
                r.append((tx,ty))
                tx,ty=tx+dx,ty+dy
            if self.canMove(tx,ty,allowCapture=1):
                r.append((tx,ty))
        return r

class Cannon(Piece):
    symbol='C'
    def rMoves(self):        
        rx,ry=self.rPos()
        r=[]
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            tx,ty=dx,dy
            while self.canMove(tx,ty,allowCapture=0):
                r.append((tx,ty))
                tx,ty=tx+dx,ty+dy
            if self.canMove(tx,ty,mustCapture=1,canCaptureOwn=1):
                tx,ty=tx+dx,ty+dy
                while self.canMove(tx,ty,allowCapture=0):
                    tx,ty=tx+dx,ty+dy
                if self.canMove(tx,ty,mustCapture=1):
                    r.append((tx,ty))
        return r

class Knight(Piece):
    symbol='N'
    def rMoves(self):        
        rx,ry=self.rPos()
        r=[]
        for dy in (1,-1):
            if self.canMove(0,dy,allowCapture=0):
                for dx in (1,-1):
                    if self.canMove(dx,dy*2):
                        r.append((dx,dy*2))
        for dx in (1,-1):
            if self.canMove(dx,0,allowCapture=0):
                for dy in (1,-1):
                    if self.canMove(dx*2,dy):
                        r.append((dx*2,dy))
        return r

            
class Elephant(Piece):
    symbol='E'
    def rMoves(self):        
        rx,ry=self.rPos()
        r=[]
        for dx,dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            if ry+dy<=4 and self.canMove(dx,dy,allowCapture=0):
                if self.canMove(2*dx,2*dy,allowCapture=1):
                   r.append((2*dx,2*dy))
        return r
        
        

class Board:
    def __init__(self):
        self.board=[[None]*10 for x in range(9)]
        self.player=0
    def makeCopy(self):
        b=Board()
        for x in range(9):
            for y in range(10):
                p=self.board[x][y]
                if p!=None:
                    p2=p.__class__(p.black)
                    b.place(p2,x,y)
        b.player=self.player
        return b
                
    def place(self,piece,x,y):
        if piece.board!=None:
            piece.board.board[piece.x][piece.y]=None
        self.board[x][y]=piece
        piece.x=x
        piece.y=y
        piece.board=self
        self.player=1-self.player
    def doMove(self,x1,y1,x2,y2,returnCopy=0):
        b=self
        if returnCopy: b=self.makeCopy()
        p=b.board[x1][y1]
        if p==None:
            1/0
        b.board[x2][y2]=p
        b.board[x1][y1]=None
        b.player=1-b.player
        if returnCopy: return b
        
    def placePair(self,type,x,y):
        self.place(type(0),x,y)
        self.place(type(1),8-x,9-y)
        
    def at(self,x,y):
        return self.board[x][y]
        
    def reset(self):
        self.board=[[None]*10 for x in range(9)]
        self.placePair(King,4,0)
        self.placePair(Guard,3,0)
        self.placePair(Guard,5,0)
        self.placePair(Elephant,2,0)
        self.placePair(Elephant,6,0)
        self.placePair(Knight,1,0)
        self.placePair(Knight,7,0)
        self.placePair(Rook,0,0)
        self.placePair(Rook,8,0)
        self.placePair(Cannon,1,2)
        self.placePair(Cannon,7,2)
        self.placePair(Pawn,0,3)
        self.placePair(Pawn,2,3)
        self.placePair(Pawn,4,3)
        self.placePair(Pawn,6,3)
        self.placePair(Pawn,8,3)
        

    def printBoard(self):
        for y in range(10):
            line=''
            for x in range(9):
                p=self.at(x,9-y)
                if p!=None:
                    line+=self.at(x,9-y).symbol
                else:
                    line+='-'
            print line   

    def listPieces(self,black,symbol=None):
        r=[]
        for col in self.board:
            for p in col:
                if p!=None and p.black==black and (symbol==None or symbol==p.symbol):
                    r.append(p)
        return r

    def listMoves(self,black=None):
        if black==None: black=self.player
        r=[]
        for p in self.listPieces(black):
            for x,y in p.moves():
                r.append((p,x,y))
        return r

    def listMovesTo(self,xx,yy,black):
        return [pxy for pxy in self.listMoves(black) if pxy[1]==xx and pxy[2]==yy]

    def win(self,black):
        return len(self.listPieces(1-black,'K'))==0
                  
