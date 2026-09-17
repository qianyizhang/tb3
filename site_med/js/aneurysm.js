/* Portable guided views, upgraded to native-array exploration by serve_site.py. */
(() => {
  const cases = JSON.parse(document.getElementById('scan-data').textContent).cases;
  const local = JSON.parse(document.getElementById('local-scans')?.textContent || 'null');
  const names = ['Side · sagittal', 'Front · coronal', 'Top · axial'];
  const directions = ['patient right', 'front of head', 'top of head'];
  let current = null, pending = null;

  for (const [id, data] of Object.entries(cases)) {
    const root = document.querySelector(`[data-scan="${id}"]`);
    const $ = selector => root.querySelector(selector);
    const state = { axis: data.default_axis, marks: true, cursor: [...data.center], volume: null, serial: 0 };
    const images = data.planes.map(plane => { const image = new Image(); image.src = plane.image; return image; });
    const panels = data.planes.map((plane, axis) => {
      const box = document.createElement('div'); box.className = 'scan-screen';
      box.innerHTML = `<h3>${names[axis]}</h3><canvas aria-label="${id.toUpperCase()} ${names[axis]} scan"></canvas><div class="slice-row" hidden><label for="${id}-slice-${axis}">Slice</label><input id="${id}-slice-${axis}" type="range" min="0" max="${data.shape[axis]-1}" step="1"><output></output></div><div class="axis-labels"></div>`;
      $('.scan-views').append(box);
      const canvas = box.querySelector('canvas'), slider = box.querySelector('input');
      const panel = {axis, box, canvas, slider, offset:plane.offset};
      slider.oninput = () => { state.cursor[axis] = +slider.value; draw(); };
      canvas.onclick = event => {
        if (!state.volume) return;
        const rect = canvas.getBoundingClientRect(), rem = [0,1,2].filter(d => d !== axis);
        state.cursor[rem[0]] = clamp(panel.offset[0] + Math.round((event.clientX-rect.left)/rect.width*(canvas.width-1)), rem[0]);
        state.cursor[rem[1]] = clamp(panel.offset[1] + Math.round((1-(event.clientY-rect.top)/rect.height)*(canvas.height-1)), rem[1]);
        draw();
      };
      canvas.addEventListener('wheel', event => {
        if (!state.volume) return;
        event.preventDefault(); state.cursor[axis] = clamp(state.cursor[axis] + Math.sign(event.deltaY), axis); draw();
      }, {passive:false});
      return panel;
    });
    function clamp(value, axis) { return Math.min(data.shape[axis]-1, Math.max(0, value)); }
    function marks(ctx, panel, slab) {
      const axis = panel.axis, rem = [0,1,2].filter(d => d !== axis), h = panel.canvas.height;
      function point(coordinate) { return [coordinate[rem[0]]-panel.offset[0], h-1-(coordinate[rem[1]]-panel.offset[1])]; }
      if (state.volume) {
        const [x,y] = point(state.cursor);
        ctx.strokeStyle = '#58dcff'; ctx.lineWidth = .7; ctx.beginPath();
        ctx.moveTo(x,0);ctx.lineTo(x,y-5);ctx.moveTo(x,y+5);ctx.lineTo(x,h);
        ctx.moveTo(0,y);ctx.lineTo(x-5,y);ctx.moveTo(x+5,y);ctx.lineTo(panel.canvas.width,y);ctx.stroke();
      }
      if (!state.marks) return;
      const depth = state.volume ? state.cursor[axis] : data.center[axis];
      if (data.reference && Math.abs(data.center[axis]-depth) <= slab + data.reference.extent_mm[axis]/data.spacing[axis]/2) {
        const [x,y] = point(data.center);
        ctx.strokeStyle = '#ffdb69'; ctx.lineWidth = 1.1; ctx.beginPath();
        // A 3.5 mm guide ring stays circular after voxel-spacing correction.
        ctx.ellipse(x,y,3.5/data.spacing[rem[0]],3.5/data.spacing[rem[1]],0,0,Math.PI*2);ctx.stroke();
      }
      if (data.answer && Math.abs(data.answer[axis]-depth) <= slab) {
        const [x,y] = point(data.answer);
        const rx=1.3/data.spacing[rem[0]],ry=1.3/data.spacing[rem[1]];
        ctx.strokeStyle = '#ff81bd';ctx.lineWidth = 1.2;ctx.beginPath();ctx.moveTo(x,y-ry);ctx.lineTo(x+rx,y);ctx.lineTo(x,y+ry);ctx.lineTo(x-rx,y);ctx.closePath();ctx.stroke();
      }
    }
    function draw() {
      const live = Boolean(state.volume), zoom = +$('[data-zoom]').value, slab = live ? +$('[data-slab]').value : 3;
      root.classList.toggle('is-live',live);
      for (const panel of panels) {
        const axis=panel.axis, rem=[0,1,2].filter(d=>d!==axis), canvas=panel.canvas, plane=data.planes[axis];
        panel.box.hidden = !live && axis !== state.axis;
        if (panel.box.hidden) continue;
        const w=live?Math.ceil(data.shape[rem[0]]/zoom):plane.width, h=live?Math.ceil(data.shape[rem[1]]/zoom):plane.height;
        panel.offset=live?rem.map((d,n)=>Math.max(0,Math.min(data.shape[d]-[w,h][n],Math.round(state.cursor[d]-[w,h][n]/2)))):plane.offset;
        canvas.width=w;canvas.height=h;canvas.dataset.live=String(live);
        const aspect=w*data.spacing[rem[0]]/(h*data.spacing[rem[1]]);
        canvas.style.aspectRatio=String(aspect);canvas.style.width=`min(100%, ${420*aspect}px)`;
        const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;
        if (live) {
          const high=Math.max(1, +$('[data-high]').value || data.high), stride=[data.shape[1]*data.shape[2],data.shape[2],1];
          const pixels=ctx.createImageData(w,h), lo=Math.max(0,state.cursor[axis]-slab),hi=Math.min(data.shape[axis]-1,state.cursor[axis]+slab);
          for(let y=0;y<h;y++)for(let x=0;x<w;x++) {
            const base=(x+panel.offset[0])*stride[rem[0]]+(h-1-y+panel.offset[1])*stride[rem[1]];
            let value=-Infinity;for(let d=lo;d<=hi;d++)value=Math.max(value,state.volume[base+d*stride[axis]]);
            const gray=Math.max(0,Math.min(255,Math.round(value/high*255))),i=(y*w+x)*4;
            pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=gray;pixels.data[i+3]=255;
          }
          ctx.putImageData(pixels,0,0);
        } else if (images[axis].complete && images[axis].naturalWidth) ctx.drawImage(images[axis],0,0);
        else { images[axis].onload=draw; continue; }
        marks(ctx,panel,slab);
        panel.slider.value=state.cursor[axis];panel.box.querySelector('.slice-row').hidden=!live;
        panel.box.querySelector('output').textContent=state.cursor[axis];
        const center=live?state.cursor[axis]:plane.slice;
        panel.box.querySelector('.axis-labels').textContent=`Right on image → ${directions[rem[0]]} · Up → ${directions[rem[1]]}. ${'ijk'[axis]} = ${center}${slab?` · brightest of ${Math.min(data.shape[axis]-1,center+slab)-Math.max(0,center-slab)+1} slices`:' · single slice'}.`;
      }
      root.querySelectorAll('[data-plane]').forEach(button=>button.setAttribute('aria-pressed',String(+button.dataset.plane===state.axis)));
      $('.scan-plane-buttons').hidden=live;
      $('[data-coordinates]').textContent=live?`Cursor [${state.cursor.join(', ')}] · ${data.shape.join(' × ')} voxels`:data.reference?`Reference [${data.center.join(', ')}]${data.answer?` · Sol [${data.answer.join(', ')}]`:''}`:'No source reference point.';
      $('[data-cursor-legend]').hidden=!live;
    }
    function portable() {
      state.serial++;state.volume=null;
      $('[data-local-controls]').hidden=true;$('[data-explore]').textContent='Explore full scan';
      $('[data-explore]').disabled=false;
      $('[data-status]').textContent='Guided figure restored. Choose Explore full scan to return to every slice.';draw();
    }
    async function loadVolume() {
      if (pending) pending.abort();
      if (current && current.root!==root) current.release();
      const controller=new AbortController();pending=controller;current={root,release:portable};
      const serial=++state.serial;
      const button=$('[data-explore]'), status=$('[data-status]');button.disabled=true;
      status.textContent='Loading the full scan from this computer…';
      try {
        const response=await fetch(`${local.base}${data.source_id}/${$('[data-volume]').value}.bin`,{signal:controller.signal});
        if(!response.ok)throw new Error('The scan file is unavailable. Restore the local scan archive, then try again.');
        const buffer=await response.arrayBuffer();
        if(serial!==state.serial)return;
        if(buffer.byteLength!==data.shape.reduce((a,b)=>a*b,1)*4)throw new Error('The scan file has an unexpected size.');
        state.volume=new Float32Array(buffer);$('[data-local-controls]').hidden=false;
        button.textContent='Return to guided figure';
        status.textContent='Full scan ready. Drag the slice sliders or scroll over an image. Click to move the linked crosshairs. In combined slices, confirm depth with Single slice.';
        draw();
      } catch(error) {
        if(serial!==state.serial)return;
        portable();
        status.textContent=error.name==='AbortError'?'Loading stopped; the guided figure is still available.':`${error.message} The guided figure is still available.`;
      } finally { if(serial===state.serial)button.disabled=false; }
    }
    root.querySelectorAll('[data-plane]').forEach(button=>button.onclick=()=>{state.axis=+button.dataset.plane;draw();});
    $('[data-marks]').onclick=()=>{state.marks=!state.marks;$('[data-marks]').setAttribute('aria-pressed',String(state.marks));$('[data-marks]').textContent=state.marks?'Hide markers':'Show markers';draw();};
    $('[data-reset]').onclick=()=>{
      state.cursor=[...data.center];$('[data-high]').value=Math.round(data.high);$('[data-zoom]').value=data.reference?'4':'1';$('[data-slab]').value='3';draw();
    };
    $('[data-explore]').onclick=()=>{if(state.volume){portable();$('[data-status]').textContent='Guided figure restored. Full scan exploration is available whenever you want it.';}else loadVolume();};
    $('[data-volume]').onchange=loadVolume;
    for(const selector of ['[data-high]','[data-zoom]','[data-slab]'])$(selector).oninput=draw;
    $('[data-high]').value=Math.round(data.high);$('[data-zoom]').value=data.reference?'4':'1';
    if(local?.cases.includes(data.source_id)) {
      $('[data-explore]').hidden=false;
      $('[data-status]').textContent='Choose Explore full scan for linked slice views, zoom, and contrast controls. The scan stays on this computer.';
    }
    else if(local)$('[data-status]').textContent='Full scan files are missing on this computer. The guided views remain available; restore runs/br016-aneurysm/blind-review to explore every slice.';
    draw();
  }
})();
