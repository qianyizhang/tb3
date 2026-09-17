'use strict';
const landmarkCases = JSON.parse(document.getElementById('landmark-data').textContent);
const landmarkExplorer = document.getElementById('landmark-explorer');
for (const item of landmarkCases) {
  const wrapper = document.createElement('div');
  wrapper.innerHTML = item.html;
  wrapper.querySelector('select').addEventListener('change', event => {
    wrapper.querySelector('img').src = item.images[event.target.value];
  });
  landmarkExplorer.append(wrapper);
}
