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
        if k[:2]!='__':
            d=getattr(klass,k)
            if not callable(d):
                try:
                    delattr(klass,k)
                    if not defaults.has_key(klass):
                        defaults[klass]={}
                    defaults[klass][k]=d
                except AttributeError:
                    for b in klass.__bases__:
                        reorgDefaults(b)
    

class Base:
    arg1=1
    def __init__(self):
        self._attr={}
    def f1(self):
        return self.arg1
    def __getattr__(self,key):
        if key in self._attr.keys():
            return self._attr[key]
        elif self.__class__ in defaults.keys() and key in defaults[self.__class__].keys():
            return defaults[self.__class__][key]
        else:
            for b in getAllBaseClasses(self.__class__):
                if b in defaults.keys() and key in defaults[b].keys():
                    return defaults[b][key]
            else:
                raise AttributeError,key
    def __setattr__(self,key,value):
        if key=='_attr':
            self.__dict__[key]=value
            reorgDefaults(self.__class__)
        else:
            self._attr[key]=value

class Sub(Base):
    arg2='arg2'

class SubSub(Sub):
    arg4=4
    

a=Base()
print '1:',a.arg1
a.a=1
print '1:',a.a
a.arg1=2
print '2:',a.arg1

Sub.f2=123

b=Sub()
print 'arg2:',b.arg2
print '1:',b.arg1
print '123:',b.f2
print '1:',b.f1()
    
Base.arg1=10
reorgDefaults(Base)

c=SubSub()
d=SubSub()
print '10:',c.arg1
print '2:',a.arg1

print '10:',d.arg1
e=Base()
print '10:',e.arg1
