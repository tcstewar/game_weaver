defaults={}

def getAllBaseClasses(klass):
    b=[klass]
    i=0
    while i<len(b):
        c=b[i]
        for bb in c.__bases__:
            b.append(bb)
        i+=1
    return b


def reorgDefaults(klass):
    for k in dir(klass):
        if k[:2]!='__' and k!='_allList':
            d=getattr(klass,k)
            if not callable(d) and not type(d)==type(lambda x:x):
                try:
                    delattr(klass,k)
                    if not defaults.has_key(klass):
                        defaults[klass]={}
                    defaults[klass][k]=d
                except AttributeError:
                    pass
    for b in klass.__bases__:
       reorgDefaults(b)

classOverrides={}
def addClassAttributeOverride(klass,key,func):
    if klass not in classOverrides.keys():
        classOverrides[klass]={}
    if key not in classOverrides[klass].keys():
        classOverrides[klass][key]=[]
    classOverrides[klass][key].append(func)
    
def removeClassAttributeOverride(klass,key,func):
    classOverrides[klass][key].remove(func)
        
    

class AttributeOverrideable:
    def __init__(self):
        self._attr={}
        self._attrOverride={}
    def __getattr__(self,key):
        r=self.getWithoutOverrides(key)

        for b in getAllBaseClasses(self.__class__):
            co=classOverrides.get(b,None)
            if co!=None:
                for overrideFunc in co.get(key,()):
                    r2=overrideFunc(self,r)
                    r=r2
        for overrideFunc in self._attrOverride.get(key,()):
            r=overrideFunc(self,r)
        return r
    def __setattr__(self,key,value):
        if key=='_attr':
            self.__dict__[key]=value
            reorgDefaults(self.__class__)
        elif callable(key) or type(value)==type(lambda x: x) or key=='_attrOverride':
            self.__dict__[key]=value
        else:
            self._attr[key]=value
    def addAttrOverride(self,key,func):
        if not self._attrOverride.has_key(key):
            self._attrOverride[key]=[]
        self._attrOverride[key].append(func)
    def removeAttrOverride(self,key,func):
        self._attrOverride[key].remove(func)
    def getWithoutOverrides(self,key):
        if key in self._attr.keys():
            r=self._attr[key]
        elif self.__class__ in defaults.keys() and key in defaults[self.__class__].keys():
            r=defaults[self.__class__][key]
        else:
            for b in getAllBaseClasses(self.__class__):
                if b in defaults.keys() and key in defaults[b].keys():
                    r=defaults[b][key]
                    break
            else:
                raise AttributeError,key
        return r
        
        
        
        
            

    
