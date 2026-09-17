(() => {
  const data = JSON.parse(document.getElementById('registration-data').textContent);
  const $ = id => document.getElementById(id);
  const old = data.methods['Sol / original 2D source'];
  const next = data.methods['Sol / full 3D source'];
  let selected = 5;
  Object.keys(data.source).forEach(name => $('reg-plane').add(new Option(name, name)));
  data.ids.forEach((id, index) => {
    const button = document.createElement('button');
    button.textContent = id;
    button.onclick = () => { selected = index; render(); };
    $('reg-queries').append(button);
  });
  function render() {
    const plane = $('reg-plane').value;
    $('reg-source').src = data.source[plane][selected];
    $('reg-manual').src = data.manual[plane][selected];
    $('reg-old').src = old.images[plane][selected];
    $('reg-new').src = next.images[plane][selected];
    const previousError = old.grade.per_point_mm[selected];
    const newError = next.grade.per_point_mm[selected];
    $('reg-old-error').textContent = `${previousError.toFixed(2)} mm from reference`;
    $('reg-new-error').textContent = `${newError.toFixed(2)} mm from reference`;
    $('reg-status').textContent = selected === 5
      ? 'q06 · User accepts this worst case visually. Its 6.41 mm distance still exceeds the frozen 5 mm maximum.'
      : `${data.ids[selected]} · Full-source estimate is within the frozen point tolerance. Overall full-source RMS: 2.60 mm; maximum: 6.41 mm.`;
    $('reg-context').textContent = plane === 'Original oblique plane'
      ? 'This source plane was available in both attempts.'
      : 'This source depth was available only in the full-source attempt. The target volume was available in both.';
    [...$('reg-queries').children].forEach((button, index) => button.setAttribute('aria-pressed', String(index === selected)));
  }
  $('reg-plane').onchange = render;
  render();
})();
