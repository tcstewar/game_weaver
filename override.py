import ioverride
import coverride

class OverrideException(Exception):
    pass

def isInstance(base):
    if hasattr(base,'im_self'):
        if base.im_self==None:
            return 0
        else:
            return 1
    elif hasattr(base,'self'):
        return 1
    elif hasattr(base,'klass'):
        return 0
    else:
        raise OverrideException('%s cannot be overriden' % base)
    

def add(base,func):
    if isInstance(base): ioverride.add(base,func)
    else:                coverride.add(base,func)

def remove(base,func):
    if isInstance(base): ioverride.remove(base,func)
    else:                coverride.remove(base,func)

def getList(base):
    if isInstance(base): ioverride.getList(base)
    else:                coverride.getList(base)

def removeAll(base):
    if isInstance(base): ioverride.removeAll(base)
    else:                coverride.removeAll(base)
    
def makeSafeReference(base):
    try:    
        if isInstance(base): return ioverride.makeSafeReference(base)
        else:                return coverride.makeSafeReference(base)
    except OverrideException:
        return base
    
