"""Build four source-bounded interpretation packs without models, labels or scores."""
from __future__ import annotations
import argparse,ast,hashlib,io,json
from pathlib import Path
from PIL import Image

KEYS=('healthagentbench','radagent','healthagentbench-tumor-tiles','healthagentbench-cxr-correction')
SRC=Path('.local/explainers/core-20260929/interpretation-a-source')
def root():
 for p in Path(__file__).resolve().parents:
  if (p/'presentation/EXPLAINER-SCOPE.json').exists():return p
 raise RuntimeError('tb3 root not found')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
def make(repo,key,out,receipt_path):
 if key not in KEYS:raise ValueError(key)
 if out.exists():raise FileExistsError(f'Refusing to overwrite {out}')
 receipt=json.loads(receipt_path.read_text());assert receipt['entry_id']==key and all(x.get('attempted_at') for x in receipt['attempts'])
 source_dir=repo/SRC;real=key=='healthagentbench-tumor-tiles';sources={}
 for pin in receipt['source_pins']:
  pinned=repo/pin['local_path'] if pin.get('local_path') else (repo/'.local/explainers/completion-20260927/041-source' if key=='radagent' else source_dir/'pinned-source')/pin['path']
  assert pinned.is_file() and pinned.stat().st_size==pin['bytes'] and sha(pinned)==pin['sha256'], pinned
  sources[str(pinned.relative_to(repo))]=pin['sha256']
 if real:
  ex=receipt['source_example'];tile=source_dir/'tumor-076-overview-tile.bin';tables=source_dir/'tumor-076-jpeg-tables.bin'
  assert sha(tile)==ex['overview_tile_sha256'] and sha(tables)==ex['jpeg_tables_sha256']
  sources[str(tile.relative_to(repo))]=sha(tile);sources[str(tables.relative_to(repo))]=sha(tables)
 out.mkdir(parents=True)
 if real:
  image=Image.open(io.BytesIO(tables.read_bytes()[:-2]+tile.read_bytes()[2:]));image.load();assert image.size==(512,512)
  image.save(out/'overview.png',format='PNG',optimize=False);assert sha(out/'overview.png')==ex['overview_png_sha256']
  taskrow=source_dir/'pinned-source/tasks/tumor_area_selection_pathology_slide_0001/environment/workspace/benchmark_tasks.json';assert any(x['path'].endswith('/benchmark_tasks.json') and sha(taskrow)==x['sha256'] for x in receipt['source_pins'])
  row=json.loads(taskrow.read_text())[0];dump(out/'public-task-row.json',row);sources[str(taskrow.relative_to(repo))]=sha(taskrow)
  source={'role':'exact-source-WSI-overview-only','title':'CAMELYON16 slide_0001 whole-slide H&E','input':'/data/slide/current/slide.tif','overview':'overview.png','level0_width_px':ex['level0_width_px'],'level0_height_px':ex['level0_height_px'],'overview_width_px':512,'overview_height_px':512,'overview_content_height_px':448,'grid_cols':28,'grid_rows':25,'analysis_tile_size_px':256,'analysis_downsample':16,'tile_level0_px':4096,'task_id':'slide_0001','private_mask':None,'full_slide_bytes_retained':False}
  operation={'type':'whole-slide-grid-search','grid_formula':'x=floor(level0_pixel_x/4096), y=floor(level0_pixel_y/4096)','grid_domain':{'x':[0,27],'y':[0,24]},'last_row_level0_height_px':2048,'inspection_cursor_only':True,'tumor_threshold_from_public_row':row['tumor_threshold'],'tile_semantics':'A tile is positive in hidden mask derivation when at least 0.2 of its region is tumor; displayed overview cannot determine that status.','source_mask':None}
  output={'role':'required-schema-only','path':'/workspace/submission.json','schema':{'task_id':'slide_0001','instruction':'retain supplied instruction','contains_tumor':'boolean, not independently scored by pinned tile evaluator','predicted_tumor_tiles':'array of {x:int,y:int}'},'prediction':None,'score':None,'reference':None}
  notice={'label':'Exact slide overview; tumor labels unavailable','text':'This is the official slide_0001 source overview, not full-resolution search evidence. Hidden tumor mask, selected tiles, prediction and F1 are absent.','url':receipt['upstream_url'],'link_label':'Official CAMELYON16 source'}
 elif key=='healthagentbench':
  source={'role':'symbolic-input-socket','title':'HealthAgentBench exact CT case valid_16_a_1','input':'/workspace/data/scan.nii.gz','helper':'/workspace/data/labels.txt','actual_scan':None,'actual_requested_labels':None,'paired_report':None,'private_gold':None}
  operation={'type':'requested-finding-binary-table','step':'Read each name in labels.txt; inspect the 3D CT for that requested finding; write yes or no for every retained name.','requested_names':'not acquired','source_gold':'report-derived phrase-rule categories; evaluator-only','all_or_nothing_reward':True}
  output={'role':'required-schema-only','path':'/workspace/submission/predictions.txt','schema':'<exact name from labels.txt>: yes|no, one line per requested name','prediction':None,'score':None,'reference':None}
  notice={'label':'Symbolic workflow · CT-RATE case gated','text':'Exact CT, requested names and private gold are unavailable (HTTP 401). Request official CT-RATE access and stage the matched case; no patient answer is shown.','url':receipt['upstream_url'],'link_label':'Official CT-RATE access'}
 elif key=='radagent':
  runtime=repo/'.local/explainers/completion-20260927/041-source/minimal_inference/app/runtime/agent_runtime.py'
  constants={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(runtime.read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('ART_TOOL_NAMES','CHECKLIST')}
  checklist=[line.strip() for line in constants['CHECKLIST'].splitlines() if line.strip()];assert len(checklist)==9 and len(constants['ART_TOOL_NAMES'])==10
  source={'role':'symbolic-input-socket','title':'RadAgent chest CT report workflow','input':'CT NIfTI path passed to specialist services','actual_scan':None,'saved_tool_trace':None,'reference_report':None}
  operation={'type':'tool-assisted-reporting','steps':['v8c prompt directs report_generation_tool draft first; no observed sequence','Nine-item checklist with specialist classifier, VQA, segmentation, slice selection and windowing tools','Reconcile conflicts before final answer'],'action_schema':{'call_tool':'tool name + arguments + preliminary_findings','final_answer':'answer string'},'case_specific_tool_outputs':None,'max_assistant_steps':60,'tool_names':constants['ART_TOOL_NAMES'],'checklist':checklist}
  output={'role':'required-schema-only','path':'final assistant JSON action and saved trace','schema':'{"action":"final_answer","answer":"<report text>"}','prediction':None,'score':None,'reference':None}
  notice={'label':'Symbolic workflow · no matched CT or tool trace','text':'CT-RATE requires access; the pinned repository has no worked scan, specialist outputs, generated report or paired reference for this explainer. This workflow is symbolic.','url':receipt['upstream_url'],'link_label':'Official CT-RATE access'}
 else:
  source={'role':'symbolic-input-socket','title':'HealthAgentBench CXR report correction case_01','input':'/data/patient/study_NN/view_*.jpg','target_rule':'highest numbered study is current target','prior_reports':'not acquired','target_draft_findings':'not acquired','reference_report':None,'manifest_study_count':12}
  operation={'type':'constrained-findings-edit','steps':['Read chronological prior/current studies','Compare only existing draft FINDINGS claims with current X-ray and available history','Correct or remove unsupported existing claims; do not add new findings','Return FINDINGS only, no IMPRESSION'],'patient_findings':None}
  output={'role':'required-schema-only','path':'/workspace/submission.json','schema':{'task_id':'case_01','final_answer':'FINDINGS:\n<corrected existing claims only>'},'prediction':None,'score':None,'reference':None}
  notice={'label':'MIMIC-CXR case requires credentialed access','text':'No current/prior X-rays, draft FINDINGS or reference report were acquired. The displayed workflow is symbolic and contains no patient claims.','url':receipt['upstream_url'],'link_label':'Official MIMIC-CXR access'}
 source['notice']=notice
 dump(out/'source.json',source);dump(out/'operation.json',operation);dump(out/'output.json',output)
 (out/'NOTICE.md').write_text(notice['label']+'. '+notice['text']+' '+notice['url']+'\n')
 lic='LicenseRef-CAMELYON16-local-research' if real else 'LicenseRef-TB3-symbolic-teaching'
 (out/'DATA-LICENSE.txt').write_text(lic+'; task/source terms and local-use scope in resolution receipt.\n')
 assets=[{'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'provenance':'source-derived-teaching' if real else 'symbolic-protocol','role':'illustration'} for p in sorted(out.iterdir())]
 if not real: sources={f'presentation/external-tasks/sources/{key}-resolution.json':sha(receipt_path)}
 dump(out/'manifest.json',{'id':f'retained-{key}-interpretation-v1','frame':'native-WSI-level0-grid' if real else 'symbolic-task-workflow','units':'px' if real else 'none','license':lic,'label_license':lic,'reference_policy':'no-reference-assets','sources':sources,'checks':{'native_input':real,'private_reference':False,'model_run':False,'evaluator_run':False},'assets':assets})
def main():
 p=argparse.ArgumentParser();p.add_argument('--entry',choices=KEYS,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();make(root(),a.entry,a.output,a.receipt)
if __name__=='__main__':main()
