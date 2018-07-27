import time
import thread
import sys
import simpleCS

appType='Chat Room'

try:    
  from javax import swing
  class Client(swing.JFrame):
    def __init__(self):
        swing.JFrame.__init__(self)
        self.title='Chat'
        self.windowClosing=self.onExit
        self.text=swing.JTextArea(editable=0,lineWrap=1,wrapStyleWord=1)
        self.contentPane.add(swing.JScrollPane(self.text))
        self.input=swing.JTextField(actionPerformed=self.onEnter)
        self.contentPane.add(self.input,'South')
        self.size=300,200
        self.show()
        self.input.requestFocus()
    def onEnter(self,event):
        text=self.input.text
        self.input.text=""
        if text[0]=='/':
            s=text[1:].split(' ',1)
            arg=''
            command=s[0]
            if len(s)>1: arg=s[1]
            if command=='topic':
                self.server.setTopic(arg)
            if command=='name':
                self.server.setName(arg)
            if command=='private':
                self.server.setPrivate(1)
            if command=='public':
                self.server.setPrivate(0)
        else:
            self.server.say(text)
    def onExit(self,event):
        simpleCS.stopClient(self)
        self.dispose()
    def onJoin(self):
        self.server.setName(self.adminName)
    def write(self,message):
        self.text.append('\n'+message)
        self.text.caretPosition=self.text.document.length
except ImportError:
    pass


class Server:
    def __init__(self,config):
        self.private=0
        self.topic=''
        self.waiting={}
        self.waitingId=0
    def onJoin(self,client):
        client.name=client.addr
        self._recalcStatus()
        self.allClients.write('%s joined' % client.name)
        client.setTitle('Chat: %s' % self.topic)
        client.onJoin()
    def say(self,client,text):
        self.allClients.write('%s: %s'%(client.name,text))
    def onDisconnect(self,client):
        self.allClients.write('%s left' % client.name)
        self._recalcStatus()
        if len(self.clients)==0:
            self.adminServer.stopApp(self)
        
    def setName(self,client,name):
        if client.name!=name:
            self.allClients.write('%s is now %s' % (client.name,name))
            client.name=name
            self._recalcStatus()
    def setTopic(self,client,topic):
        self.topic=topic
        self.allClients.setTitle('Chat: %s' % self.topic)
        self._recalcStatus()
    def setPrivate(self,client,private):
        if private==self.private: return
        self.private=private
        if private:
            self.allClients.write('%s has made this a private room' % client.name)
        else:
            self.allClients.write('%s has made this a public room again' % client.name)
        self._recalcStatus()
       
    def _recalcStatus(self):
        if self.private:
            self.status='<Private Room>'
        else:
            self.status='%s [%s]' % (self.topic,','.join([c.name for c in self.clients]))
        self.adminServer.resendAppStatus()
        

    
