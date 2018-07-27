from java import awt

def getScreenInset():
    ge=awt.GraphicsEnvironment.getLocalGraphicsEnvironment()
    for gd in ge.getScreenDevices():
        for c in gd.getConfigurations():
            return awt.Toolkit.getDefaultToolkit().getScreenInsets(c)

def getScreenSize():
    return awt.Toolkit.getDefaultToolkit().getScreenSize()

bounds=None
def getScreenBounds():
    global bounds
    if bounds==None:
        i=getScreenInset()
        s=getScreenSize()
        bounds=awt.Rectangle(i.left,i.top,s.width-i.left-i.right,s.height-i.top-i.bottom)
    return bounds    
    
       
getScreenBounds()
