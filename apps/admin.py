import simpleCS
import apps



class Config:
    adminPort=6660
    appPorts=range(6661,6666)
    serverAddress='127.0.0.1'
    


def listAppTypes():
    r=[]
    for key in dir(apps):
      if key!='admin':  
        app=getattr(apps,key)
        if hasattr(app,'Server'):
            desc=getattr(app,'appType',key)
            r.append((key,desc))
    return r
    
class AppData:
    def __init__(self,server,port,type):
        self.server=server
        self.port=port
        self.type=type
    def makeInfo(self):
        return self.type,getattr(getattr(apps,self.type),'appType',self.type),self.port,getattr(self.server,'status',''),getattr(self.server,'private',0)

import cPickle
def guessName(addr):
    try:
        names=cPickle.load(open('recentNames.pickle'))
    except Exception,e:
        print e
        return addr
    add=addr[:addr.find(':')]
    if add in names.keys():
        return names[add]
    return addr
def rememberName(addr,name):
    try:
        f=open('recentNames.pickle')
        names=cPickle.load(f)
        f.close()
    except Exception,e:
        names={}
    add=addr[:addr.find(':')]
    names[add]=name
    f=open('recentNames.pickle','w')
    cPickle.dump(names,f)
    f.close()
    
    
    
class DummyConfig:
    class Labels:
        pass
    class Options:
        pass
    
        
    
    
    

class Server:
    def __init__(self,config):
        self.apps=[]
        self.appTypes=listAppTypes()
        self.appConfig={}
        for app,desc in self.appTypes:
            self.appConfig[app]=getattr(getattr(apps,app),'Config',DummyConfig)()
        self.runningApps=[]
        self.config=config
    def onJoin(self,client):
        client.setAppTypes(self.appTypes)
        for appType,desc in self.appTypes:
            for key in dir(self.appConfig[appType].Options):
                val=getattr(self.appConfig[appType].Options,key)
                if type(val)==type(()) or type(val)==type([]):
                    client.setAppConfig(appType,key,getattr(self.appConfig[appType],key))
        client.setRunningApps(self._makeAppInfoList())
        client.name=guessName(client.addr)
        client.setName(client.name)
    def _makeAppInfoList(self):
        return [x.makeInfo() for x in self.runningApps]
    def onDisconnect(self,client):
        pass
    def resendAppStatus(self,client=None):
        self.allClients.setRunningApps(self._makeAppInfoList())
    def setName(self,client,name):
        if name not in [c.name for c in self.clients]:
            rememberName(client.addr,name)
            client.name=name
        client.setName(client.name)
    def setAppConfig(self,client,appType,key,value):
        conf=self.appConfig[appType]
        if value in getattr(conf.Options,key):
            oldVal=getattr(conf,key)
            setattr(conf,key,value)
            if hasattr(conf,'isValid') and not conf.isValid():
                setattr(conf,key,oldVal)
                value=oldVal
            self.allClients.setAppConfig(appType,key,value)
    def startApp(self,client,type):
        port=self._getFreePort()
        if port!=None:
            app=getattr(apps,type)
            appServer=app.Server(self.appConfig[type])
            appServer.adminServer=self
            simpleCS.startServer(port,appServer)
            self.runningApps.append(AppData(appServer,port,type))
            self.allClients.setRunningApps(self._makeAppInfoList())
            if client!=None:
                client.joinApp(type,port)
    def stopApp(self,appServer):
        simpleCS.stopServer(appServer)
        for i in range(len(self.runningApps)):
            if self.runningApps[i].server==appServer:
                del self.runningApps[i]
                self.allClients.setRunningApps(self._makeAppInfoList())
                break
    def _getFreePort(self):
        used=[a.port for a in self.runningApps]
        for p in self.config.appPorts:
            if p not in used:
                return p
        return None

import sys

try:
  from javax import swing
