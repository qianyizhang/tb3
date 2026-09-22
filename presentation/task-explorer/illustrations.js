// Original vector drawings. Geometry, textures and example marks are conceptual,
// never loaded patient data, predictions, measured effects or evaluator answers.
function taskArt(e, output=false) {
  const k=e.illustration.kind, id=e.id, subject=e.illustration.subject || 'generic';
  const ink='#264851', muted='#698b94', blue='#79b6d2', teal='#52a999', amber='#dfaa64', rose='#c7839a';
  const r=(x,y,w,h,fill,extra='')=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="${fill}" ${extra}/>`;
  const c=(x,y,rad,fill,extra='')=>`<circle cx="${x}" cy="${y}" r="${rad}" fill="${fill}" ${extra}/>`;
  const oval=(x,y,rx,ry,fill,extra='')=>`<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="${fill}" ${extra}/>`;
  const line=(x,y,a,b,col=ink,w=2,extra='')=>`<line x1="${x}" y1="${y}" x2="${a}" y2="${b}" stroke="${col}" stroke-width="${w}" ${extra}/>`;
  const path=(d,col=ink,w=2,fill='none',extra='')=>`<path d="${d}" stroke="${col}" stroke-width="${w}" fill="${fill}" ${extra}/>`;
  const txt=(x,y,s,size=13,col=ink)=>`<text x="${x}" y="${y}" font-size="${size}" fill="${col}">${esc(s)}</text>`;
  const group=(x,y,s,body)=>`<g transform="translate(${x} ${y}) scale(${s})">${body}</g>`;
  const arrow=(x,y,a,b)=>line(x,y,a,b,teal,3)+`<g transform="translate(${a} ${b}) rotate(${Math.atan2(b-y,a-x)*180/Math.PI})">${path('M-7 -5L0 0L-7 5',teal,3)}</g>`;
  const dots=(n=60,col=muted)=>Array.from({length:n},(_,i)=>c(30+(i*47%260),25+(i*31%140),1.5,col,'opacity=".45"')).join('');
  const frame=body=>r(20,12,280,166,'#193c48')+body;
  const cells=(colored=false)=>Array.from({length:14},(_,i)=>{
    const x=40+(i*53%240),y=34+(i*41%128),col=colored?[blue,teal,rose,amber][i%4]:'#bac8d6';
    return oval(x,y,15+(i%3)*3,11+(i%4),col,'opacity=".85"')+c(x-2,y+1,4,colored?'#fff4':rose);
  }).join('');
  const vessel=(colored=false)=>path('M160 160L160 115L119 95L117 60M160 115L201 94L204 57M119 95L139 64L181 64L201 94M139 64L133 29M181 64L190 29M160 140L106 140L77 115M160 140L211 142L239 116',colored?teal:'#b3c8d1',8,'none','stroke-linecap="round" stroke-linejoin="round"')+(colored?path('M119 95L139 64L181 64L201 94',amber,8):'');
  const tissue=colored=>frame(cells(colored));
  const aorta=colored=>path('M122 98V63Q151 15 191 62L195 134M159 38L159 21M178 43L188 22M193 98L221 82M194 118L222 130M195 134L174 163M195 134L218 163',colored?teal:'#b3c8d1',8,'none','stroke-linecap="round" stroke-linejoin="round"');
  const airways=colored=>path('M159 35V76L125 104L108 132M125 104L99 102M159 76L198 104L215 132M198 104L224 101',colored?amber:'#b3c8d1',6,'none','stroke-linecap="round"');
  const scan=(colored=false)=>{
    if(subject==='tissue') return tissue(colored);
    if(subject==='skin') return frame(oval(160,94,92,70,'#ddc5b3')+path('M128 66Q171 35 197 75T171 138Q111 142 115 103Z',rose,2,colored?teal:'#765964'));
    if(subject==='wrist') return frame(path('M122 150L133 63M176 151L161 67','#d1dbdd',19)+[0,1,2,3].map(i=>oval(119+i*18,46+i%2*15,10,12,colored?teal:'#c7d5d9')).join(''));
    if(subject==='ultrasound') return frame(path('M160 25L57 151Q160 188 263 151Z',muted,1,'#718f99')+path('M112 102Q176 61 218 126',colored?teal:'#bed0d0',9));
    if(subject==='heart') return frame(path('M159 51C118 10 73 66 117 116L161 158L208 111C250 57 194 17 159 51Z',muted,2,'#a6bac2')+oval(143,72,19,20,'#426777')+oval(183,73,18,19,colored?teal:'#426777')+oval(149,115,18,26,'#426777')+oval(185,112,16,25,'#426777'));
    if(subject==='brain-vessels') return frame(vessel(colored));
    if(subject==='aorta') return frame(aorta(colored));
    if(subject==='vessels') return frame(airways(colored));
    if(subject==='airways') return frame(oval(119,104,36,50,colored?teal:'#4f7481')+oval(202,104,36,50,colored?teal:'#4f7481')+airways(colored));
    if(subject==='teeth') return frame(Array.from({length:10},(_,i)=>{
      const x=53+i*23,y=48+Math.abs(i-4.5)*8;
      return path(`M${x} ${y}q-10 4-7 20l4 29 6-13 7 13 3-29q3-20-13-20`,muted,1,colored?(e.illustration.mask_mode==='multiclass'?[teal,amber,blue,rose][i%4]:i===4?amber:'#cad5d9'):'#cad5d9');
    }).join(''));
    if(subject==='chest') return frame(oval(160,98,87,72,'#758f9b')+oval(124,94,30,53,colored?teal:'#2c515f')+oval(195,94,31,53,colored?blue:'#2c515f')+path('M161 42L161 147','#d7e3e5',6)+c(192,108,11,colored?amber:'#98aeba'));
    if(subject==='chest-ct') return frame(oval(160,97,106,66,'#a6bac2')+oval(116,91,34,43,'#2c515f')+oval(205,91,34,43,'#2c515f')+oval(163,113,20,23,'#7b98a3')+c(162,143,9,'#d5dedb')+c(208,107,7,colored?amber:'#91a7ad'));
    if(subject==='brain') return frame(oval(160,96,70,74,'#a6bac2')+oval(127,96,31,56,colored?blue:'#627f8e')+oval(193,96,31,56,colored?teal:'#627f8e')+path('M160 29Q149 66 163 95T159 160','#d3dfdc',3)+c(197,85,14,colored?amber:'#c5d2d1'));
    if(subject==='knee') return frame(path('M116 19L121 67Q108 99 136 103Q153 99 166 103Q194 99 185 68L188 19',muted,2,'#a6bac2')+path('M119 117Q148 108 185 119L184 176H125Z',muted,2,'#a6bac2')+path('M120 111Q157 103 187 113',teal,3)+oval(210,87,8,20,'#bed0d2'));
    if(subject==='breast') return frame(path('M71 79Q111 41 154 69Q162 77 170 69Q215 41 255 79L252 99Q230 151 191 128L161 104L129 128Q89 151 71 99Z',muted,2,'#8eaab3')+oval(112,98,28,23,'#587d8c')+oval(212,98,28,23,'#587d8c')+c(222,91,7,colored?amber:'#718e99'));
    if(subject==='prostate') return frame(oval(160,94,76,57,'#728f9a')+oval(160,100,44,35,colored?teal:'#a5bdc4')+oval(160,98,27,23,colored?blue:'#617f8b'));
    if(subject==='abdomen') return frame(oval(160,98,94,64,'#a2b7ba')+oval(121,96,26,20,colored?blue:'#466b78')+oval(200,95,25,21,colored?teal:'#466b78')+oval(160,133,14,10,colored?amber:'#dae3df')+path('M119 59Q162 37 194 63L186 84Q150 86 120 68',muted,1,colored?rose:'#78939b'));
    return frame(r(80,39,155,112,'#617f8e')+c(144,87,28,colored?teal:'#acbec5')+path('M176 76L217 139H150Z',muted,2,colored?amber:'#829ea9'));
  };
  const volume=(colored=true,axis='z')=>[0,1,2,3].map(z=>{
    const x=70+z*17,y=77-z*13;
    return path(`M${x} ${y}l113-25 61 56-115 28Z`,muted,1,'#cde5df','fill-opacity=".28"')+oval(x+90,y+14,40,15,colored?[blue,teal,rose,amber][z]:'#90a3ad','opacity=".65"');
  }).join('')+line(60,150,60,47,muted,2)+txt(44,41,axis);
  const doc=(title='')=>r(65,19,190,151,'#fff','stroke="#b8ced0"')+r(83,38,100,9,teal)+[0,1,2,3,4].map(i=>r(83,66+i*18,140-i%2*32,5,'#c8d9dc')).join('')+(title?txt(84,153,title):'');
  const table=(flags=false)=>r(25,26,270,138,'#fff','stroke="#b8ced0"')+[0,1,2,3,4,5].map(i=>{
    const y=29+i*22;
    return r(27,y,266,19,flags&&[2,4].includes(i)?'#f3d5b8':i===0?'#dcebe8':'#f1f5f4')+line(84,y,84,y+19,'#bdd0d0',1)+line(188,y,188,y+19,'#bdd0d0',1)+txt(39,y+14,i===0?'ID':String(i),11)+r(96,y+7,61,4,muted)+r(200,y+7,i%2?47:68,4,flags&&i===4?rose:muted);
  }).join('');
  const curve=(offset=0,col=blue)=>path('M'+Array.from({length:80},(_,i)=>`${25+i*3.4},${110+offset-42*Math.exp(-(((i-30)/6)**2))-24*Math.exp(-(((i-57)/8)**2))+Math.sin(i*1.8)*4}`).join('L'),col,2);
  const chart=body=>line(25,160,295,160,muted)+line(25,160,25,25,muted)+body;
  const grid=(phase=false)=>Array.from({length:160},(_,i)=>{
    const x=i%16,y=Math.floor(i/16),v=(Math.sin(x*.65+y*.48)+Math.cos(y*.9-x*.25)+2)/4;
    return r(24+x*17,15+y*16,16,15,phase?`hsl(${180+v*145} 42% ${32+v*36}%)`:`hsl(192 38% ${24+v*55}%)`);
  }).join('');
  const frequency=()=>frame(Array.from({length:25},(_,i)=>line(42,24+i*6,279,24+i*6,i%3===0?blue:'#294955',i%3===0?2:1)).join('')+c(160,96,15,amber,'opacity=".6"')+txt(40,160,'sampled lines',13,'#d7ecec'));
  const signals=()=>chart([0,1,2,3].map((_,i)=>path('M'+Array.from({length:70},(_,j)=>`${27+j*3.7},${36+i*33+Math.sin(j*.85+i)*12*Math.exp(-(((j-20-i*7)/14)**2))}`).join('L'),[blue,teal,rose,amber][i],2)).join(''));
  const spectrum=()=>chart(curve()+curve(17,rose)+curve(-14,teal));
  const field=()=>grid(true)+path('M27 139Q87 67 139 129T287 49','#fff',2)+path('M27 104Q87 32 139 94T287 14','#fff',1);
  const ring=()=>frame(oval(162,94,61,50,amber)+oval(166,95,39,31,'#193c48')+path('M126 56Q212 43 214 100',rose,11)+dots(22,'#9cbbc1'));
  const waves=()=>signals()+txt(240,180,'time',12);
  const projections=()=>{
    let out=c(158,94,65,'#e0ebea')+oval(159,94,24,36,muted);
    for(let i=0;i<5;i++) {
      const a=i*.62,x=158+91*Math.cos(a),y=94+75*Math.sin(a);
      out+=c(x,y,4,teal)+line(x,y,315-x,188-y,blue,1,'opacity=".7"');
    }
    return out;
  };
  const labels=(multi=false)=>{
    const names=e.illustration.labels || (multi?['finding A','finding B','finding C']:['class A','class B','class C']);
    return r(33,12,254,166,'#fff','stroke="#b8ced0"')+names.map((name,i)=>{
      const y=34+i*134/names.length;
      return c(51,y-4,5,multi||i===1?teal:'#fff','stroke="#69a69b"')+txt(67,y,name,Math.min(15,126/names.length));
    }).join('');
  };
  const optical=()=>group(8,5,.47,grid())+group(159,5,.47,grid(true))+txt(38,105,'amplitude',13)+txt(204,105,'phase',13)+Array.from({length:8},(_,i)=>{
    const a=i*Math.PI/4,x=160+77*Math.cos(a),y=144+33*Math.sin(a);
    return line(x,y,160,140,teal,1.5)+c(x,y,4,amber);
  }).join('')+oval(160,140,24,9,blue,'opacity=".8"');
  const cavity=(x,y,rx,ry,col=teal,mesh=false,extra='')=>oval(x,y,rx,ry,'none',`stroke="${col}" stroke-width="2.5" ${extra}`)+(mesh?path(`M${x} ${y-ry}L${x-rx} ${y}L${x} ${y+ry}L${x+rx} ${y}Z`,col,1)+line(x-rx,y,x+rx,y,col,1)+oval(x,y,rx*.45,ry,'none',`stroke="${col}" stroke-width="1"`):'');
  const screenCard=(rows)=>r(28,25,264,143,'#fff','stroke="#b8ced0"')+rows.map(([label,col],i)=>c(49,53+i*44,6,col)+txt(66,58+i*44,label,14)).join('');
  let art='';
  switch(k) {
    case 'segmenter_calibration':
      art=output?[0,1].map(i=>r(20+i*157,16,123,113,'#193c48')+oval(82+i*157,75,31,22,'none',`stroke="${blue}" stroke-width="2.5" stroke-dasharray="5 4"`)+oval(85+i*152,78-i*5,29+i*5,24-i*4,'none',`stroke="${teal}" stroke-width="3"`)+txt(59+i*157,148,i?'LiteMedSAM':'SAM2',13)).join('')+line(34,177,55,177,blue,2.5,'stroke-dasharray="5 4"')+txt(62,181,'reference',12)+line(165,177,186,177,teal,3)+txt(193,181,'prediction',12):scan()+r(84,66,71,61,'none',`stroke="${amber}" stroke-width="3" stroke-dasharray="6 4"`)+txt(79,175,'reference-derived box',12,'#e7eff1');
      break;
    case 'source_provenance':
      art=output?['Source evidence','Candidate task','Feasibility + limits'].map((label,i)=>r(40,13+i*61,240,41,'#fff','stroke="#b8ced0"')+txt(58,39+i*61,label,15)+(i<2?arrow(160,56+i*61,160,70+i*61):'')).join(''):group(4,18,.56,doc('source record'))+group(146,4,.53,doc('prior evidence'))+group(93,80,.46,scan())+path('M108 93L143 118M230 90L216 117',teal,2);
      break;
    case 'mask_shortcuts':
      art=output?line(52,146,283,146,muted)+line(52,146,52,30,muted)+txt(112,177,'object size',13)+txt(16,20,'position',13)+[[88,119,'A'],[163,82,'B'],[247,44,'C']].map(([x,y,label])=>c(x,y,7,teal)+txt(x+11,y+5,label,15)).join('')+path('M76 133L263 32',amber,2,'none','stroke-dasharray="5 4"'):frame([0,1,2].map(i=>oval(75+i*81,123-i*36,16+i*7,12+i*6,'#bdced2')+txt(68+i*81,162,String(i+1),13,'#e7eff1')).join(''));
      break;
    case 'anatomy_curation':
      art=output?screenCard([['Candidate with evidence',teal],['Hold: context missing',amber],['Exclude: ambiguous key',rose]]):[0,1,2,3,4].map(i=>path(`M66 ${21+i*29}q16-7 32 0l15-3v17l-15-3q-16 7-32 0l-12 3v-17Z`,muted,1,i===2?amber:'#9fbdc5')).join('')+group(121,18,.62,doc('source labels'))+txt(40,185,'vertebral masks',12)+c(110,84,12,'#f3e1ba')+txt(106,89,'?',15)+txt(179,146,'context?',13);
      break;
    case 'registration_diagnosis':
      art=output?r(18,18,284,68,'#fff','stroke="#b8ced0"')+txt(31,40,'Transform composition',14)+path('M46 67L102 51L146 67',blue,2)+arrow(160,61,202,61)+txt(214,67,'T(x)',17)+r(18,101,284,71,'#fff','stroke="#b8ced0"')+txt(31,123,'Search + correspondence',14)+r(48,135,68,24,'none',`stroke="${muted}" stroke-dasharray="4 3"`)+c(83,146,4,teal)+c(144,146,4,amber)+line(88,146,139,146,rose,2)+txt(177,152,'residual',13):group(0,20,.49,scan())+group(162,20,.49,scan())+c(86,69,5,amber)+c(256,79,5,teal)+path('M103 106Q160 157 238 105',rose,2,'none','stroke-dasharray="5 4"')+txt(30,173,'saved query',13)+txt(186,173,'saved match',13);
      break;
    case 'cardiac_contours':
      art=[0,1,2].map(i=>cavity(60+i*100,87,31-i*6,53-i*9,output?teal:blue,output)).join('')+arrow(38,156,284,156)+txt(58,183,output?'time-varying cavity mesh':'contours supplied at every phase',13);
      break;
    case 'cardiac_anchors':
      art=[0,1,2].map(i=>(output?cavity(61+i*99,87,32-i*6,50-i*8,i===1?teal:amber,true,i===1?'stroke-dasharray="5 4"':''):group(1+i*100,30,.37,scan())+(i!==1?cavity(62+i*99,68,12-i*2,19-i*3,amber):''))+txt(38+i*99,151,i===1?(output?'recover':'image'):'anchor',13)).join('')+arrow(42,171,281,171);
      break;
    case 'cardiac_material':
      art=output?cavity(149,89,62,53,teal,true)+cavity(156,84,54,60,blue,false,'stroke-dasharray="5 4"')+c(106,54,5,amber)+txt(88,45,'A',13)+c(149,142,5,rose)+txt(156,153,'B',13)+line(22,176,43,176,teal,3)+txt(49,180,'model',12)+line(160,176,181,176,blue,2,'stroke-dasharray="5 4"')+txt(187,180,'reference',12):cavity(91,90,39,63,blue,true)+c(64,46,5,amber)+txt(48,39,'A',13)+c(91,153,5,rose)+txt(101,165,'B',13)+group(160,35,.47,scan())+txt(29,183,'initial material mesh',12)+txt(187,149,'ultrasound',12);
      break;
    case 'vessel_source_screen':
      art=output?screenCard([['Check connection evidence',teal],['Record reference gaps',amber],['Admit, hold or exclude',muted]]):group(16,0,.9,frame(vessel()+r(127,53,31,23,'#193c48')+c(142,65,18,'none',`stroke="${amber}" stroke-width="2" stroke-dasharray="4 3"`)))+txt(252,64,'?',22,amber)+txt(49,182,'source topology needs review',12);
      break;
    case 'prediction_screen':
      art=output?screenCard([['Inspect prediction difference',teal],['Verify reference support',blue],['Decide task suitability',amber]]):group(16,0,.9,frame(path('M73 140L121 99L159 63L246 43M121 99L226 141',blue,5,'none','stroke-dasharray="6 5"')+path('M75 137L121 99L141 81M171 60L244 46M121 99L193 122',teal,4)+c(158,70,20,'none',`stroke="${amber}" stroke-width="2"`)))+line(34,182,56,182,teal,3)+txt(62,186,'prediction',12)+line(178,182,200,182,blue,3,'stroke-dasharray="5 4"')+txt(206,186,'reference',12);
      break;
    case 'nodule_outline':
      art=scan()+(output?c(192,108,17,'none',`stroke="${amber}" stroke-width="3"`):'');
      break;
    case 'ct_phantom':
      art=output?frame(oval(160,94,62,75,'#d9e0df')+oval(160,96,56,67,'#6b838d')+oval(143,96,16,43,'#193c48','transform="rotate(17 143 96)"')+oval(181,91,12,32,'#193c48','transform="rotate(-18 181 91)"')+oval(158,51,19,13,'#a8babf')):group(16,0,.9,frame(Array.from({length:15},(_,i)=>path(`M${40+i*16} 26Q${90+i*13} 73 ${40+i*16} 104Q${10+i*16} 137 ${40+i*16} 164`,i%3===0?'#c3d5d9':'#527785',8)).join('')))+txt(84,184,'sparse projection data',12);
      break;
    case 'route_unfold':
      art=output?path('M47 63L106 31L141 48L211 25L277 42',teal,5)+path('M106 31L141 48',amber,5)+r(34,95,252,62,'#193c48')+path('M45 126Q117 108 165 126T276 126','#a3b7bf',18)+line(45,126,276,126,amber,2,'stroke-dasharray="4 3"')+txt(96,182,'unfolded CT view',13):group(16,0,.9,frame(path('M47 128L106 80M141 97L211 74L277 91','#acbdc5',14)+c(123,88,29,'none',`stroke="${amber}" stroke-width="2" stroke-dasharray="5 4"`)+c(70,109,5,teal)+c(241,82,5,teal)))+txt(54,184,'local repair + route anchors',12);
      break;
    case 'anatomy_audit':
      art=output?doc('Affected label + witness')+c(254,127,7,amber):scan(true)+txt(55,178,'supplied spatial labels',12);
      break;
    case 'object_identity':
      art=oval(82,85,30,40,blue)+r(139,48,41,69,teal)+path('M239 42L284 122H207Z',amber,2,amber)+[0,1,2].map(i=>txt(51+i*86,157,output?['label A','label B','label C'][i]:['object 1','object 2','object 3'][i],13)).join('');
      break;
    case 'landmark_point':
      art=scan()+(output?c(175,92,6,amber)+path('M175 75V109M158 92H192',amber,2):txt(48,174,e.illustration.target_prompt || 'named target; location unknown',12));
      break;
    case 'candidate_judgment':
      art=output?doc('Tumor / benign / uncertain'):scan()+c(177,89,15,'none','stroke="#d6ad69" stroke-width="2"')+txt(47,175,'candidate center is supplied',12);
      break;
    case 'point_correspondence':
      art=group(0,18,.48,scan())+group(164,18,.48,scan())+c(87,66,5,amber)+(output || e.illustration.initial_candidate?c(output?240:260,output?76:56,5,teal):'')+txt(27,154,'query point',12)+txt(190,154,output?'matched point':e.illustration.initial_candidate?'initial candidate':'search target',12)+(output?arrow(106,90,217,90):'');
      break;
    case 'dynamic_mesh':
      art=output?[0,1,2].map(i=>oval(62+i*96,88,32-i*5,51-i*8,'none','stroke="#358e85" stroke-width="2"')+path(`M${62+i*96} ${37+i*8}L${30+i*101} 88L${62+i*96} ${139-i*8}L${94+i*91} 88Z`,blue,1)+line(30+i*101,88,94+i*91,88,blue,1)).join('')+arrow(30,166,287,166)+txt(119,188,'phase',12):e.illustration.input_form==='masks'?[0,1,2].map(i=>oval(64+i*96,88,30-i*5,49-i*8,teal)).join('')+txt(81,173,'supplied phase masks',12):scan();
      break;
    case 'route_repair':
      art=frame(path('M50 135L103 99L138 103M166 89L198 61L266 50',teal,7,'none','stroke-linecap="round"')+(output?path('M138 103L166 89',amber,7):''))+txt(66,176,output?'supported route / connection':'supplied route discontinuity',12);
      break;
    case 'route_discovery':
      art=output?frame(path('M60 142L122 103L166 53L254 42M122 103L216 130',teal,4))+txt(99,177,'named paths',12):scan();
      break;
    case 'classify': case 'multilabel':art=output?labels(k==='multilabel'):scan();break;
    case 'segment':
      art=scan(output);
      if(output && e.illustration.mask_mode==='binary') art=frame(subject==='aorta'?aorta(true):subject==='heart'?oval(183,73,18,19,teal):oval(162,96,34,27,teal))+txt(121,176,'target',13,'#d5ece6');
      if(output && e.illustration.mask_mode==='separate') art=group(1,25,.5,frame(oval(160,93,40,28,teal)))+group(158,25,.5,frame(c(175,89,13,amber)))+txt(55,147,'organ')+txt(208,147,'lesion');
      break;
    case 'detect':art=scan()+ (output?r(80,49,83,81,'none','stroke="#e9b362" stroke-width="3"')+r(180,93,59,59,'none','stroke="#62c6b4" stroke-width="3"'):'');break;
    case 'instances':art=tissue(output)+(output?txt(38,163,'1     2      3      4',16,'#ffffff'):'');break;
    case 'nuclei':art=tissue()+ (output?Array.from({length:14},(_,i)=>c(38+(i*53%240),35+(i*41%128),5,[teal,amber,blue][i%3],'stroke="white"')) .join(''):'');break;
    case 'tiles':art=Array.from({length:12},(_,i)=>group(10+i%4*77,14+Math.floor(i/4)*58,.22,tissue(output&&[2,5,10].includes(i)))).join('');break;
    case 'report':case 'caption':
      art=output?doc(k==='report'?'Findings / impression':'Image description'):scan();
      if(id==='healthagentbench-cxr-correction') art=output?doc('Corrected findings')+line(83,90,214,90,teal,5):group(0,25,.5,scan())+group(159,10,.52,doc('Draft findings'))+line(202,55,270,55,rose,3);
      if(subject==='breast') art=output?r(38,20,245,150,'#fff','stroke="#b8ced0"')+['Laterality','Lesion count','Enhancement','BI-RADS category'].map((s,i)=>txt(53,49+i*32,s,14)+line(223,49+i*32,266,49+i*32,muted,2)).join(''):group(0,18,.5,scan())+group(160,18,.5,scan(true))+txt(33,137,'pre-contrast')+txt(184,137,'post-contrast');
      break;
    case 'vqa':art=output?doc('Answer to the question'):scan()+c(265,42,22,'#f5e6be')+txt(258,50,'?',25);break;
    case 'quality':art=output?chart([0,1,2,3,4].map(i=>r(52+i*44,140-i*22,29,20+i*22,i===3?teal:'#c8d9dc')).join('')):scan()+dots(150);break;
    case 'denoise':art=scan()+(!output?dots(180,'#eddfce'):'');break;
    case 'superres':art=output?scan():group(15,5,.95,scan())+Array.from({length:14},(_,i)=>line(26+i*20,20,26+i*20,173,'#e4efed',1,'opacity=".5"')).join('')+Array.from({length:8},(_,i)=>line(27,25+i*20,288,25+i*20,'#e4efed',1,'opacity=".5"')).join('');break;
    case 'restore3d':art=volume(output)+(!output?dots(80):'');break;
    case 'synthesis':art=output?scan().replaceAll('#466b78','#e8ebe6').replaceAll('#a2b7ba','#526d75'):scan();break;
    case 'mri':art=output?scan():frequency();break;
    case 'mri_dynamic':art=[0,1,2].map(i=>group(i*93+9,28,.38,output?scan():frequency())).join('')+arrow(42,144,274,144)+txt(126,174,'time');break;
    case 'image_sequence':art=[0,1,2].map(i=>group(i*93+9,28,.38,tissue())+(!output?Array.from({length:4},(_,j)=>line(25+i*93+j*18,39,25+i*93+j*18,93,amber,3)).join(''):'')).join('')+arrow(42,144,274,144)+txt(126,174,'time');break;
    case 'tensor':art=output?Array.from({length:36},(_,i)=>oval(47+i%9*28,40+Math.floor(i/9)*36,13,4,[teal,blue,amber][i%3],`transform="rotate(${i*19} ${47+i%9*28} ${40+Math.floor(i/9)*36})"`)).join(''):spectrum();break;
    case 't2':art=output?grid():chart(path('M30 36Q90 111 285 149',teal,4)+[0,1,2,3,4].map(i=>c(42+i*48,45+102*(1-Math.exp(-i*.65)),4,amber)).join(''));break;
    case 'ct':art=output?scan():projections();break;
    case 'dualct':art=output?group(0,20,.5,scan(true))+group(157,20,.5,scan(true))+txt(38,153,'material A')+txt(200,153,'material B'):group(0,20,.5,projections())+group(157,20,.5,projections())+txt(35,153,'energy 1')+txt(192,153,'energy 2');break;
    case 'pet':art=output?grid()+c(170,86,19,amber,'opacity=".8"'):projections();break;
    case 'ultrasound':case 'photoacoustic':case 'soundmap':art=output?(k==='soundmap'?field():scan()):waves();break;
    case 'odt':art=output?volume():optical();break;
    case 'idt':art=output?volume():[0,1,2].map(i=>group(i*91+8,14+i*19,.38,grid())).join('')+txt(83,168,'intensity views');break;
    case 'diffraction':art=output?group(0,20,.5,grid())+group(158,20,.5,grid(true))+txt(38,154,'amplitude')+txt(210,154,'phase'):frame([0,1,2,3,4].map(i=>c(83+i*38,55+i%2*52,28,'none',`stroke="${blue}" stroke-width="2" opacity=".7"`)+c(83+i*38,55+i%2*52,12,amber,'opacity=".65"')).join(''));break;
    case 'opticalvolume':art=output?volume():grid()+Array.from({length:16},(_,i)=>c(53+i%4*69,34+Math.floor(i/4)*39,14,'none','stroke="#daecdc"')).join('');break;
    case 'molecules':art=output?volume(false)+[0,1,2,3,4,5].map(i=>c(105+i*19,56+i%3*24,4,rose)).join(''):frame(dots(70,amber));break;
    case 'lensless':art=output?scan():grid();break;
    case 'nlos':art=output?volume():path('M220 25V150H81',ink,9)+c(62,44,11,amber)+path('M62 44L213 65L131 144L88 107',teal,3)+r(58,81,37,53,blue)+txt(34,175,'hidden object',12);break;
    case 'wavefront':art=output?Array.from({length:7},(_,i)=>path(`M35 ${39+i*17}Q154 ${-16+i*20}285 ${39+i*17}`,teal,2)).join(''):Array.from({length:30},(_,i)=>c(53+i%6*44+Math.sin(i)*7,33+Math.floor(i/6)*30,4,blue)+line(53+i%6*44,33+Math.floor(i/6)*30,53+i%6*44+Math.sin(i)*7,33+Math.floor(i/6)*30,amber,2)).join('');break;
    case 'spectral':art=output?group(0,15,.48,grid(true))+group(161,15,.48,grid())+txt(43,148,'component A')+txt(194,148,'component B'):spectrum();break;
    case 'spectral_cube':art=output?volume(true,'λ')+txt(100,174,'31 wavelength bands'):grid()+Array.from({length:8},(_,i)=>r(35+i*32,20,15,145,ink,'opacity=".45"')).join('');break;
    case 'deflectometry':
      art=output?path('M163 30Q103 95 163 160Q206 95 163 30Z',teal,2,'#a9d2da')+line(77,95,249,95,muted,1,'stroke-dasharray="5 5"')+line(140,96,185,96,ink,2)+line(140,87,140,105,ink)+line(185,87,185,105,ink)+txt(202,78,'thickness',11)+path('M158 29Q204 61 203 107',amber,2)+txt(216,139,'curvature',11):[0,1].map(view=>group(view*158,18,.5,frame(Array.from({length:10},(_,i)=>path(`M${35+i*26} 25Q${85+i*14+view*20} 85 ${35+i*26} 165`,i%2?blue:'#c8dce2',10)).join('')))+txt(view*158+42,137,'camera '+(view+1))).join('');
      break;
    case 'temperature':art=output?line(120,30,120,137,muted,14)+line(120,80,120,140,amber,9)+c(120,146,16,amber)+txt(156,103,'T',29):spectrum();break;
    case 'phase':art=output?chart(path('M32 145Q150 151 280 35',teal,4)):chart(path('M30 140L88 76L88 140L147 76L147 140L205 76L205 140L280 60',blue,4));break;
    case 'astronomy':
      art=output?ring():frequency()+dots(20);
      if(id.includes('lucky-imaging')) art=frame(c(160,95,62,'#b5c6cc')+[0,1,2,3,4,5].map(i=>c(131+i%3*29,66+Math.floor(i/3)*45,10+i,output?'#78929b':'#9aafb7')).join(''));
      if(id.includes('shapelet')) art=output?frame(oval(160,95,54,28,blue,'transform="rotate(-25 160 95)"')+oval(160,95,14,9,amber)):frame(path('M102 139Q66 45 173 32M213 54Q254 106 193 153',blue,12));
      break;
    case 'astro_uncertainty':art=output?ring()+oval(162,94,73,62,'none','stroke="#c7839a" stroke-width="17" opacity=".4"')+txt(38,164,'uncertain structure',12,'#e2ebec'):frequency();break;
    case 'astro_dynamic':art=output?[0,1,2].map(i=>group(i*97+9,30,.33,ring())).join('')+arrow(48,133,275,133)+txt(119,165,'time'):signals();break;
    case 'astro_features':art=output?chart(path('M30 124Q96 55 154 95T288 40',teal,3)+path('M30 87Q98 131 164 110T288 122',rose,3)+txt(212,181,'time',12)):signals();break;
    case 'astro_volume':art=output?volume():ring();break;
    case 'planet':art=frame(c(155,95,output?19:62,output?'#49626c':amber)+c(247,131,5,output?teal:'#728d91')+(output?r(234,118,26,26,'none','stroke="#52a999" stroke-width="2"'):''));break;
    case 'geofield':art=output?field():field()+r(63,15,40,160,'#edf2ef','opacity=".9"')+r(157,15,61,160,'#edf2ef','opacity=".9"');break;
    case 'seismic':art=output?[0,1,2,3,4].map(i=>path(`M20 ${33+i*31}Q112 ${10+i*19}173 ${36+i*22}T300 ${33+i*28}`,[blue,teal,amber,rose,muted][i],12)).join(''):waves();break;
    case 'conductivity':art=output?oval(159,94,97,74,blue)+oval(130,79,33,24,amber)+oval(191,120,22,19,teal):oval(159,94,97,74,'#dfebe7')+Array.from({length:12},(_,i)=>{const a=i*Math.PI/6,x=159+98*Math.cos(a),y=94+74*Math.sin(a);return c(x,y,5,teal)+line(x,y,318-x,188-y,blue,1,'opacity=".5"')}).join('');break;
    case 'register':art=oval(148,94,65,65,blue,'opacity=".5"')+oval(output?148:176,output?94:79,65,65,rose,'opacity=".5"')+path('M80 94H241M148 25V162',ink,1,'none','stroke-dasharray="5 5"');break;
    case 'longitudinal':art=group(1,16,.5,scan())+group(159,16,.5,scan())+(output?path('M91 86Q160 142 250 86',teal,3)+c(91,86,13,'none','stroke="#d6ad69" stroke-width="3"')+c(250,86,17,'none','stroke="#d6ad69" stroke-width="3"'):'')+txt(36,154,'earlier')+txt(212,154,'later');break;
    case 'viewer':art=scan()+r(20,12,43,166,'#102c35')+[0,1,2,3].map(i=>r(29,28+i*34,23,23,i===(output?2:0)?teal:'#537782')).join('')+line(82,160,268,160,'#c3dddb',3)+c(output?223:129,160,6,amber);break;
    case 'metadata':art=output?doc('Requested field'):table()+txt(98,20,'study / series',12);break;
    case 'workflow':art=output?group(2,17,.57,scan(true))+group(164,18,.5,doc())+arrow(133,149,231,149):group(5,9,.65,scan())+r(203,42,96,41,'#daebe7')+r(203,106,96,41,'#dce5ef')+arrow(175,73,196,73)+path('M252 85V105',teal,3)+txt(215,68,'process')+txt(216,132,'analyze');break;
    case 'risk':art=output?r(43,83,235,15,'#cbdcdd')+r(43,83,139,15,teal)+c(182,91,8,ink)+txt(39,123,'0',15)+txt(269,123,'1',15)+txt(41,48,'one probability per test row',16)+txt(43,158,'illustrative marker',12):line(25,107,289,107,muted,3)+[0,1,2,3].map(i=>c(45+i*48,107,7,blue)+line(45+i*48,107,45+i*48,50+i%2*26,blue,2)).join('')+line(225,25,225,149,rose,3,'stroke-dasharray="5 5"')+r(230,31,62,108,'#f5e9ed')+txt(193,174,'cutoff',13)+txt(33,29,'observed history',13);break;
    case 'records':art=table(output)+(output?path('M275 85l5 5 11-13',rose,3)+path('M275 130l5 5 11-13',rose,3):'');break;
    case 'etl':art=output?table():[0,1,2].map(i=>group(6+i*93,20+i%2*53,.36,table())).join('');break;
    case 'trials':art=output?doc('trial identifiers')+[0,1,2].map(i=>path(`M218 ${70+i*24}l6 6 11-15`,teal,3)).join(''):group(3,25,.57,doc('patient note'))+group(153,0,.48,doc())+group(161,54,.48,doc('criteria'));break;
    case 'box3d':art=volume(false)+(output?path('M120 51L204 35L249 84L249 129L164 148L120 99ZM120 51L164 99L249 84M164 99V148',amber,3):'');break;
    case 'vesselgraph':art=output?vessel(true)+[ [119,95],[139,64],[181,64],[201,94] ].map(([x,y])=>c(x,y,7,amber)).join(''):frame(vessel());break;
    default:throw new Error('Unknown illustration kind: '+k);
  }
  return `<svg viewBox="0 0 320 190" role="img" aria-label="${esc((output?e.illustration.output:e.illustration.input)+' — conceptual drawing')}" xmlns="http://www.w3.org/2000/svg"><g font-family="system-ui,sans-serif">${art}</g></svg>`;
}
