"""Exact integer-cell Boolean geometry; independent of either Clipper source."""
from collections import defaultdict
from fractions import Fraction


def area2(ring):
    return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(ring,ring[1:]+ring[:1]))


def winding(ring,x2,y2):
    n=0
    for a,b in zip(ring,ring[1:]+ring[:1]):
        cross=(b[0]-a[0])*(y2-2*a[1])-(b[1]-a[1])*(x2-2*a[0])
        if 2*a[1]<=y2<2*b[1] and cross>0:n+=1
        if 2*b[1]<=y2<2*a[1] and cross<0:n-=1
    return n


def normalize(ring):
    clean=[]
    for p in ring:
        p=tuple(p)
        if not clean or clean[-1]!=p:clean.append(p)
    if len(clean)>1 and clean[-1]==clean[0]:clean.pop()
    changed=True
    while changed and len(clean)>3:
        changed=False
        for i,p in enumerate(clean):
            a,b=clean[i-1],clean[(i+1)%len(clean)]
            if a!=b and (p[0]-a[0])*(b[1]-p[1])==(p[1]-a[1])*(b[0]-p[0]) and (p[0]-a[0])*(p[0]-b[0])+(p[1]-a[1])*(p[1]-b[1])<=0:
                clean.pop(i);changed=True;break
    assert len(clean)>=3 and area2(clean)!=0
    return clean


def canonical_ring(ring):
    ring=normalize(ring)
    return min(tuple(r[i:]+r[:i]) for r in [ring,list(reversed(ring))] for i in range(len(r)))


def rings_to_nodes(rings):
    rings=[normalize(r) for r in rings]
    parents=[]
    for i,r in enumerate(rings):
        a,b=r[0],r[1];dx=b[0]-a[0];dy=b[1]-a[1]
        # Point strictly inside the geometric ring, using the edge's inward side.
        sign=1 if area2(r)>0 else -1
        p=((Fraction(a[0]+b[0],2)-sign*Fraction(dy,4*(abs(dx)+abs(dy)))),
           (Fraction(a[1]+b[1],2)+sign*Fraction(dx,4*(abs(dx)+abs(dy)))))
        choices=[j for j,q in enumerate(rings) if abs(area2(q))>abs(area2(r)) and winding(q,2*p[0],2*p[1])!=0]
        parents.append(min(choices,key=lambda j:abs(area2(rings[j]))) if choices else None)
    out=[]
    def emit(parent,depth):
        for i,r in enumerate(rings):
            if parents[i]==parent:
                assert (area2(r)>0)==(depth%2==0)
                out.append({'depth':depth,'hole':depth%2==1,'xy':r});emit(i,depth+1)
    emit(None,0)
    assert len(out)==len(rings)
    return out


def solve(case):
    paths=case['subject']+case['clip']
    xs=sorted({x for r in paths for x,y in r});ys=sorted({y for r in paths for x,y in r})
    assert all(a[0]==b[0] or a[1]==b[1] for r in paths for a,b in zip(r,r[1:]+r[:1]))
    def filled(n):
        return {'EvenOdd':n%2!=0,'NonZero':n!=0,'Positive':n>0,'Negative':n<0}[case['rule']]
    cells=set()
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x2,y2=xs[i]+xs[i+1],ys[j]+ys[j+1]
            s=filled(sum(winding(r,x2,y2) for r in case['subject']))
            c=filled(sum(winding(r,x2,y2) for r in case['clip']))
            if {'Union':s or c,'Intersection':s and c,'Difference':s and not c,'Xor':s!=c}[case['op']]:cells.add((i,j))
    edges=set()
    for i,j in cells:
        points=[(xs[i],ys[j]),(xs[i+1],ys[j]),(xs[i+1],ys[j+1]),(xs[i],ys[j+1])]
        for a,b in zip(points,points[1:]+points[:1]):
            if (b,a) in edges:edges.remove((b,a))
            else:edges.add((a,b))
    outgoing=defaultdict(list)
    for a,b in edges:outgoing[a].append(b)
    def direction(a,b):
        return 0 if b[0]>a[0] else 1 if b[1]>a[1] else 2 if b[0]<a[0] else 3
    rings=[]
    while edges:
        a,b=min(edges);start=a;ring=[a]
        while True:
            edges.remove((a,b))
            if b==start:break
            ring.append(b)
            candidates=[q for q in outgoing[b] if (b,q) in edges]
            assert candidates
            incoming=direction(a,b)
            # At point-touching components, keep the filled face on the left.
            q=min(candidates,key=lambda q:{1:0,0:1,3:2,2:3}[(direction(b,q)-incoming)%4])
            a,b=b,q
        rings.append(ring)
    nodes=rings_to_nodes(rings)
    exact_area=sum((xs[i+1]-xs[i])*(ys[j+1]-ys[j]) for i,j in cells)
    assert sum((-1 if n['hole'] else 1)*abs(area2(n['xy'])) for n in nodes)==2*exact_area
    return nodes,{'cells':len(cells),'area':exact_area,'roots':sum(n['depth']==0 for n in nodes),'holes':sum(n['hole'] for n in nodes),'max_depth':max([n['depth'] for n in nodes],default=-1)}
