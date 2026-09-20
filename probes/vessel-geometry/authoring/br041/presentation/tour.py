"""Narrated, source-derived comparison video. Does not modify model artifacts."""
from pathlib import Path
import json,subprocess,textwrap,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;ROOT=H.parents[4];P=ROOT/'runs/br041-image-only-centerline/presentation';O=P/'tour';O.mkdir(exist_ok=True)
D=json.loads((P/'manifest.json').read_text());routes=D['routes'];W,Hh,FPS=1280,720,12
FONT='/System/Library/Fonts/Supplemental/Arial.ttf';BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
scenes=[
 dict(title='Three lines. Three different anatomical stories.',key='all',caption='The same CTA and named target; no supplied mask or endpoints. Geometry disagreement is not one kind of anatomical error.',speech='All three agents received the same coronary CT image and the same request: trace the right coronary artery into the right posterior descending artery. No mask or endpoint coordinates were supplied. We will compare where the routes agree, where they diverge, and what those differences mean.'),
 dict(title='Terra: the intended coronary route is missed.',key='terra',caption='The submitted line is spatially separate from the requested coronary route. This is a localization problem, not just an endpoint difference.',speech='Terra is the clearest localization miss. Its orange line is largely separate from the annotated coronary route. Bright contrast on a curved image is not enough to identify the artery. Here, the native spatial course and the reference comparison agree that this is a broad route mismatch.'),
 dict(title='Sol: accurate tracing, different distal branch.',key='sol',caption='Blue follows the shared RCA, then tracks the purple R-PLA reference. The traced artery is real; its named identity does not match the request.',speech='Sol is very different. It traces the shared right coronary artery closely, then follows the posterolateral branch, shown in purple, instead of the requested posterior descending branch in green. Against that alternative branch, its ninety fifth percentile distance is only zero point three five millimeters. This is a named branch selection error, not a general failure to extract a coronary centerline.'),
 dict(title='Astra: the requested R-PDA is closely followed.',key='astra',caption='The full annotated route is covered within 1 mm. Up to the reference endpoint, the 95th-percentile distance is 0.47 mm.',speech='Astra selects the requested posterior descending branch. Its gold line covers the entire annotated route within one millimeter. If we inspect only the portion through the annotation endpoint, its ninety fifth percentile distance is zero point four seven millimeters. The key remaining question is where to stop.'),
 dict(title='Astra: inspect the continuation, not just the score.',key='extension',caption='Gold continues ~15 mm beyond the green annotation endpoint. A plausible visible continuation may be preferable to stopping at the label boundary; this remains unadjudicated.',speech='Now follow Astra beyond the green annotation endpoint. It adds about fifteen millimeters of curved length through faint distal signal. The section on the right follows Astra, while the reference section stays at the annotated end. The extension may be plausible and could be preferable if the image supports a continuous lumen. But this case has no independent adjudication of that extent. A distance penalty cannot resolve the question.'),
 dict(title='Compare the reason for divergence.',key='summary',caption='Terra: localization mismatch. Sol: real artery, wrong requested branch. Astra: correct branch, plausible extra extent. Frozen scores describe annotation agreement.',speech='The useful comparison is therefore qualitative as well as geometric. Terra misses the route. Sol traces a real artery well but selects the wrong named branch. Astra follows the requested branch, with a plausible but unresolved distal extension. All three failed the original strict verifier, but those failures are not equivalent. Use the interactive viewer to inspect the original CT, especially Astra’s final segment.')]
colors={k:r['color'] for k,r in routes.items()};assets={}
for k,r in routes.items():
 n=len(r['path']);assets[k]=(np.fromfile(P/r['cpr'],dtype='<f4').reshape(8,n,65),np.fromfile(P/r['sections'],dtype='<f4').reshape(n,65,65));r['p']=np.array(r['path']);r['a']=np.array(r['arc'])
def txt(d,p,s,n=22,col='#eaf0f6',bold=False,width=None):
 if width:s='\n'.join(textwrap.wrap(s,width))
 d.multiline_text(p,s,font=font(n,bold),fill=col,spacing=7)
def gray(a,level=180,window=650):return Image.fromarray(np.uint8(np.clip((a-(level-window/2))/window,0,1)*255)).convert('RGB')
def projection(p,t):
 q=p-np.array(D['center']);yaw=-.3+.45*np.sin(t*np.pi);pitch=.32
 xx=q[:,0]*np.cos(yaw)+q[:,1]*np.sin(yaw);yy=-q[:,0]*np.sin(yaw)+q[:,1]*np.cos(yaw);zz=q[:,2]*np.cos(pitch)+yy*np.sin(pitch)
 return np.c_[335+xx*4.4,340-zz*4.4]
