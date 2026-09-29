# FeEcho4D Patient001 contour teaching assets

Source: [FeEcho4D project](https://feecho4d.github.io/Website/) and
[Zenodo record 21322299](https://zenodo.org/records/21322299). The project states
noncommercial research use. This pack is for local task interpretation; its
`LicenseRef-FeEcho4D-noncommercial-research` identifier does not assert public
redistribution permission. The prior release-metadata audit found no explicit
license field. Keep image and derived contour assets local until that scope is
clarified.

The pack uses audited native Patient001 radial images and label-127 cavity masks.
Plane 1 is a supplied contour; plane 8 is one of eight common withheld evaluation
directions. Reference masks appear only in `reference.json` for a reader reveal.
The original author baseline did not use image appearance to reconstruct; it
interpolated radii from supplied masks. Saved `radius_px` arrays are projected onto
native plane 8 with the same assumption used in the retained audit. The player
does no fitting or new trial.

Data axes are native image rows/columns (464 × 485); in-plane spacing is
0.089950 mm/pixel. Five-degree plane steps and axis/origin are pilot assumptions,
not audited native per-plane poses. Dense volume is an annotation-derived source
fit, not independent 3D truth. The one-patient 240 frame/plane pairs are repeated
observations, not independent cases. Fixed vertex IDs do not establish tissue
material motion. The native OBJ cavity partition and physical transform remain
unresolved, so those files are not a volume oracle.

Rebuild from pinned local inputs into a fresh directory:

```sh
.venv-br021/bin/python scripts/build_cardiac_contour_assets.py --out NEW_DIRECTORY
```
