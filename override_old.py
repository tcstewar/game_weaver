overridesI={}
def overrideI(base,func):
    print base,func
    if not hasattr(base,'im_func'):  # must be a lambda
        i=base.argCount
        name=base.name
        self=base.im_self
        print i,name,base.im_self
    else:
        i=base.im_func.func_code.co_argcount
        if base.im_func in overridesI.keys():
            name,x,y=overrides[base.im_func]
            i-=3
        if base.im_func in overrides.keys():
            name,x,y=overrides[base.im_func]
            i-=2
        else:
            name=base.im_func.func_name
        self=base.im_self
        base=getattr(base.im_class,name)
    if i==1: f=lambda func=func,base=base,self=self: func(self,base)
    elif i==2: f=lambda x,func=func,base=base,self=self: func(self,x,base)
    elif i==3: f=lambda x,y,func=func,base=base,self=self: func(self,x,y,base)
    elif i==4: f=lambda x,y,z,func=func,base=base,self=self: func(self,x,y,z,base)
    else: raise Exception('Cannot override functions with more than 4 arguments')
    overrides[f]=(name,base,func)
    f.im_self=self
    f.argCount=i
    f.name=name

    

    setattr(self,name,f)
    


overrides={}
def override(base,func):
    if base.im_self!=None:
        overrideI(base,func)
        return
    i=base.im_func.func_code.co_argcount
    if base.im_func in overrides.keys():
        name,x,y=overrides[base.im_func]
        i-=2
    else:
        name=base.im_func.func_name
    if i==1: f=lambda self,func=func,base=base: func(self,base)
    elif i==2: f=lambda self,x,func=func,base=base: func(self,x,base)
    elif i==3: f=lambda self,x,y,func=func,base=base: func(self,x,y,base)
    elif i==4: f=lambda self,x,y,z,func=func,base=base: func(self,x,y,z,base)
    else: raise Exception('Cannot override functions with more than 4 arguments')
    overrides[f]=(name,base,func)
    f.name=name

    setattr(base.im_class,name,f)


def getOverrideList(base):
    f=base.im_func
    r=[]
    while f in overrides.keys():
        name,base,func=overrides[f]
        r.append(func)
        f=base.im_func
    r.append(f)
    return r

    
def removeOverride(base,func):
    if base.im_func.func_name!='<lambda>':
        base=getattr(base.im_class,base.im_func.func_name)
    else:
        base=getattr(base.im_class,base.im_func.name)
        
    os=getOverrideList(base)
    if func not in os:
        raise Exception('No override to %s found in %s' % (func,base))
    if func==os[-1]:
        raise Exception('Cannot remove original base method')
    originalBase=os[-1]
    os=os[:-1]
    os.remove(func)
    setattr(base.im_class,originalBase.func_name,originalBase)
    os.reverse()
    for o in os:
        override(getattr(base.im_class,originalBase.func_name),o)
    
    
    
   
    

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
    override(C.func0,o1)
    a.func0()

    print 'remove override o1'    
    removeOverride(C.func0,o1)
    a.func0()

    print 'add override o1,o2'    
    override(C.func0,o1)
    override(C.func0,o2)
    a.func0()

    print getOverrideList(C.func0)

    print 'remove override o1'    
    removeOverride(C.func0,o1)
    a.func0()

#    print 'remove override o2'    
#    removeOverride(C.func0,o2)
#    a.func0()

    override(C.func1,p1)
    a.func1('a')
    print 'Instance'
    b=C()
    override(a.func0,o1)
#    override(a.func1,p2)
#    override(a.func1,p3)
#    override(a.func0,o3)
    a.func0()
    a.func1('b')
    override(a.func1,p3)
    print a.func1
    a.func1('b')
    
    print C.func0
    print b.func0
    b.func0()
    
    
    
