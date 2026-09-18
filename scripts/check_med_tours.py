#!/usr/bin/env python3
"""Check scientific display invariants, provenance, local links and video metadata."""
import argparse, hashlib, json, math, re, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOURS=ROOT/'site_med/tours'
def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def finite(values):
    if isinstance(values,list): return all(finite(v) for v in values)
    return isinstance(values,(int,float)) and math.isfinite(values)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--exports',action='store_true');args=ap.parse_args()
    prov=read(TOURS/'data/provenance.json')
    for name,digest in prov['sources'].items(): assert sha(ROOT/name)==digest,('source changed',name)
    for name,digest in prov['outputs'].items(): assert sha(TOURS/'data'/name)==digest,('derived data changed',name)
    stories=read(TOURS/'storyboards.json')
    for name,s in stories.items():
        assert s['steps'][0]['at']==0
        assert all(a['at']<b['at'] for a,b in zip(s['steps'],s['steps'][1:]))
        assert s['steps'][-1]['at']<s['duration']
    seg=read(TOURS/'data/segmentation.json')
    assert seg['transferred_ml']==21.04 and len(seg['frames'])==24
    assert abs(seg['frames'][seg['pointFrame']]['z_mm']-seg['point_lps_mm'][2])<1e-5
    assert all(0<=v<=1 for v in seg['pointUV'])
    for f in seg['frames']:
        assert set(f['images'])=={'before','after','region'}
        for filename in f['images'].values():assert (TOURS/'data'/filename).is_file()
    v=read(TOURS/'data/vessels.json');assert len(v['added'])==103
    assert v['cut_indices']==list(range(len(v['path'])))
    assert len(v['cuts'])==len(v['path'])==len(v['arc'])==371
    assert len(v['cpr'])==8
    cumulative=0
    for i in range(1,len(v['path'])):
        cumulative+=math.dist(v['path'][i-1],v['path'][i]);assert abs(cumulative-v['arc'][i])<.005
    assert abs(v['original_axis_length_mm']-v['saved_line_length_mm']-8.890774)<.001
    for m in [v['before'],v['after']]:
        assert finite(m['points']);assert all(len(f)==3 and min(f)>=0 and max(f)<len(m['points']) for f in m['faces'])
    c=read(TOURS/'data/cardiac.json');original=read(ROOT/'runs/br035-segmentation-mechanics/review/masks-synthetic/data.json')
    assert c['frames']==len(c['masks'])==30
    for m,source in zip(c['models'],original['models']):
        assert m['points']==source['points'] and m['faces']==source['faces'], 'cardiac geometry changed'
        assert finite(m['points'])
    tracks=c['material_tracks'];assert len(set(tracks['source_cells']))==24
    for a,b in zip(tracks['reference'][0],tracks['prediction'][0]):assert math.dist(a,b)<.0002
    assert all(len(frame)==24 and finite(frame) for key in ['reference','prediction'] for frame in tracks[key])
    assert 7.37<c['metrics']['strain_mae_pp'][2]<7.38
    r=read(TOURS/'data/registration.json');assert len(r['ids'])==8
    assert abs(r['methods']['Sol / full 3D source']['grade']['max_mm']-6.411513)<1e-5
    l=read(TOURS/'data/landmarks.json');full=l['cases']['ct-full'];crop=l['cases']['ct-partial']
    assert full['plane_index']==crop['plane_index']==263
    assert crop['shape'][2]==920 and full['shape'][2]==1214
    assert crop['targets']['T4']['reference']['status']=='out_of_fov'
    assert crop['targets']['T5']['reference']['status']=='observed'
    assert all(crop['targets'][k]['predictions']['sol-xhigh']['status']=='out_of_fov' for k in ['T4','T5'])
    a=read(TOURS/'data/aneurysm.json');cases=a['cases']
    assert set(cases)=={'N01','N02','N03'}
    assert cases['N02']['answer']==[[312,213,94]] and cases['N02']['accepted_prediction']
    assert not cases['N01']['grade']['passed'] and cases['N01']['answer']==[]
    assert cases['N03']['source_assisted'] and cases['N03']['answer']==[]
    for name in ['N01','N02']:
        c=cases[name];lo,hi=c['crop_bounds']
        for p in c['planes']:
            axis=p['axis'];axes=p['axes'];frames=p['frames']
            assert [f['index'] for f in frames]==list(range(c['reference_center'][axis]-12,c['reference_center'][axis]+13))
            assert abs(p['aspect']-(hi[axes[0]]-lo[axes[0]])*c['spacing'][axes[0]]/((hi[axes[1]]-lo[axes[1]])*c['spacing'][axes[1]]))<1e-9
            assert sum(f['mask_voxels'] for f in frames)==c['reference_voxels']
            if c['answer']:
                point=c['answer'][0]
                assert p['point_uv']==[(point[axes[0]]-lo[axes[0]]+.5)/(hi[axes[0]]-lo[axes[0]]),1-(point[axes[1]]-lo[axes[1]]+.5)/(hi[axes[1]]-lo[axes[1]])]
    for filename in a['image_files']:assert (TOURS/'data'/filename).is_file()
    for path in TOURS.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if not target.startswith(('http:','https:','#')):assert (path.parent/target.split('#')[0]).exists(), (path,target)
    if args.exports:
        manifest=read(TOURS/'exports/manifest.json')
        assert manifest['renderer_sha256']==sha(TOURS/'tour.js')
        assert manifest['storyboard_sha256']==sha(TOURS/'storyboards.json')
        assert manifest['data_provenance_sha256']==sha(TOURS/'data/provenance.json')
        assert len(manifest['videos'])==2*len(stories)
        probe=shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'
        for v in manifest['videos']:
            p=TOURS/'exports'/v['file'];assert sha(p)==v['sha256']
            metadata=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
            streams=metadata['streams'];assert len(streams)==1
            m=streams[0];assert m['codec_name']=='h264' and m['pix_fmt']=='yuv420p'
            assert (m['width'],m['height'])==(v['width'],v['height'])
            assert int(m['nb_frames'])==v['frames'] and abs(float(m['duration'])-v['seconds'])<.05
            assert m['avg_frame_rate']==str(v['fps'])+'/1'
        for name in stories:
            for ext in ['vtt','srt']:assert (TOURS/'exports'/f'{name}.{ext}').is_file()
    print(f'PASS: {len(prov["sources"])} source hashes, {len(prov["outputs"])} derived files, scientific display invariants, local links'+(', video manifests/streams' if args.exports else ''))
if __name__=='__main__':main()
