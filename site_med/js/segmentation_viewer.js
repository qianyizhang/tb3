(() => {
  'use strict';
  const assets = window.SEGMENTATION_ASSETS || {};
  const comparison = document.getElementById('comparison');
  const caption = document.getElementById('comparison-caption');
  const planeButtons = document.querySelectorAll('[data-plane]');
  const stateButtons = document.querySelectorAll('[data-state]');

  const descriptions = {
    'axial-before': 'Axial CT slice with original ground-truth masks: Pancreas (yellow) and Duodenum (blue) correctly segregated.',
    'axial-after': 'Axial CT slice with 21 mL pancreatic tissue absorbed into the duodenum label. Overall organ shapes remain deceptively plausible.',
    'axial-region': 'Axial CT slice isolating the transferred 21 mL pancreatic head tissue (magenta overlay). Notice the distinct pancreatic parenchymal texture.',
    'coronal-before': 'Coronal (frontal) CT slice showing the natural vertical anatomical relationship between the pancreatic head and duodenal C-loop.',
    'coronal-after': 'Coronal CT slice after tissue transfer: Duodenum mask extends upward and absorbs 21 mL of pancreatic parenchyma.',
    'coronal-region': 'Coronal CT slice isolating the transferred region (magenta). The agent missed this transfer during a 13-organ global sweep but caught it when focused.'
  };

  function update() {
    const activePlaneBtn = document.querySelector('[data-plane][aria-pressed="true"]');
    const activeStateBtn = document.querySelector('[data-state][aria-pressed="true"]');
    if (!activePlaneBtn || !activeStateBtn) return;
    const plane = activePlaneBtn.dataset.plane;
    const state = activeStateBtn.dataset.state;
    const key = `${plane}-${state}`;
    if (assets[key] && comparison) {
      comparison.src = assets[key];
      if (caption && descriptions[key]) {
        caption.textContent = descriptions[key];
      }
    }
  }

  planeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      planeButtons.forEach(b => b.setAttribute('aria-pressed', 'false'));
      btn.setAttribute('aria-pressed', 'true');
      update();
    });
  });

  stateButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      stateButtons.forEach(b => b.setAttribute('aria-pressed', 'false'));
      btn.setAttribute('aria-pressed', 'true');
      update();
    });
  });

  update();
})();
