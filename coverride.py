def add(base,func):
    if hasattr(base,'im_func') and base.im_func.func_name!='<lambda>': # if this is the first override
        name=base.im_func.func_name
        argCount=base.im_func.func_code.co_argcount
        klass=base.im_class
    else:
        name=base.name
        argCount=base.argCount
        klass=base.klass
        base=getattr(klass,name) # to refresh to make sure we're adding to the most recent
        
    if argCount==1: f=lambda self,func=func,base=base: func(self,base)
    elif argCount==2: f=lambda self,x,func=func,base=base: func(self,x,base)
    elif argCount==3: f=lambda self,x,y,func=func,base=base: func(self,x,y,base)
    elif argCount==4: f=lambda self,x,y,z,func=func,base=base: func(self,x,y,z,base)
    else: raise Exception('Cannot override functions with more than 4 arguments')
    f.argCount=argCount
    f.klass=klass
    f.name=name
    f.func=func
    f.base=base

    setattr(klass,name,f)

def getCurrent(base):
    if hasattr(base,'base'):
        base=getattr(base.klass,base.name)
    elif hasattr(base,'im_class'):
        base=getattr(base.im_class,base.im_func.func_name)
    return base

def makeSafeReference(base):
    if hasattr(base,'im_func') and base.im_func.func_name!='<lambda>': # if this is the first override
        name=base.im_func.func_name
        argCount=base.im_func.func_code.co_argcount
        klass=base.im_class
    else:
        name=base.name
        argCount=base.argCount
        klass=base.klass
    if argCount==1: f=lambda self,klass=klass,name=name:getattr(klass,name)(self)
    elif argCount==2: f=lambda self,x,klass=klass,name=name:getattr(klass,name)(self,x)
    elif argCount==3: f=lambda self,x,y,klass=klass,name=name:getattr(klass,name)(self,x,y)
    elif argCount==4: f=lambda self,x,y,z,klass=klass,name=name:getattr(klass,name)(self,x,y,z)
    else: raise Exception('Cannot override functions with more than 4 arguments')
    return f
   
    

def getList(base):
    base=getCurrent(base)
    r=[]
    while hasattr(base,'func') and hasattr(base,'base'):
        r.append(base.func)
        base=base.base
    return r

def removeAll(base):
    base=getCurrent(base)
    if hasattr(base,'base'):
        base=getattr(base.klass,base.name)
    if hasattr(base,'func'):
        b=base
        while hasattr(b,'func'):
            b=b.base
        name=base.name
        klass=base.klass
        setattr(klass,name,b)

def remove(base,func):
    base=getCurrent(base)
    if hasattr(base,'base'):
        base=getattr(base.klass,base.name)
    os=getList(base)
    for o in os:
        if o==func:
            os.remove(o)
            break
        # needed to handle different instances of a bound method
        if hasattr(o,'im_self') and hasattr(func,'im_self') and o.im_self==func.im_self:
            if o.im_func==func.im_func:
                os.remove(o)
                break
    else:
        print 'Warning: override %s was not added to %s before trying to remove it' % (func,base)
        return
    removeAll(base)
    os.reverse()
    for o in os:
        add(getattr(base.klass,base.name),o)
        
    

if __name__=='__main__':
    class C:
        def func0(self):
            print 'func0'
        def func1(self,x):
            print 'func1',x
    a=C()

    def o1(self,baseFunc):
        print 'pre-o1'
        baseFunc(self)
        print 'post-o1'
    def o2(self,baseFunc):
        print 'pre-o2'
        baseFunc(self)
        print 'post-o2'
    def o3(self,baseFunc):
        print 'pre-o3'
        baseFunc(self)
        print 'post-o3'
    def p1(self,x,baseFunc):
        print 'pre-p1',x
        baseFunc(self,x)
        print 'post-p1',x
    def p2(self,x,baseFunc):
        print 'pre-p2',x
        baseFunc(self,x)
        print 'post-p2',x
    def p3(self,x,baseFunc):
        print 'pre-p3',x
        baseFunc(self,x)
        print 'post-p3',x

    print 'add override o1'    
    add(C.func0,o1)
    a.func0()

    print 'add override o2'    
    add(C.func0,o2)
    a.func0()
    print 'add override o3'    
    add(C.func0,o3)
    a.func0()

    print getList(C.func0)
    removeAll(C.func0)
    print getList(C.func0)
    a.func0()

    print 'add override o1,o2,o3'    
    add(C.func0,o1)
    add(C.func0,o2)
    add(C.func0,o3)
    a.func0()

    print 'remove override o1'
    remove(C.func0,o1)
    a.func0()

    add(C.func1,p1)
    add(C.func1,p2)
    add(C.func1,p3)
    a.func1(1)
    
