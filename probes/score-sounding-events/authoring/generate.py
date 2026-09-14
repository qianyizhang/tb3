"""Original notation fixtures rendered with pinned Verovio and resvg."""
import json, re
from pathlib import Path
from fractions import Fraction
from xml.etree.ElementTree import Element,SubElement,tostring
import verovio,resvg_py

ROOT=Path(__file__).parents[1]
def node(parent,tag,text=None,**attrs):
    n=SubElement(parent,tag,attrs)
    if text is not None:n.text=str(text)
    return n

# Entry: pitches or rest, eighth-note duration, tie status.
TOP=[
 [('G4',2,''),('A4',2,''),('B4',2,''),('C5',2,'start')],
 [('C5',4,'stop'),('D5',2,''),('E5',2,'')],
 [('F#5',3,''),('E5',1,''),('F#5',2,''),('C5',2,'')],
 [('B4+D5',4,''),('A4',2,''),('G4',2,'')]]
BOTTOM=[
 [('C4',4,''),('E4',4,'')],
 [('D4',2,''),('F4',2,''),('E4',4,'start')],
 [('E4',2,'stop'),('rest',2,''),('D4',2,''),('C4',2,'')],
 [('D4',4,''),('C4',4,'')]]

def pitch(s,octave_shift):
    m=re.fullmatch(r'([A-G])([#b]?)([0-9])',s)
    step,acc,oct=m.groups();alter={'':0,'#':1,'b':-1}[acc];oct=int(oct)+octave_shift
    midi=12*(oct+1)+dict(C=0,D=2,E=4,F=5,G=7,A=9,B=11)[step]+alter
    return step,alter,oct,midi

def create(index):
    # Variants alter rhythm/order and accidental choice as well as clef/register.
    import copy
    top=copy.deepcopy(TOP);bottom=copy.deepcopy(BOTTOM)
    if index in [1,3]:
        top[0]=[('A4',1,''),('G4',1,''),('B4',2,''),('A4',2,''),('C5',2,'start')]
        top[2]=[('Eb5',2,''),('Eb5',2,''),('E5',2,''),('D5',2,'')]
        bottom[3]=[('C4',2,''),('rest',2,''),('D4',2,''),('C4',2,'')]
    shift=[0,0,-1,-1][index]
    score=Element('score-partwise',version='4.0')
    plist=node(score,'part-list');sp=node(plist,'score-part',id='P1');node(sp,'part-name','')
    part=node(score,'part',id='P1')
    events=[];pending={}
    for b in range(4):
        measure=node(part,'measure',number=str(b+1))
        if b==0:
            attrs=node(measure,'attributes');node(attrs,'divisions',2)
            key=node(attrs,'key');node(key,'fifths',0)
            time=node(attrs,'time');node(time,'beats',4);node(time,'beat-type',4)
            clef=node(attrs,'clef');node(clef,'sign','G' if index<2 else 'F');node(clef,'line',2 if index<2 else 4)
        # Each voice's explicit accidental indications are reset by the barline.
        for voice,bars in [(1,top),(2,bottom)]:
            if voice==2:node(node(measure,'backup'),'duration',8)
            onset=Fraction(4*b);accidentals={}
            assert sum(n[1] for n in bars[b])==8
            for names,duration,tie in bars[b]:
                for chord_idx,name in enumerate(names.split('+')):
                    n=node(measure,'note')
                    if chord_idx:node(n,'chord')
                    if name=='rest':node(n,'rest')
                    else:
                        step,alter,oct,midi=pitch(name,shift);p=node(n,'pitch');node(p,'step',step)
                        if alter:node(p,'alter',alter)
                        node(p,'octave',oct)
                    node(n,'duration',duration)
                    if tie:node(n,'tie',type=tie)
                    node(n,'voice',voice)
                    node(n,'type',{1:'eighth',2:'quarter',3:'quarter',4:'half'}[duration])
                    if duration==3:node(n,'dot')
                    if name!='rest':
                        old=accidentals.get((step,oct),0)
                        if old!=alter:node(n,'accidental',{-1:'flat',0:'natural',1:'sharp'}[alter])
                        accidentals[(step,oct)]=alter
                        node(n,'stem','up' if voice==1 else 'down')
                        if tie:node(node(n,'notations'),'tied',type=tie)
                        key=(voice,midi)
                        if tie=='stop':
                            e=pending.pop(key);e['duration_quarters']=str(Fraction(e['duration_quarters'])+Fraction(duration,2))
                        else:
                            e=dict(midi_pitch=midi,onset_quarters=str(onset),duration_quarters=str(Fraction(duration,2)))
                            events.append(e)
                            if tie=='start':pending[key]=e
                onset+=Fraction(duration,2)
        if b==3:node(node(measure,'barline',location='right'),'bar-style','light-heavy')
    assert not pending
    xml='<?xml version="1.0" encoding="UTF-8"?>\n'+tostring(score,encoding='unicode')
    return xml,events

def main():
    for p in [ROOT/'authoring/notation',ROOT/'environment/images',ROOT/'tests']:
        p.mkdir(parents=True,exist_ok=True)
    golden=[]
    for i in range(4):
        name=f'fragment_{i+1:02}';xml,events=create(i)
        (ROOT/f'authoring/notation/{name}.musicxml').write_text(xml+'\n')
        toolkit=verovio.toolkit();toolkit.setOptions(dict(pageWidth=2600,pageHeight=1000,scale=60,adjustPageHeight=True,breaks='none',header='none',footer='none',spacingLinear=.45,spacingNonLinear=.6))
        assert toolkit.loadData(xml)
        assert toolkit.getPageCount()==1
        svg=toolkit.renderToSVG(1)
        # SVG and machine-readable notation stay author-side. PNG has no notation metadata.
        (ROOT/f'authoring/notation/{name}.svg').write_text(svg)
        png=resvg_py.svg_to_bytes(svg_string=svg,background='white',width=2200)
        (ROOT/f'environment/images/{name}.png').write_bytes(png)
        for e in events:
            for key in ['onset_quarters','duration_quarters']:
                q=Fraction(e[key]);e[key]=f'{q.numerator}/{q.denominator}'
        golden.append(dict(excerpt_id=name,events=events))
    (ROOT/'tests/golden-generated.json').write_text(json.dumps(golden,indent=2)+'\n')
    print(json.dumps(dict(renderer=verovio.toolkit().getVersion(),excerpt_events={x['excerpt_id']:len(x['events']) for x in golden}),indent=2))

if __name__=='__main__':main()
