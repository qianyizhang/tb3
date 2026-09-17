# BR-040 — Sol/xhigh CT and MRI landmark comparison

User request, 2026-09-17: “ok, do a sol-xhigh runs on CT and MRI”.

Run one fresh `openai/gpt-5.6-sol` / `xhigh` attempt on each unchanged task:

- BR-039 full CT: 26 requests, 24 visible centres and 2 absent extra levels.
- BR-039 partial CT: 26 requests, 13 visible, 11 outside, 2 absent.
- BR-038 full MRI: all 32 AFIDs, native 3D voxel output, 3 mm acceptance.

Preserve full-volume array access, native coordinates, instructions, image helper, scoring and 3600-second limit. Reuse the same-byte completed oracle/nop controls; verify every frozen file before and after, and require the Sol Harbor task checksum to equal the controls and Terra. No retries. The agent receives no earlier answers or private references. Keep model configuration private; retain raw traces locally. Run at most two conditions concurrently.

This compares **model plus reasoning setting**, Sol/xhigh versus Terra/high. It is not an isolated model-only ablation or a population accuracy estimate. CT hallucination and localization remain separate endpoints. MRI's frozen full-volume task has no unavailable targets, so it cannot measure MRI hallucination. No resumption of the older cropped-MRI world-coordinate task is implied.

Collect exact score replay, independent physical-distance checks, image-payload and retrieval audit, and an offline per-landmark comparison. Do not classify infrastructure failures or timeouts as normal model failures.
