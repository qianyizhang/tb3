# Locate intracranial aneurysms

Inspect this one TOF-MRA examination and identify every intracranial aneurysm
visible in the supplied volume. There may be zero, one, or multiple aneurysms.
Normal vessel bends and branch points are not aneurysms. No abnormality has been
synthetically injected. You are locating abnormalities, not predicting rupture
risk or drawing precise contours.

Write `/app/answer/answer.json` with exactly this schema:
`{"aneurysms": [[i, j, k], ...]}`. Return an empty list if none is present.
Coordinates are zero-based voxel-centre indices in the original 3-D array, in
**i,j,k order**. Choose a point within each aneurysm sac. Floating-point indices
are accepted; grading rounds to the nearest voxel centre. Coarse expert-labelled
regions plus 1 mm tolerance are used for matching. All lesions must be found and
extra detections count as false positives; duplicate points do not help.

## Inputs and tools

- `/app/data/brain.npz`: skull-stripped TOF-MRA. NumPy keys `volume`, `affine`.
- `/app/data/original.npz`: original unstripped TOF-MRA on the same voxel grid.
- `/app/data/volume.json`: array shape, spacing, RAS affine, display window.
- `/app/data/overview.png`: three full-volume maximum-intensity projections.
- `/app/data/slabs.png`: twelve equal axial-slab projections covering the entire scan.
- `/app/inspect_mra.py`: supplied slice / projection rendering tool, NumPy and Pillow.

Array axes increase towards Right, Anterior, Superior. Display horizontal increases
the first remaining array axis, and vertical increases the second axis upwards;
labels and ticks show these conventions. These are explicit coordinate views,
not the usual radiological left-right display. Array values remain native resolution.
Projections can obscure superimposed vessels: inspect slices / smaller slabs as needed.
The full scan is included; no crop or displayed position indicates a target.

Examples (illustrative arbitrary coordinates, not suggested findings):
```
python /app/inspect_mra.py --axis k --slices 30 40 50 --out /app/slices.png
python /app/inspect_mra.py --axis j --bounds 80 180 100 200 30 90 --out /app/slab.png
python /app/inspect_mra.py --raw --axis i --slices 100 --high 1000 --out /app/raw.png
```
Without `--slices`, the tool makes a maximum-intensity projection through the
selected bounds. Upper bounds are exclusive. `--high` adjusts the display window,
and `--size` adjusts rendering size. You may write your own analysis or rendering
code; the supplied views are starting points. Finish with the answer file.
