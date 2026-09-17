/* Display retained regional measurements; no fitting, inference or rescoring. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('cardiac-data').textContent);
  const region = document.getElementById('cardiac-region');
  const direction = document.getElementById('cardiac-direction');
  const svg = document.getElementById('cardiac-curve');
  const status = document.getElementById('cardiac-status');
  const a = data.conditions.masks.material;
  const b = data.conditions['masks-images'].material;
  for (const id of a.regions) {
    const option = document.createElement('option');
    option.value = String(id); option.textContent = `AHA region ${id}`;
    region.append(option);
  }
  function draw() {
    const r = a.regions.indexOf(Number(region.value));
    const d = Number(direction.value);
    const arrays = [a.reference_regional_engineering_pct,
                    a.predicted_regional_engineering_pct,
                    b.predicted_regional_engineering_pct];
    const curves = arrays.map(values => values.map(frame => frame[r][d]));
    // Keep the same vertical scale when comparing regions within one direction.
    const all = arrays.flatMap(values => values.flatMap(frame => frame.map(row => row[d])));
    const low = Math.min(0, Math.floor(Math.min(...all) / 5) * 5);
    const high = Math.max(5, Math.ceil(Math.max(...all) / 5) * 5);
    const x = i => 65 + i / (curves[0].length - 1) * 590;
    const y = value => 270 - (value - low) / (high - low) * 235;
    svg.replaceChildren();
    function element(tag, attrs, text) {
      const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
      for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
      if (text !== undefined) node.textContent = text;
      svg.append(node); return node;
    }
    const names = ['Longitudinal', 'Circumferential', 'Radial'];
    element('title', {}, `${names[d]} engineering strain, AHA region ${a.regions[r]}`);
    element('desc', {}, 'Reference, masks alone and masks plus ultrasound through 30 source phases. Regional averages can conceal local errors.');
    for (let i = 0; i <= 4; i++) {
      const value = low + (high - low) * i / 4;
      element('line', {x1: 65, x2: 655, y1: y(value), y2: y(value), stroke: '#ccd4d1'});
      element('text', {x: 55, y: y(value) + 4, 'text-anchor': 'end', fill: '#54696d', 'font-size': 12}, `${value.toFixed(0)}%`);
    }
    element('text', {x: 65, y: 295, fill: '#54696d', 'font-size': 12}, 'Frame 1');
    element('text', {x: 655, y: 295, 'text-anchor': 'end', fill: '#54696d', 'font-size': 12}, 'Frame 30');
    const colors = ['#9b651b', '#007f76', '#9a4772'];
    curves.forEach((curve, i) => element('polyline', {
      points: curve.map((value, t) => `${x(t)},${y(value)}`).join(' '),
      fill: 'none', stroke: colors[i], 'stroke-width': 2.6,
      'stroke-dasharray': i === 0 ? '7 4' : 'none'
    }));
    const extrema = curves.map(curve => (d === 2 ? Math.max(...curve) : Math.min(...curve)).toFixed(2));
    status.textContent = `Region ${a.regions[r]} · ${names[d].toLowerCase()} peaks: reference ${extrema[0]}%, masks ${extrema[1]}%, masks + ultrasound ${extrema[2]}%. Coverage ${(100 * a.region_coverage[String(a.regions[r])]).toFixed(1)}%.`;
  }
  region.addEventListener('change', draw);
  direction.addEventListener('change', draw);
  draw();
  document.getElementById('cardiac-figure').src = data.figure;
  document.getElementById('cardiac-figure-link').href = data.figure;
})();
