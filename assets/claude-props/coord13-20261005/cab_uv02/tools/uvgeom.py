# exact float64 2D triangle helpers for UV2 QA (no bbox-only decisions)
import numpy as np
def sarea(p):
    (ax,ay),(bx,by),(cx,cy)=p
    return 0.5*((bx-ax)*(cy-ay)-(cx-ax)*(by-ay))
def _ccw(p):
    return p if sarea(p)>=0 else p[::-1]
def clip_area(a,b):
    """positive area of intersection of triangles a,b (3x2 float64). 0 if either degenerate."""
    if abs(sarea(a))==0.0 or abs(sarea(b))==0.0: return 0.0
    a=[tuple(x) for x in _ccw(np.asarray(a,float))]; b=[tuple(x) for x in _ccw(np.asarray(b,float))]
    out=a
    for i in range(3):
        if not out: break
        (x1,y1),(x2,y2)=b[i],b[(i+1)%3]
        inp=out; out=[]
        side=lambda p:(x2-x1)*(p[1]-y1)-(y2-y1)*(p[0]-x1)
        for j in range(len(inp)):
            P,Q=inp[j],inp[(j+1)%len(inp)]; sp,sq=side(P),side(Q)
            if sp>=0:
                out.append(P)
                if sq<0: t=sp/(sp-sq); out.append((P[0]+t*(Q[0]-P[0]),P[1]+t*(Q[1]-P[1])))
            elif sq>=0:
                t=sp/(sp-sq); out.append((P[0]+t*(Q[0]-P[0]),P[1]+t*(Q[1]-P[1])))
    if len(out)<3: return 0.0
    s=0.0
    for j in range(len(out)):
        s+=out[j][0]*out[(j+1)%len(out)][1]-out[(j+1)%len(out)][0]*out[j][1]
    return max(0.0,0.5*s)
def _pseg(p,a,b):
    ab=b-a; L=ab@ab
    t=0.0 if L==0 else min(1.0,max(0.0,((p-a)@ab)/L))
    return np.linalg.norm(p-(a+t*ab))
def _segx(a,b,c,d):
    def o(p,q,r): return np.sign((q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]))
    o1,o2,o3,o4=o(a,b,c),o(a,b,d),o(c,d,a),o(c,d,b)
    return (o1*o2<=0) and (o3*o4<=0) and not (o1==o2==o3==o4==0 and (max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]) or max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1])))
def _inside(p,t):
    s=[np.sign((t[(i+1)%3][0]-t[i][0])*(p[1]-t[i][1])-(t[(i+1)%3][1]-t[i][1])*(p[0]-t[i][0])) for i in range(3)]
    return (all(x>=0 for x in s) or all(x<=0 for x in s)) and abs(sarea(t))>0
def tri_dist(a,b):
    """exact Euclidean distance between closed triangles (0 if touching/overlapping)."""
    a=np.asarray(a,float); b=np.asarray(b,float)
    for i in range(3):
        for j in range(3):
            if _segx(a[i],a[(i+1)%3],b[j],b[(j+1)%3]): return 0.0
    if any(_inside(p,b) for p in a) or any(_inside(p,a) for p in b): return 0.0
    d=min(_pseg(a[i],b[j],b[(j+1)%3]) for i in range(3) for j in range(3))
    return min(d,min(_pseg(b[i],a[j],a[(j+1)%3]) for i in range(3) for j in range(3)))
class Grid:
    def __init__(s,tris,cell=1/64):
        s.c=cell; s.t=tris; s.g={}
        for k,t in enumerate(tris):
            lo=np.floor(t.min(0)/cell).astype(int); hi=np.floor(t.max(0)/cell).astype(int)
            for i in range(lo[0],hi[0]+1):
                for j in range(lo[1],hi[1]+1): s.g.setdefault((i,j),[]).append(k)
    def near(s,t,r):
        lo=np.floor((t.min(0)-r)/s.c).astype(int); hi=np.floor((t.max(0)+r)/s.c).astype(int); out=set()
        for i in range(lo[0],hi[0]+1):
            for j in range(lo[1],hi[1]+1): out.update(s.g.get((i,j),()))
        return out
