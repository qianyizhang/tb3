"""Build a frozen, independently solved geometry corpus before model trials."""
import copy,json,random,re
from pathlib import Path
from arrangement import solve

ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'environment/clipper2-src/fixtures/test_cpp_polytree.rs').read_text()
def rect(x0,y0,x1,y1):return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
def historical(name,op,rule):
    body=raw.split('fn '+name+'() {',1)[1].split('\n#[test]',1)[0]
    def paths(label):
        m=re.search(r'let '+label+r' = vec!\[(.*?)\];',body,re.S)
        if not m:return []
        return [[list(p) for p in zip(v[::2],v[1::2])]
                for a in re.findall(r'make_path64\(&\[(.*?)\]\)',m[1],re.S)
                for v in [[int(x) for x in re.findall(r'-?\d+',a)]]]
    return {'family':name,'op':op,'rule':rule,'subject':paths('subject'),'clip':paths('clip')}
base=[historical(n,o,r) for n,o,r in [
 ('test_polytree_holes4_issue_618','Union','NonZero'),
 ('test_polytree_holes5','Xor','NonZero'),
 ('test_polytree_holes6_issue_618','Xor','NonZero'),
 ('test_polytree_holes7_issue_618','Union','NonZero'),
 ('test_polytree_holes9_issue_957','Union','NonZero'),
 ('test_polytree_holes10_issue_973','Union','NonZero'),
 ('test_polytree_union2_issue_987','Union','EvenOdd')]]
for n in [3,5,7]:
    paths=[rect(0,0,120,8),rect(0,92,120,100),rect(0,8,8,92),rect(112,8,120,92)]
    paths += [rect(8+i*96//n,8,12+i*96//n,92) for i in range(1,n)]
    base.append({'family':f'joined_ladder_{n}','op':'Union','rule':'NonZero','subject':paths,'clip':[]})
for depth,rule in [(4,'EvenOdd'),(6,'NonZero'),(6,'Positive'),(6,'Negative')]:
    paths=[rect(i*6,i*6,120-i*6,120-i*6) for i in range(depth+1)]
    if rule!='EvenOdd':
        paths=[p if (i%2==0)==(rule!='Negative') else p[::-1] for i,p in enumerate(paths)]
    base.append({'family':f'nested_{depth}_{rule}','op':'Union','rule':rule,'subject':paths+[rect(140,0,160,20)],'clip':[]})
base.extend([
 {'family':'difference_window','op':'Difference','rule':'NonZero','subject':[rect(0,0,80,80)],'clip':[rect(15,15,65,65)]},
 {'family':'intersection_comb','op':'Intersection','rule':'NonZero','subject':[rect(i*15,0,i*15+8,70) for i in range(5)]+[rect(0,0,68,7)],'clip':[rect(-5,10,80,60)]},
 {'family':'signed_cancellation','op':'Union','rule':'NonZero','subject':[rect(0,0,70,70),rect(10,10,60,60)[::-1],rect(25,25,45,45)],'clip':[]},
 {'family':'empty_intersection','op':'Intersection','rule':'EvenOdd','subject':[rect(0,0,10,10)],'clip':[rect(20,20,30,30)]},
])
summary=[];solved=[]
for b in base:
    nodes,stats=solve(b);solved.append((b,nodes));summary.append({'family':b['family'],**stats})
transforms=[(1,0,1,0,0),(3,0,5,701,-359),(2,1,3,-1907,2251),(1,-2,1,18000,-22000)]
cases=[]
for b,nodes in solved:
    for transform in transforms:
        for permuted in [False,True]:
            sx,k,sy,dx,dy=transform
            def ring(r):return [[sx*x+k*y+dx,sy*y+dy] for x,y in r]
            c={key:copy.deepcopy(b[key]) for key in ['family','op','rule','subject','clip']}
            c['subject']=[ring(r) for r in c['subject']];c['clip']=[ring(r) for r in c['clip']]
            if permuted:
                rng=random.Random(730000+len(cases))
                for key in ['subject','clip']:
                    rng.shuffle(c[key])
                    for i,r in enumerate(c[key]):
                        n=rng.randrange(len(r));r=r[n:]+r[:n]
                        if i%2==0:r=r+[r[0]]
                        c[key][i]=r
            c.update(name=f'overlay-{len(cases):03d}',preserve=permuted,reverse=permuted,
                     expected=[{**n,'xy':ring(n['xy'])} for n in nodes],transform=list(transform),permuted=permuted)
            cases.append(c)
(ROOT/'tests/cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
public=[copy.deepcopy(cases[i]) for i in [0,8,80,136]]
for c in public:
    for k in ['family','transform','permuted']:c.pop(k)
(ROOT/'environment/examples.json').write_text(json.dumps(public,indent=2)+'\n')
(ROOT/'authoring/corpus-summary.json').write_text(json.dumps({'base_layouts':len(base),'total_cases':len(cases),'transforms_per_layout':4,'input_order_variants':2,'geometric_exclusions':[],'layouts':summary},indent=2)+'\n')
print(json.dumps({'base_layouts':len(base),'cases':len(cases),'max_depth':max(s['max_depth'] for s in summary)},indent=2))
