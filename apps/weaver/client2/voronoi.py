def calcCircumcenter(a0,a1,b0,b1,c0,c1):
    d=(a0-c0)*(b1-c1)-(b0-c0)*(a1-c1)
    x=( ((a0-c0)*(a0+c0)+(a1-c1)*(a1+c1))*(b1-c1)/2
       -((b0-c0)*(b0+c0)+(b1-c1)*(b1+c1))*(a1-c1)/2)/d
    y=( ((b0-c0)*(b0+c0)+(b1-c1)*(b1+c1))*(a0-c0)/2
       -((a0-c0)*(a0+c0)+(a1-c1)*(a1+c1))*(b0-c0)/2)/d
    return x,y

def calcDist(x1,y1,x2,y2):
    return (x2-x1)*(x2-x1)+(y2-y1)*(y2-y1)

def findNearest(x,y,points):
    ds=[(calcDist(x,y,p[0],p[1]),p) for p in points]
    ds.sort()
    return [d[1] for d in ds]


def makeSets(list,n):
    if n==1:
        return [[x] for x in list]
    else:
        r=[]
        for a in list:
            l2=list[:]
            l2.remove(a)
            for s in makeSets(l2,n-1):
                s2=s[:]
                s2.append(a)

                # yuck.  Okay, this sucks.  Do this better
                s3=s2[:]
                s3.sort()
                if s3==s2:
                    r.append(s2)            
        return r

def isCounterClockwise(p):
    s=0
    p=list(p)
    p.append(p[0])
    for i in range(len(p)-1):
        s+=p[i][0]*p[i+1][1]-p[i+1][0]*p[i][1]
    return s>0

def calcVoronoi(points):
    if len(points)==2:
        x1,y1=points[0]
        x2,y2=points[1]
        cx,cy=(x1+x2)/2,(y1+y2)/2
        dx,dy=(x2-x1),(y2-y1)
        rays=[]
        rays.append((cx,cy,-dy,dx,(0,1)))
        rays.append((cx,cy,dy,-dx,(0,1)))
        return rays,[]
    
    v=[]
    for p1,p2,p3 in makeSets(points,3):
        x,y=calcCircumcenter(p1[0],p1[1],p2[0],p2[1],p3[0],p3[1])
        nearest=findNearest(x,y,points)[:3]
        if p1 in nearest and p2 in nearest and p3 in nearest:
          v.append((x,y,p1,p2,p3))

    rays=[]
    lines=[]
    for i in range(len(v)):
        v1=v[i]
        x,y,p1,p2,p3=v1
        isccw=isCounterClockwise((p1,p2,p3))
        found12=0
        found23=0
        found13=0
        for v2 in v:
          if v2!=v1:
            if not found12 and p1 in v2 and p2 in v2:
                if v1>v2:  # only report one of these lines, not both identical ones
                    lines.append((x,y,v2[0],v2[1],(points.index(p1),points.index(p2))))
                found12=1
            elif not found13 and p1 in v2 and p3 in v2:
                if v1>v2:  # only report one of these lines, not both identical ones
                    lines.append((x,y,v2[0],v2[1],(points.index(p1),points.index(p3))))
                found13=1
            elif not found23 and p2 in v2 and p3 in v2:
                if v1>v2:  # only report one of these lines, not both identical ones
                    lines.append((x,y,v2[0],v2[1],(points.index(p2),points.index(p3))))
                found23=1
            
        if isccw:
            if not found12:
                rays.append((x,y,p2[1]-p1[1],p1[0]-p2[0],(points.index(p1),points.index(p2))))
            if not found23:
                rays.append((x,y,p3[1]-p2[1],p2[0]-p3[0],(points.index(p2),points.index(p3))))
            if not found13:
                rays.append((x,y,p1[1]-p3[1],p3[0]-p1[0],(points.index(p1),points.index(p3))))
        else:
            if not found12:
                rays.append((x,y,p1[1]-p2[1],p2[0]-p1[0],(points.index(p2),points.index(p1))))
            if not found23:
                rays.append((x,y,p2[1]-p3[1],p3[0]-p2[0],(points.index(p2),points.index(p3))))
            if not found13:
                rays.append((x,y,p3[1]-p1[1],p1[0]-p3[0],(points.index(p1),points.index(p3))))
            
    return rays,lines
    
                        
                            
                                 
                        
                        
