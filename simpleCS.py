import socket
import thread
import time
import cPickle
import traceback

debug=0
logging=0

def log(text):
    if (logging):
        f=open('serverLog.txt','a')
        f.write(text+'\n')
        f.close()
    if (debug):
        print text


class SafeSocket:
    headerSize=16
    bufferSize=2048
    def __init__(self,socket,handler,name,extraArg=None,server=None):
        self.socket=socket
        self.handler=handler
        self.extraArg=extraArg
        self.stop=0
        thread.start_new_thread(self.watcher,())
        thread.start_new_thread(self.ping,())
        self.server=server
        self.addr='%s:%s' % name
        self.lastSendTime=time.time()
        
    def sendFunc(self,func,args,args2):
        if self.stop: raise socket.error
        if func!='': log('sending command "%s" with args "%s" and "%s"' % (func,args,args2))
        m=cPickle.dumps((func,args,args2))
        header=str(len(m)).rjust(self.headerSize)
        self.socket.send(header+m)
        self.lastSendTime=time.time()
    def ping(self):
        try:
          while not self.stop:
              now=time.time()
              if now>self.lastSendTime+2:
                self.sendFunc('',None,None)
                self.lastSendTime=now
              time.sleep(2)
        except socket.error:
            if self.server!=None: self.server.removeClient(self)
            elif hasattr(self.handler,'onDisconnect'): self.handler.onDisconnect()
        except:
            pass

    def watcher(self):
        buff=''
        try:  
          while not self.stop:
            while len(buff)<self.headerSize:
                buff+=self.socket.recv(self.bufferSize)
            h=buff[:self.headerSize]
            buff=buff[self.headerSize:]
            ln=int(h)
            while len(buff)<ln:
                buff+=self.socket.recv(self.bufferSize)
            m=buff[:ln]
            buff=buff[ln:]
#            if self.server!=None and self not in self.server.clients:
#                self.stop=1
#            else:  
            self.callFunction(m)
        except socket.error,e:
            log('Lost connection from %s' % self.addr)
        except TypeError,e:
            log('Lost connection from %s' % self.addr)
        if self.server!=None: self.server.removeClient(self)
        elif hasattr(self.handler,'onDisconnect'): self.handler.onDisconnect()
        self.socket.close()
    def callFunction(self,m):
        func,args,args2=cPickle.loads(m)
        if func=='': return  # ignore pings
        log('calling command "%s" with args "%s" and "%s"' % (func,args,args2))

        f=getattr(self.handler,func,None)
        if f==None:
            try:
                f=self.handler._getattr_conditional(func,self.extraArg)
            except AttributeError:
                pass
        if f==None:
            print 'Error: unknown function call:',(func,args,args2)
        else:
            if self.extraArg!=None: args=(self.extraArg,)+args
            try:  
                apply(f,args,args2)
            except Exception,e:
                traceback.print_exc()

class Server:
    def __init__(self,port,handler):
        self.port=port
        self.clients=[]
        self.handler=handler
        self.stop=0
        thread.start_new_thread(self.listener,())

    # Why do I have to kill the socket all the time in Jython?
    def listener(self):
        while not self.stop:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.bind(('',self.port))
            s.listen(5)
            conn,addr=s.accept()
            self.addClient(conn,addr)
            s.close()

    def listener2(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind(('',self.port))
        while not self.stop:
            s.listen(5)
            conn,addr=s.accept()
            self.addClient(conn,addr)

    def addClient(self,conn,addr):
        c=SafeSocket(conn,self.handler,addr,server=self)
        c.proxy=Proxy(c,onFail=self.removeClient)
        c.extraArg=c.proxy
        log('New connection from %s'%c.addr)
        self.clients.append(c)
        self.handler.clients.append(c.proxy)
        self.handler.onJoin(c.proxy)
    def removeClient(self,ss):
        p=ss.proxy
        if ss.proxy in self.handler.clients: self.handler.clients.remove(ss.proxy)
        if ss in self.clients: self.clients.remove(ss)
        if hasattr(self.handler,'onDisconnect'):
            self.handler.onDisconnect(p)

    def sendToAll(self,m,ignore=[]):
        for c in self.clients:
            if c not in ignore:
                c.send(m)

class FuncProxy:
    def __init__(self,ss,func,onFail=None):
        self.ss=ss
        self.func=func
        self.onFail=onFail
    def __call__(self,*args,**args2):
        if self.func=='forceDisconnect':
            self.onFail(self.ss)
        else:
          try:
            self.ss.sendFunc(self.func,args,args2)
          except socket.error:
            if self.onFail!=None: self.onFail(self.ss)

class AllFuncProxy:
    def __init__(self,server,func):
        self.server=server
        self.func=func
    def __call__(self,*args,**args2):
        for s in self.server.clients:
            try:
                s.sendFunc(self.func,args,args2)
            except socket.error:
                self.server.removeClient(s)



class Proxy:
    def __init__(self,ss,onFail=None):
        self._ss=ss
        self._onFail=onFail
        self.addr=ss.addr
        self._proxies={}
    def __getattr__(self,attr):
        if attr[0]=='_': raise AttributeError,attr
        if self._proxies.has_key(attr):
            return self._proxies[attr]
        else:
            p=FuncProxy(self._ss,attr,onFail=self._onFail)
            self._proxies[attr]=p
            return p

class AllProxy:
    def __init__(self,server):
        self._server=server
    def __getattr__(self,attr):
        if attr[0]=='_': raise AttributeError,attr
        return AllFuncProxy(self._server,attr)


        
clients={}
servers={}

def startClient(addr,port,handler):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((addr,port))
    ss=SafeSocket(s,handler,(addr,port))
    handler.server=Proxy(ss)
    if handler in clients.keys(): stopClient(handler)
    clients[handler]=ss
    
def startServer(port,handler):
    s=Server(port,handler)
    handler.allClients=AllProxy(s)
    handler.clients=[]
    handler.currentPort=port
    servers[handler]=s

def stopClient(handler):
    if handler in clients.keys():
        ss=clients[handler]
        ss.stop=1
        del clients[handler]
    
def stopServer(handler):
    if handler in servers.keys():
        s=servers[handler]
        dummyConnect=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        dummyConnect.connect(('127.0.0.1',s.port))
        dummyConnect.close()
        s.stop=1
        del servers[handler]
    
    
