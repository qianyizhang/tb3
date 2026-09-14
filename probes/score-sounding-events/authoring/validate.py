"""A transcription recorded from the four rendered raster images, plus grader controls."""
import json,sys,hashlib,importlib.util
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).parents[1]

# Rows are sounding MIDI pitch, zero-based onset, duration. Written after visual
# review of staff, clef, rhythm, accidental scope and ties in the emitted PNGs.
TREBLE_A=[(67,0,1),(69,1,1),(71,2,1),(72,3,3),(74,6,1),(76,7,1),
 (78,8,'3/2'),(76,'19/2','1/2'),(78,10,1),(72,11,1),
 (71,12,2),(74,12,2),(69,14,1),(67,15,1),
 (60,0,2),(64,2,2),(62,4,1),(65,5,1),(64,6,3),(62,10,1),(60,11,1),(62,12,2),(60,14,2)]
TREBLE_B=[(69,0,'1/2'),(67,'1/2','1/2'),(71,1,1),(69,2,1),(72,3,3),(74,6,1),(76,7,1),
 (75,8,1),(75,9,1),(76,10,1),(74,11,1),(71,12,2),(74,12,2),(69,14,1),(67,15,1),
 (60,0,2),(64,2,2),(62,4,1),(65,5,1),(64,6,3),(62,10,1),(60,11,1),(60,12,1),(62,14,1),(60,15,1)]

def manual():
    result=[]
    for i,(rows,shift) in enumerate([(TREBLE_A,0),(TREBLE_B,0),(TREBLE_A,-12),(TREBLE_B,-12)]):
        events=[]
        for pitch,onset,duration in rows:
            a=Fraction(onset);b=Fraction(duration)
            events.append(dict(midi_pitch=pitch+shift,onset_quarters=f'{a.numerator}/{a.denominator}',duration_quarters=f'{b.numerator}/{b.denominator}'))
        result.append(dict(excerpt_id=f'fragment_{i+1:02}',events=events))
    return result

def main():
    spec=importlib.util.spec_from_file_location('grade',ROOT/'tests/verifier.py');grade=importlib.util.module_from_spec(spec);spec.loader.exec_module(grade)
    transcription=manual();generated=json.loads((ROOT/'tests/golden-generated.json').read_text())
    assert all(grade.events(a['events'])==grade.events(b['events']) for a,b in zip(transcription,generated))
    (ROOT/'authoring/raster-transcription.json').write_text(json.dumps(transcription,indent=2)+'\n')
    (ROOT/'tests/golden.json').write_text(json.dumps(transcription,indent=2)+'\n')
    import copy
    controls={}
    variants={'independent_transcription':transcription,'empty':[dict(excerpt_id=x['excerpt_id'],events=[]) for x in transcription]}
    untied=copy.deepcopy(transcription)
    for x in untied:
        for e in x['events'][:]:
            if Fraction(e['duration_quarters'])==3:
                start=Fraction(e['onset_quarters']);e['duration_quarters']='1/1'
                x['events'].append(dict(midi_pitch=e['midi_pitch'],onset_quarters=f'{start+1}/1',duration_quarters='2/1'))
    variants['split_ties']=untied
    serial=copy.deepcopy(transcription)
    for x in serial:
        t=Fraction(0)
        for e in x['events']:
            e['onset_quarters']=str(t);t+=Fraction(e['duration_quarters'])
    variants['serialize_voices']=serial
    bad_acc=copy.deepcopy(transcription)
    for x in bad_acc:
        for e in x['events']:
            if Fraction(e['onset_quarters'])==10 and e['midi_pitch'] in [78,66]:e['midi_pitch']-=1
            if Fraction(e['onset_quarters'])==9 and e['midi_pitch'] in [75,63]:e['midi_pitch']+=1
    variants['forget_accidental_scope']=bad_acc
    for name,v in variants.items():controls[name]=grade.compare(transcription,v)
    assert controls['independent_transcription']['accepted']
    assert all(not v['accepted'] for k,v in controls.items() if k!='independent_transcription')
    print(json.dumps(dict(excerpts=4,notation_templates=2,sounding_events=sum(len(x['events']) for x in transcription),raster_review='All four final PNGs visually transcribed; matching generated notation/event truth.',png_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'environment/images').glob('*.png'))},controls=controls),indent=2))

if __name__=='__main__':main()