def render(si,frac):
 s=scenes[si];mode=s['key'];key='astra' if mode in ['all','extension','summary'] else mode;r=routes[key];im=Image.new('RGB',(W,Hh),'#0b121a');d=ImageDraw.Draw(im)
 txt(d,(30,20),'BR-041  /  IMAGE-ONLY CORONARY TRACING',15,'#55d8b4');txt(d,(30,53),s['title'],30,bold=True)
 d.rounded_rectangle((25,108,655,559),12,fill='#131f2b');d.rounded_rectangle((673,108,1255,559),12,fill='#131f2b')
 txt(d,(42,120),'Original route geometry · oblique RAS view',18,'#a7bacb')
 active=['terra','sol','astra'] if mode in ['all','summary'] else [key]
 for k in ['rpla','reference']+active:
  pts=projection(routes[k]['p'],frac);d.line([tuple(p) for p in pts],fill=colors[k],width=3 if k in active else 2)
 end=projection(routes['reference']['p'][[-1]],frac)[0];d.ellipse((end[0]-6,end[1]-6,end[0]+6,end[1]+6),outline=colors['reference'],width=3)
 if mode=='extension':idx=round(330+frac*(len(r['p'])-331))
 elif mode=='sol':idx=round((.6+.4*frac)*(len(r['p'])-1))
 elif mode=='astra':idx=round(frac*330)
 else:idx=round(frac*(len(r['p'])-1))
 idx=min(len(r['p'])-1,idx);p=projection(r['p'][[idx]],frac)[0];d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill='white')
 legend=[('reference','R-PDA annotation'),('rpla','R-PLA annotation')]+[(k,routes[k]['label']) for k in active]
 for j,(k,label) in enumerate(legend):
  x=42+(j%3)*195;y=508+(j//3)*23;d.line((x,y+8,x+18,y+8),fill=colors[k],width=3);txt(d,(x+23,y),label,14)
 # Source CPR uses actual physical arc, not point percentage.
 cpr,sec=assets[key];a=0;ids=np.searchsorted(r['a'],np.linspace(0,r['a'][-1],540)).clip(0,len(r['a'])-1);cp=gray(cpr[a,ids,:].T,120 if mode=='extension' else 250,360 if mode=='extension' else 800).resize((540,140));im.paste(cp,(693,151));txt(d,(693,121),r['label']+' · source CTA CPR',18)
 xx=693+r['a'][idx]/r['a'][-1]*540;d.line((xx,151,xx,291),fill=colors[key],width=2);txt(d,(695,272),'0 mm',13);txt(d,(1137,272),f"{r['a'][-1]:.1f} mm",13)
 ridx=r['referenceIndex'][idx];level,width=(120,360) if mode=='extension' else (250,800)
 for j,(data,label) in enumerate([(sec[idx],'Selected line'),(assets['reference'][1][ridx],'Nearest reference')]):
  x=705+j*275;im.paste(gray(data,level,width).resize((195,195)),(x,331));txt(d,(x,306),label,17,'#a7bacb');cx=x+97;cy=428;d.line((cx-5,cy,cx+5,cy),fill=colors[key] if j==0 else colors['reference'],width=1);d.line((cx,cy-5,cx,cy+5),fill=colors[key] if j==0 else colors['reference'],width=1)
 txt(d,(698,532),f"Position {r['a'][idx]:.1f} mm · sections 16 × 16 mm",15,'#a7bacb')
 txt(d,(32,585),s['caption'],24,width=100)
 txt(d,(32,683),'Author-generated CPR from unchanged submissions · annotation extent is not independent clinical adjudication',15,'#a7bacb');txt(d,(1160,683),f'{si+1} / {len(scenes)}',15)
 return im
chapters=[];elapsed=0
for i,s in enumerate(scenes):
 audio=O/f'{i:02}.aiff';subprocess.run(['say','-v','Samantha','-r','155','-o',str(audio),s['speech']],check=True)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(audio)],text=True));duration+=1.5;n=int(np.ceil(duration*FPS));duration=n/FPS
 target=O/f'{i:02}.mp4';cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{Hh}','-r',str(FPS),'-i','-','-i',str(audio),'-af','apad','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(target)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for j in range(n):proc.stdin.write(render(i,j/max(1,n-1)).tobytes())
 proc.stdin.close();assert proc.wait()==0
 if i in [0,2,4]:render(i,.6).save(O/f'preview-{i}.jpg',quality=92)
 chapters.append({'start':elapsed,'duration':duration,'title':s['title'],'route':'astra' if s['key'] in ['all','extension','summary'] else s['key'],'narration':s['speech'],'caption':s['caption']});elapsed+=duration;print(i,s['title'],duration,flush=True)
(O/'concat.txt').write_text(''.join(f"file '{i:02}.mp4'\n" for i in range(len(scenes))))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(O/'concat.txt'),'-c','copy','-movflags','+faststart',str(P/'guided-tour.mp4')],check=True)
(P/'tour-chapters.json').write_text(json.dumps(chapters,indent=2)+'\n');(P/'tour-transcript.md').write_text('# Guided comparison transcript\n\n'+ '\n\n'.join(f"## {c['title']}\n\n{c['narration']}" for c in chapters)+'\n')
receipt={'duration_seconds':elapsed,'chapters':len(chapters),'source_manifest_sha256':hashlib.sha256((P/'manifest.json').read_bytes()).hexdigest(),'video_sha256':hashlib.sha256((P/'guided-tour.mp4').read_bytes()).hexdigest(),'narration':'Local macOS Samantha speech synthesis','visuals':'Source-derived CPR and cross-sections, exact route geometry. No generative images.','interpretation':'Astra extension plausible and unresolved; not adjudicated as preferable to annotation.'};(P/'tour-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