#  swing.UIManager.setLookAndFeel(swing.UIManager.getSystemLookAndFeelClassName())
  import java
  class RunningAppTableModel(swing.table.AbstractTableModel):
    def __init__(self):
        self.data=[]
    def getColumnName(self,col): return ['Type','Status'][col]
    def getRowCount(self): return len(self.data)
    def getColumnCount(self): return 2
    def getValueAt(self,row,col): return self.data[row][(1,3)[col]]
    def isCellEditable(self,row,col): return 0
    def setList(self,data):
        data.sort()
        self.data=data
        self.fireTableDataChanged()
    def getInfoForRow(self,row):
        return self.data[row]

  class ConfigTableModel(swing.table.AbstractTableModel):
    def __init__(self,config,appType,onChange):
        self.config=config
        self.keys=[]
        self.options={}
        self.onChange=onChange
        self.appType=appType
        for key in dir(self.config.Options):
            val=getattr(self.config.Options,key)
            if type(val)==type([]) or type(val)==type(()):
                self.keys.append(key)
                self.options[key]=getattr(self.config.Options,key)
    def getColumnName(self,col): return ['Option','Setting'][col]
    def getRowCount(self): return len(self.keys)
    def getColumnCount(self): return 2
    def getValueAt(self,row,col):
        if col==0: return getattr(self.config.Labels,self.keys[row],self.keys[row])
        else: return getattr(self.config,self.keys[row])
    def isCellEditable(self,row,col):
        return [0,1][col]
    def setConfigValue(self,key,value):
        setattr(self.config,key,value)
        self.fireTableDataChanged()
    def getOptionsAt(self,row):
        return self.options[self.keys[row]]
    def setValueAt(self,value,row,col):
        if col==1:
            self.onChange(self.appType,self.keys[row],value)
            self.fireTableCellUpdated(row,col)
  class ConfigTable(swing.JTable):
    def __init__(self,model):
        swing.JTable.__init__(self,model)
    def prepareEditor(self,editor,row,col):
        if col==1:
            c=editor.component
            c.removeAllItems()
            for k in self.model.getOptionsAt(row):
                c.addItem(k)
        return swing.JTable.prepareEditor(self,editor,row,col)
        

    

  class Client(swing.JFrame):
    def __init__(self):
        swing.JFrame.__init__(self)
        self.title='Network Application Organizer'
        self.windowClosing=lambda x: sys.exit()

        self.namePane=swing.JPanel(layout=java.awt.BorderLayout())
        self.namePane.add(swing.JLabel('Name:'),'West')
        self.nameText=swing.JTextField(actionPerformed=self.onTrySetName)
        self.namePane.add(self.nameText)
        self.contentPane.add(self.namePane,'North')

        self.tab=swing.JTabbedPane()
        
        self.runningAppData=RunningAppTableModel()
        self.table=swing.JTable(self.runningAppData)
        self.table.selectionMode=swing.ListSelectionModel.SINGLE_SELECTION
        self.table.preferredScrollableViewportSize=300,50
        self.table.mouseClicked=self.onTableClicked

        self.appTypeList=swing.JList(mouseClicked=self.onTypeListClicked,valueChanged=self.onTypeListSelectionChanged)
        createPane=swing.JPanel(layout=java.awt.BorderLayout())
        createPane.add(swing.JScrollPane(self.appTypeList),'West')
        self.startAppButton=swing.JButton('Start',actionPerformed=self.onStartApp)
        createPane.add(self.startAppButton,'East')

        self.optionPanelLayout=java.awt.CardLayout()
        self.optionPanel=swing.JPanel(layout=self.optionPanelLayout)
        self.optionEditor=swing.JComboBox(font=swing.JTable().font)
        createPane.add(self.optionPanel)

        self.tab.addTab('Start New App',createPane)
        self.tab.addTab('Running Apps',swing.JScrollPane(self.table))

        self.contentPane.add(self.tab)
        
        self.pack()
        self.show()
    def onTrySetName(self,event):
        self.server.setName(self.nameText.text)
        self.nameText.text=''
    def setName(self,name):
        self.nameText.text=name
    def onStartApp(self,event=None):
        type=self.appTypes[self.appTypeList.selectedIndex][0]
        self.server.startApp(type)
        self.tab.selectedIndex=1
    def onTypeListClicked(self,event):
        if event.clickCount==2:
            self.onStartApp()
    def onTypeListSelectionChanged(self,event):
        self.optionPanelLayout.show(self.optionPanel,self.appTypes[self.appTypeList.selectedIndex][0])


    def onTableClicked(self,event):
        if event.clickCount==2:
            row=self.table.selectedRow
            type,typeName,port,status,private=self.runningAppData.getInfoForRow(row)
            if not private:
                self.joinApp(type,port)

    def joinApp(self,type,port):
        client=getattr(apps,type).Client()
        addr=self.server.addr
        if ':' in addr: addr=addr[:addr.find(':')]  # strip the port number off the address
        client.adminName=self.nameText.text
        simpleCS.startClient(addr,port,client)
            
        
    def setAppTypes(self,types):
        types.sort(lambda a,b: cmp(a[1],b[1]))
        self.appTypes=types
        self.appTypeList.setListData([t[1] for t in types])
        self.appModel={}
        for type,desc in types:
            config=getattr(getattr(apps,type),'Config',DummyConfig)()
            m=ConfigTableModel(config,type,self.server.setAppConfig)
            table=ConfigTable(m)
            table.selectionMode=swing.ListSelectionModel.SINGLE_SELECTION
            table.preferredScrollableViewportSize=200,50
            table.getColumnModel().getColumn(1).setCellEditor(swing.DefaultCellEditor(self.optionEditor))
            self.optionPanel.add(swing.JScrollPane(table),type)
            self.appModel[type]=m
        if len(types)>0:
            self.appTypeList.selectedIndex=0
            self.optionPanelLayout.show(self.optionPanel,types[0][0])
        self.pack()
    def setAppConfig(self,type,key,value):
        self.appModel[type].setConfigValue(key,value)
        
            
            
            
            
            
            
        
    def setRunningApps(self,appInfo):
        self.runningAppData.setList(appInfo)
        if len(appInfo)==0:
            self.tab.selectedIndex=0
            
except ImportError:
    pass
