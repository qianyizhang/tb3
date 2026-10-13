/** Shared critical native-reader checks for full and smoke browser suites. */
const assert = require('node:assert/strict');

async function checkNativeReader(page, entry, data) {
  const view = data.explainer_views[entry.illustration.story_id];
  const plan = data.explanation_stories[entry.illustration.story_id];
  const reader = page.locator('.scene-player[data-family="native-trace"]');
  await reader.locator('[data-story-step]').first().waitFor();
  assert.equal(await reader.getAttribute('data-native-adapter'), view.adapter);
  assert.equal(await reader.locator('[data-story-step]').count(), plan.beats.length);
  assert.equal(await reader.getAttribute('data-playing'), 'false');
  assert.equal(await reader.locator('details[id^="native-evidence-"]').getAttribute('open'), null);
  for (const [index, beat] of plan.beats.entries()) {
    const chapter = reader.locator(`[data-story-step="${index}"]`);
    assert.ok((await chapter.innerText()).trim(), `${entry.id}: readable native chapter`);
    await chapter.click();
    await page.waitForFunction(
      (id) => document.querySelector('[data-family="native-trace"]')?.dataset.beat === id,
      beat.id,
    );
    assert.equal(await chapter.getAttribute('aria-pressed'), 'true');
    assert.equal(await reader.locator('[data-scene-title]').innerText(), beat.caption);
  }
  assert.equal(await reader.getAttribute('data-reference-shown'), 'false');
  if (!view.payload) {
    assert.ok((await reader.innerText()).includes('Native assets are unavailable in this copy.'));
    assert.equal(await reader.locator('[data-native-ready="true"]').count(), 1);
  }
  await reader.locator('.scene-reset').click();
  await page.waitForFunction(
    (id) => document.querySelector('[data-family="native-trace"]')?.dataset.beat === id,
    plan.beats[0].id,
  );
}

module.exports = { checkNativeReader };
