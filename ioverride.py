def add(base,func):
    if hasattr(base,'name'):
        if hasattr(base,'self'):
            self=base.self
        elif hasattr(base,'im_self'):
            self=base.im_self
        else: raise Exception("Can't figure out how to override",base)
        name=base.name
        argCount=base.argCount
        base=getattr(self,name) # to refresh to make sure we're adding to the most recent
    elif hasattr(base,'im_self'): # if this is the first override
        self=base.im_self
        name=base.im_func.func_name
        argCount=base.im_func.func_code.co_argcount
    else:
        raise Exception("Can't figure out how to override",base)

    base=getattr(self,name) # to refresh to make sure we're adding to the most recent
        
    if argCount==1: f=lambda self=self,func=func,base=base: func(self,base)
    elif argCount==2: f=lambda x,self=self,func=func,base=base: func(x,self,base)
    elif argCount==3: f=lambda x,y,self=self,func=func,base=base: func(x,y,self,base)
    elif argCount==4: f=lambda x,y,z,self=self,func=func,base=base: func(x,y,z,self,base)
    else: raise Exception('Cannot override functions with more than 1 arguments')
    f.argCount=argCount
    f.self=self
    f.name=name
    f.func=func
    f.base=base

    setattr(self,name,f)


def getCurrent(base):
    if hasattr(base,'self'):
        base=getattr(base.self,base.name)
    elif hasattr(base,'im_self'):
        base=getattr(base.im_self,base.im_func.func_name)
    return base


def getList(base):
    base=getCurrent(base)
    r=[]
    while hasattr(base,'func') and hasattr(base,'base'):
        r.append(base.func)
        base=base.base
    return r

def removeAll(base):
    base=getCurrent(base)
    if hasattr(base,'func'):
        name=base.name
        self=base.self
        delattr(self,name)

def remove(base,func):
    base=getCurrent(base)
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
        return
    removeAll(base)
    os.reverse()
    for o in os:
        add(getattr(base.self,base.name),o)


def makeSafeReference(base):
    if not hasattr(base,'name'): # if this is the first override
        name=base.im_func.func_name
        argCount=base.im_func.func_code.co_argcount
        self=base.im_self
        if name=='<lambda>':  # the class has an override
            name=base.im_func.name
            argCount=base.im_func.argCount
    else:
        print 2
        name=base.name
        argCount=base.argCount
        if hasattr(base,'self'):
            self=base.self
        else:
            self=base.im_self
    
    if argCount==1: f=lambda self=self,name=name:getattr(self,name)()
    elif argCount==2: f=lambda x,self=self,name=name:getattr(self,name)(x)
    elif argCount==3: f=lambda x,y,self=self,name=name:getattr(self,name)(x,y)
    elif argCount==4: f=lambda x,y,z,self=self,name=name:getattr(self,name)(x,y,z)
    else: raise Exception('Cannot override functions with more than 4 arguments')
    return f
        
    

if __name__=='__main__':
    class C:
        def func0(self):
            print 'func0'
        def func1(self,x):
            print 'func1',x
    a=C()

    def o1(self,baseFunc):
        print 'pre-o1'
        baseFunc()
        print 'post-o1'
    def o2(self,baseFunc):
        print 'pre-o2'
        baseFunc()
        print 'post-o2'
    def o3(self,baseFunc):
        print 'pre-o3'
        baseFunc()
        print 'post-o3'
    def p1(x,self,baseFunc):
        print 'pre-p1',x
        baseFunc(x)
        print 'post-p1',x
    def p2(x,self,baseFunc):
        print 'pre-p2',x
        baseFunc(x)
        print 'post-p2',x
    def p3(x,self,baseFunc):
        print 'pre-p3',x
        baseFunc(x)
        print 'post-p3',x

    print 'add override o1'    
    add(a.func0,o1)
    a.func0()

    print 'add override o2'    
    add(a.func0,o2)
    a.func0()

    print getList(a.func0)
    removeAll(a.func0)
    print getList(a.func0)
    a.func0()

    print 'add override o1,o2,o3'    
    add(a.func0,o1)
    add(a.func0,o2)
    add(a.func0,o3)
    a.func0()

    print 'remove override o1'
    remove(a.func0,o1)
    a.func0()

    add(a.func1,p1)
    add(a.func1,p2)
    add(a.func1,p3)
    a.func1(1)
    
