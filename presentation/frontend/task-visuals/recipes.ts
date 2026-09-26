import { mapPoint } from './coordinates';
import { C, TAU, mix, smooth, createGeometry } from './geometry';
import type { Face, LegendKey, SceneModel, ScenePoint, VisualEntry, Stage } from './types';
import { AnatomyAssets } from './anatomy';

// Task choreography over shared teaching assets; no task-specific results.
// Kept dependency-free so the complete Explorer works as a single offline file.
const recipes: Record<string, string> = {};
const register = (kinds: string, family: string) =>
  kinds.split(' ').forEach((kind) => {
    recipes[kind] = family;
  });
register('segment instances', 'segmentation');
register('landmark_point box3d', 'localization');
register('anatomy_audit object_identity mask_shortcuts anatomy_curation', 'audit');
register('dynamic_mesh cardiac_contours cardiac_anchors cardiac_material', 'motion');
register('point_correspondence register registration_diagnosis', 'registration');
register('longitudinal', 'longitudinal');
register(
  'route_repair route_discovery route_unfold vesselgraph vessel_source_screen prediction_screen',
  'routes',
);
register('mri mri_dynamic ct ct_phantom dualct pet', 'tomography');
register('restore3d lensless', 'restoration');
register('ultrasound photoacoustic soundmap seismic conductivity', 'waves');
register('odt idt diffraction opticalvolume molecules nlos wavefront deflectometry', 'optics');
register('tensor t2 spectral spectral_cube temperature phase geofield', 'fields');
register('astro_volume', 'astronomy');

function scene(e: VisualEntry, stage: Stage, clock: number, progress = 0): SceneModel {
  const d = e.illustration,
    k = d.kind,
    subject = d.subject || 'generic',
    family = recipes[k];
  if (!family) throw Error('Missing 3D scene: ' + k);
  const out = stage === 2,
    work = stage === 1,
    ink = C.ink,
    teal = C.teal,
    gold = C.gold,
    blue = C.blue,
    rose = C.rose;
  const {
    cavity,
    cavityPoint,
    primitives,
    labels,
    line,
    dot,
    face,
    label,
    group,
    path,
    ring,
    mesh,
    box,
    panel,
    imagePanel,
    volume,
    tube,
    branches,
    asset,
    anatomy,
    organ,
    sweep,
    target,
    documentMesh,
    chart,
    field,
    signals,
    sampled,
  } = createGeometry(e, stage, clock, progress);

  switch (family) {
    case 'segmentation': {
      if (k === 'instances') {
        for (let i = 0; i < 7; i++) {
          const p: ScenePoint = [
            Math.cos(i * 2.4) * (0.4 + i * 0.1),
            Math.sin(i * 2.4) * (0.4 + i * 0.1),
            Math.sin(i) * 0.17,
          ];
          mesh(p, [0.34, 0.28, 0.24], out ? [teal, blue, gold, rose][i % 4] : ink, 0.12);
          if (out) label([p[0], p[1], p[2] + 0.27], String(i + 1), teal);
        }
      } else if (out && d.mask_mode === 'binary') {
        if (['vessels', 'brain-vessels'].includes(subject)) branches(false, false, teal);
        else organ();
        label(
          [0, -1.25, 0],
          d.target ? d.target.replaceAll('_', ' ') + ' · binary mask' : 'One target mask',
          teal,
        );
      } else if (out && d.mask_mode === 'separate') {
        group([-0.8, 0, 0], 0.63, organ);
        mesh([0.95, 0, 0], [0.3, 0.36, 0.27], gold, 0.1);
        label([-0.8, -1.08, 0], 'Organ mask', teal);
        label([0.95, -1.08, 0], 'Lesion mask', gold);
      } else anatomy(out);
      if (work) {
        // A bounded reveal colors the actual displayed regions. The movement
        // teaches region labeling rather than scanning a decorative light beam.
        const cutoff = mix(-1.4, 1.4, smooth(progress));
        const palette = [teal, blue, rose, gold];
        const classes = new Map();
        primitives
          .filter((item): item is Face => item.type === 'face' && Boolean(item.surface))
          .forEach((item) => {
            const y = item.points.reduce((sum, p) => sum + p[1], 0) / item.points.length;
            if (y > cutoff) return;
            if (!classes.has(item.asset)) classes.set(item.asset, classes.size);
            const isTarget =
              !d.target ||
              item.asset === d.target ||
              (d.target === 'kidneys' && item.asset?.startsWith('kidney_'));
            if (d.mask_mode !== 'binary' || isTarget)
              item.color =
                d.mask_mode === 'binary' ? teal : palette[classes.get(item.asset) % palette.length];
          });
        const selected = AnatomyAssets.get(subject)?.find((part) => part.id === d.target);
        if (selected) {
          const bounds = [0, 1, 2].map((axis) => [
            Math.min(...selected.vertices.map((vertex) => vertex[axis])),
            Math.max(...selected.vertices.map((vertex) => vertex[axis])),
          ]);
          const anchor: ScenePoint = [
            (bounds[0][0] + bounds[0][1]) / 2,
            (bounds[1][0] + bounds[1][1]) / 2,
            bounds[2][1] + 0.08,
          ];
          ring(
            anchor,
            Math.max(bounds[0][1] - bounds[0][0], bounds[1][1] - bounds[1][0]) * 0.56,
            teal,
            'z',
            0.8,
            true,
          );
          label([0.9, 0.88, 0.3], 'Inspect target boundary', teal, anchor);
        }
        label([0, -1.35, 0], 'Assign labels along the boundaries', teal);
      }
      break;
    }
    case 'localization':
      if (k === 'box3d') {
        for (let i = 0; i < 3; i++)
          imagePanel([(i - 1) * 0.13, (i - 1) * 0.18, (i - 1) * 0.25], [2.5, 1.65]);
      } else imagePanel();
      if (work) sweep();
      if (out) target(undefined, k === 'box3d');
      if (out)
        label([0.6, 0.63, 0.55], k === 'box3d' ? 'Region' : 'Coordinate', gold, [0.52, 0.15, 0.48]);
      break;
    case 'audit':
      if (k === 'anatomy_audit') {
        const focus = d.target || (subject === 'abdomen' ? 'kidney_left' : null);
        const selected = AnatomyAssets.get(subject)?.find((part) => part.id === focus);
        const witness: ScenePoint = selected
          ? [
              (Math.min(...selected.vertices.map((point) => point[0])) +
                Math.max(...selected.vertices.map((point) => point[0]))) /
                2,
              (Math.min(...selected.vertices.map((point) => point[1])) +
                Math.max(...selected.vertices.map((point) => point[1]))) /
                2,
              Math.max(...selected.vertices.map((point) => point[2])) + 0.04,
            ]
          : [0.52, 0.15, 0.48];
        if (!asset(subject, null, focus)) anatomy(false);
        if (work) {
          ring(witness, 0.28, teal, 'z', 0.85, true);
          dot(witness, 0.05, teal);
          label([0.9, 0.95, 0.3], 'Selected supplied label', teal, witness);
        }
        if (out) {
          target(witness);
          label([0.6, 0.7, 0.5], 'Spatial witness', gold, witness);
        }
      } else if (k === 'anatomy_curation') {
        for (let i = 0; i < 5; i++)
          mesh([0, -0.9 + i * 0.43, 0], [0.46, 0.16, 0.3], i === 2 ? gold : ink, 0.12);
        if (out) group([1.2, 0, 0], 0.6, () => documentMesh([0, 0, 0], teal));
      } else {
        for (let i = 0; i < 3; i++)
          group([-1 + i, 0, 0], 0.7, () => {
            asset(['liver', 'kidney_left', 'spleen'][i], out ? [teal, blue, gold][i] : ink);
            label(
              [0, -0.95, 0],
              out ? ['Identity A', 'Identity B', 'Identity C'][i] : 'Object ' + (i + 1),
              out ? teal : ink,
            );
          });
        if (k === 'mask_shortcuts' && out)
          path(
            [
              [-1, -0.6, 0],
              [1, 0.75, 0],
            ],
            gold,
            0.8,
            1,
            true,
          );
      }
      break;
    case 'motion': {
      const markerParameters: [number, number][] = [
        [0.34, 0.22],
        [0.12, 0.72],
      ];
      const marker = (index: number, phase: number) =>
        cavityPoint(...markerParameters[index], phase);
      const markers = (phase: number) =>
        markerParameters.forEach((_, i) => {
          const p = marker(i, phase),
            color = i ? rose : gold;
          dot(p, 0.06, color);
          label(
            [p[0] + (i ? 0.14 : -0.14), p[1] + (i ? -0.15 : 0.15), p[2] + 0.1],
            i ? 'B' : 'A',
            color,
          );
        });
      if (k === 'cardiac_material' && out) {
        const phases: [number, string, string, number][] = [
          [-0.82, 'Initial', blue, 1],
          [0.82, 'Later', teal, 0.86],
        ];
        for (const [x, phase, color, scale] of phases) {
          group([x, 0.08, 0], 0.7, () => {
            cavity(color, scale);
            markers(scale);
          });
          label([x, -1.18, 0], phase + ' phase', color);
        }
        for (let i = 0; i < 2; i++) {
          const source = mapPoint(marker(i, 1), (v, q) => v * 0.7 + [-0.82, 0.08, 0][q]);
          const target = mapPoint(marker(i, 0.86), (v, q) => v * 0.7 + [0.82, 0.08, 0][q]);
          line(source, target, i ? rose : gold, 0.8, 1.5, true);
        }
        break;
      }
      const settle = out ? 1 - smooth(Math.max(0, (progress - 0.6) / 0.4)) : 1;
      const pulse = 1 - settle * 0.065 * (0.5 - 0.5 * Math.cos((clock * TAU) / 4.8));
      if (!out && d.input_form === 'masks') {
        for (let i = 0; i < 3; i++)
          group([(i - 1) * 0.95, 0, 0], 0.46, () => cavity(blue, 1 - i * 0.05));
      } else if (!out && k === 'cardiac_contours') {
        for (let i = 0; i < 7; i++)
          path(
            Array.from({ length: 49 }, (_, j) => cavityPoint(j / 48, 0.08 + i * 0.12)),
            blue,
          );
      } else {
        cavity(out ? teal : k === 'cardiac_material' ? blue : ink, pulse);
        if (k === 'cardiac_anchors' && out) {
          for (const v of [0.1, 0.45, 0.8])
            path(
              Array.from({ length: 49 }, (_, j) => cavityPoint(j / 48, v, pulse + 0.01)),
              teal,
              0.8,
              1.4,
              true,
            );
        }
        if (k === 'cardiac_anchors') {
          for (const v of [0.1, 0.8])
            path(
              Array.from({ length: 49 }, (_, j) => cavityPoint(j / 48, v, pulse)),
              gold,
            );
        }
      }
      if (k === 'cardiac_material') markers(pulse);
      if (out) label([0, -1.4, 0], 'Time-varying cavity surface', teal);
      break;
    }
    case 'registration': {
      const t = out ? 1 : work ? smooth(progress) : 0;
      if (d.scene_variant === 'slice-to-volume') {
        // The source is one oblique section, not a second full CT. The output
        // is its placement and orientation in the patient's volume frame.
        const center = out || work ? mix(-1.4, 0.72, t) : -1.4;
        for (let i = 0; i < 4; i++)
          imagePanel(
            [0.8 + i * 0.09, (i - 1.5) * 0.24, -0.42 + i * 0.1],
            [1.75, 1.18],
            subject,
            -0.2,
          );
        box([0.95, 0, -0.12], [1.94, 1.94, 0.8], blue);
        imagePanel([center, mix(0, 0.12, t), 0.62], [1.75, 1.18], subject, mix(0, -0.46, t));
        const planeCenter: ScenePoint = [center, mix(0, 0.12, t), 0.63];
        dot(planeCenter, 0.045, gold);
        label(
          [-1.22, -1.22, 0],
          out ? 'Pixel → patient transform' : 'One oblique section',
          gold,
          planeCenter,
        );
        label([1.04, -1.22, -0.1], 'Target CT volume', blue);
        if (out || work) line([-1.4, 0.1, 0.65], planeCenter, teal, 0.85, 1.7, true);
        break;
      }
      // Distinct image planes keep the actual matching question visible. A
      // cross-modality example uses the modality explicitly named in its input.
      const ultrasoundTarget = /ultrasound/i.test(d.input || '');
      [-0.95, 0.95].forEach((x, i) =>
        group([x, 0, 0], 0.6, () => {
          group(i ? [mix(0.3, 0, t), mix(0.2, 0, t), 0] : [0, 0, 0], 1, () => {
            imagePanel([0, 0, 0], [2.75, 1.88], i && ultrasoundTarget ? 'ultrasound' : subject);
          });
        }),
      );
      if (k !== 'register') {
        const source: ScenePoint = [-1.25, 0.33, 0.4],
          returned: ScenePoint = [0.95 + mix(0.18, -0.3, t), mix(0.48, 0.33, t), 0.4];
        dot(source, 0.055, gold);
        if (out || d.initial_candidate) dot(returned, 0.055, teal);
        if (out || work) line(source, returned, gold, 0.8, 1.4, true);
      }
      label([-0.95, -1.08, 0], k === 'register' ? 'Fixed image' : 'Source · fixed query', blue);
      label(
        [0.95, -1.08, 0],
        k === 'register'
          ? 'Moving image'
          : ultrasoundTarget
            ? 'Ultrasound · target'
            : 'Target · search here',
        rose,
      );
      if (out && k === 'point_correspondence')
        label([0.9, 0.85, 0.4], 'Returned point', teal, [0.65, 0.33, 0.4]);
      break;
    }
    case 'longitudinal':
      [-1, 1].forEach((side, i) =>
        group([side * 0.95, 0, 0], 0.57, () => {
          anatomy(false);
          if (out || work) {
            if (subject === 'breast' || subject === 'generic') {
              ring([0.43, 0.1, 0.55], 0.2, gold, 'z', 1);
              dot([0.43, 0.1, 0.55], 0.04, gold);
            } else mesh([0.43, 0.1, 0.55], [0.2, 0.23, 0.21], gold, 0.06);
          }
          label([0, -1.6, 0], i ? 'Later examination' : 'Earlier examination', ink);
        }),
      );
      if (out || work)
        label([0.1, -1.35, 0.5], 'Link / new / unobserved: output schema only', teal);
      break;
    case 'routes':
      if (k === 'route_unfold' && out) group([-0.76, 0.1, 0], 0.62, () => branches(false, true));
      else
        branches(
          out && k === 'route_discovery',
          k === 'route_repair' || k === 'route_unfold',
          k === 'prediction_screen' ? blue : k === 'route_repair' ? teal : null,
          k === 'prediction_screen',
        );
      if (k === 'route_unfold')
        group(out ? [-0.76, 0.1, 0] : [0, 0, 0], out ? 0.62 : 1, () => {
          dot([0, -0.15, 0.15], 0.075, teal);
          dot([1.05, 1.05, 0.2], 0.075, teal);
        });
      if (k === 'route_repair' || k === 'route_unfold') {
        if (work) {
          const traced = smooth(progress);
          const cursor: ScenePoint = [mix(0, 0.48, traced), mix(-0.15, 0.17, traced), 0.2];
          line([0, -0.15, 0.2], cursor, gold, 0.9, 2, true);
          dot(cursor, 0.065, gold);
          label([0.85, -0.85, 0.2], 'Trace candidate route', gold, cursor);
        }
        if (out && k === 'route_unfold')
          group([-0.76, 0.1, 0], 0.62, () =>
            tube(
              [
                [0, -0.15, 0],
                [0.48, 0.17, -0.12],
                [0.83, 0.55, -0.1],
                [1.05, 1.05, 0.07],
              ],
              gold,
              0.065,
            ),
          );
        else ring([0.22, 0.03, 0], 0.31, gold, 'z', 0.8, true);
      }
      if (out && k === 'vesselgraph') {
        const junctions: ScenePoint[] = [
          [0, -0.3, 0.04],
          [-0.45, 0.03, 0.08],
          [0.48, 0.17, -0.12],
          [0.83, 0.55, -0.1],
        ];
        junctions.forEach((p) => dot(p, 0.075, gold));
        label([0.85, -0.65, 0.2], 'Connection labels', gold);
      }
      if (k === 'prediction_screen') {
        group([0.06, 0.04, 0.12], 1, () => branches(false, false, teal));
        label([0, -1.45, 0], 'Prediction / reference comparison', teal);
      }
      if (k === 'vessel_source_screen') {
        ring([0.5, 0.3, 0.05], 0.3, gold, 'z', 0.8, true);
        label([0.85, -0.6, 0], 'Connection uncertain', gold);
      }
      if (out && k === 'route_unfold') {
        group([0.83, 0, 0], 0.63, () => {
          panel([0, 0, -0.14], [1.45, 2.4]);
          path(
            [
              [-0.3, -0.95, 0.04],
              [-0.38, -0.48, 0.04],
              [-0.26, 0.1, 0.04],
              [-0.36, 0.95, 0.04],
            ],
            teal,
            0.85,
            2,
          );
          path(
            [
              [0.3, -0.95, 0.04],
              [0.22, -0.48, 0.04],
              [0.34, 0.1, 0.04],
              [0.24, 0.95, 0.04],
            ],
            teal,
            0.85,
            2,
          );
          line([0, -0.95, 0.06], [-0.08, 0.95, 0.06], gold, 1, 2);
          for (const y of [-0.7, -0.2, 0.3, 0.8])
            line([-0.31, y, 0.05], [0.29, y, 0.05], blue, 0.5);
        });
        label([-0.8, -1.34, 0], 'Selected vessel route', gold);
        label([0.83, -1.34, 0], 'Curved planar view', teal);
      }
      if (work && k === 'route_discovery')
        dot([0, mix(-1.1, 1.1, smooth(progress)), 0.12], 0.07, gold);
      break;
    case 'tomography':
      if (k === 'mri' || k === 'mri_dynamic') {
        if (out) anatomy(false);
        else {
          sampled();
          if (work) sweep();
        }
        if (k === 'mri_dynamic') label([0, -1.4, 0], 'Sequence over time', teal);
      } else {
        if (out) {
          if (k === 'ct_phantom') {
            panel();
            mesh([0, 0, 0], [0.87, 1.12, 0.06], ink);
            mesh([-0.28, 0.02, 0.12], [0.24, 0.65, 0.04], blue);
            mesh([0.28, 0.12, 0.12], [0.2, 0.53, 0.04], teal);
            mesh([0, 0.68, 0.12], [0.28, 0.15, 0.04], C.faint);
          } else if (k === 'pet') {
            mesh([0, 0, 0], [0.8, 1, 0.6], ink, 0.06);
            mesh([0.27, 0.23, 0.45], [0.24, 0.28, 0.2], gold, 0.08);
          } else anatomy(false);
        } else {
          mesh([0, 0, 0], [0.4, 0.65, 0.4], ink, 0.08);
          for (let i = 0; i < 9; i++) {
            const a = (i * TAU) / 9 + (work ? smooth(progress) * 0.6 : 0),
              p: ScenePoint = [1.35 * Math.cos(a), 0.18, 1.35 * Math.sin(a)];
            dot(p, 0.04, k === 'dualct' && i % 2 ? rose : teal);
            line(p, [-p[0], -0.25, -p[2]], i % 2 ? blue : teal, 0.3);
          }
          ring([0, 0.18, 0], 1.35, ink);
        }
        if (k === 'dualct' && out) {
          group([-0.72, 0, 0], 0.5, () => mesh([0, 0, 0], [0.7, 1, 0.65], blue));
          group([0.72, 0, 0], 0.5, () => mesh([0, 0, 0], [0.7, 1, 0.65], gold));
          label([-0.8, -1.3, 0], 'Material A', blue);
          label([0.8, -1.3, 0], 'Material B', gold);
        }
      }
      break;
    case 'restoration':
      anatomy(false);
      if (!out)
        for (let i = 0; i < 110; i++)
          dot(
            [Math.sin(i * 13.7) * 1.15, Math.sin(i * 4.3) * 1.05, Math.cos(i * 7.7) * 0.85],
            0.011,
            C.faint,
          );
      if (work) sweep();
      break;
    case 'waves':
      if (!out) {
        signals();
        if (work) ring([0, 0, 0], 0.65 + 0.3 * smooth(progress), gold, 'z');
      } else if (k === 'seismic') {
        for (let j = 0; j < 6; j++) group([0, (j - 3) * 0.35, 0], 1, () => field(false));
      } else if (['soundmap', 'conductivity'].includes(k)) {
        field(true);
        label([0, -1.25, 0], k === 'soundmap' ? 'Sound speed' : 'Conductivity', teal);
      } else anatomy(false);
      break;
    case 'optics':
      if (k === 'nlos') {
        face(
          [
            [0.2, -1, -0.6],
            [0.2, 1, -0.6],
            [0.2, 1, 0.8],
            [0.2, -1, 0.8],
          ],
          C.faint,
          0.15,
        );
        box([-0.6, -0.35, -0.25], [0.6, 0.9, 0.55], ink);
        path(
          [
            [1, 1, 1],
            [0.2, 0.35, 0.65],
            [-0.7, -0.2, -0.2],
          ],
          teal,
          0.8,
          2,
          true,
        );
        if (out) mesh([-0.6, -0.35, -0.25], [0.35, 0.5, 0.3], teal, 0.05);
      } else if (k === 'deflectometry') {
        if (out) {
          mesh([0, 0, 0], [0.34, 1, 0.78], teal, 0.015);
          label([0.9, 0, 0], 'Thickness / curvature', teal);
        } else
          for (let view = 0; view < 2; view++)
            group([view ? 0.75 : -0.75, 0, 0], 0.56, () => {
              panel();
              for (let i = 0; i < 12; i++)
                path(
                  Array.from({ length: 30 }, (_, j) => [
                    (i - 5.5) * 0.18 + 0.15 * Math.sin(j * 0.14 + view * 0.3),
                    -1 + j / 15,
                    0,
                  ]),
                  blue,
                  0.8,
                );
              label([0, -1.3, 0], 'Camera ' + (view + 1), blue);
            });
      } else if (k === 'wavefront') {
        if (out) field(false);
        else {
          panel();
          for (let i = 0; i < 42; i++)
            dot(
              [((i % 7) - 3) * 0.34 + Math.sin(i) * 0.04, (Math.floor(i / 7) - 2.5) * 0.34, 0],
              0.025,
              blue,
            );
        }
      } else if (k === 'molecules') {
        if (out) {
          box([0, 0, 0], [2.2, 2, 1.6], C.faint);
          for (let i = 0; i < 12; i++)
            dot([Math.sin(i * 2.3), Math.cos(i * 3.6) * 0.8, Math.sin(i * 4.7) * 0.7], 0.045, gold);
        } else sampled();
      } else if (out) {
        if (k === 'diffraction') {
          group([-0.72, 0, 0], 0.53, () => field(false));
          group([0.72, 0, 0], 0.53, () => field(false, rose));
          label([-0.85, -0.9, 0], 'Amplitude', teal);
          label([0.85, -0.9, 0], 'Phase', rose);
        } else {
          volume(teal, 7);
          mesh([0, 0, 0], [0.6, 0.7, 0.5], teal, 0.12);
        }
      } else {
        for (let i = 0; i < 6; i++)
          group(
            [Math.cos((i * TAU) / 6) * 0.9, Math.sin((i * TAU) / 6) * 0.7, Math.sin(i) * 0.35],
            0.45,
            () => {
              ring([0, 0, 0], 0.6, blue, 'z');
              ring([0, 0, 0], 0.3, gold, 'z');
            },
          );
        if (work) ring([0, 0, 0], 1.2, teal);
      }
      break;
    case 'fields':
      if (!out) {
        if (k === 't2') chart('decay', blue);
        else if (k === 'geofield') {
          field(false);
          for (let i = 0; i < 12; i++)
            dot([Math.sin(i) * 1.2, 0.5, Math.cos(i * 2.1)], 0.035, gold);
        } else signals();
      } else if (k === 'temperature') {
        tube(
          [
            [0, -0.7, 0],
            [0, 0.9, 0],
          ],
          ink,
          0.08,
        );
        dot([0, -0.8, 0], 0.16, gold);
        line([0, -0.7, 0.1], [0, 0.45, 0.1], gold, 1, 3);
        label([0.4, 0.2, 0], 'Temperature', gold);
      } else if (k === 'tensor') {
        const radii: ScenePoint[] = [
          [0.68, 0.21, 0.25],
          [0.21, 0.68, 0.25],
          [0.21, 0.25, 0.68],
        ];
        for (let i = 0; i < 25; i++)
          group([((i % 5) - 2) * 0.45, (Math.floor(i / 5) - 2) * 0.45, 0], 0.25, () =>
            mesh([0, 0, 0], radii[i % 3], [blue, teal, gold][i % 3]),
          );
      } else if (k === 'spectral_cube') {
        volume(teal, 9);
        label([0, -1.4, 0], 'λ · wavelength, not depth', teal);
      } else if (k === 'phase') chart('phase');
      else field(['spectral', 't2'].includes(k));
      break;
    case 'astronomy':
      if (!out) {
        sampled();
        if (work) signals();
      } else if (d.scene_variant === 'moon') {
        mesh([0, 0, 0], [0.9, 0.9, 0.9], ink, 0.025);
        for (let i = 0; i < 6; i++) {
          const r = 0.06 + (i % 3) * 0.04;
          path(
            Array.from({ length: 33 }, (_, j) => {
              const a = (j * TAU) / 32,
                x = Math.sin(i * 2.3) * 0.53 + r * Math.cos(a),
                y = Math.cos(i * 3.1) * 0.5 + r * Math.sin(a);
              return [x, y, Math.sqrt(0.9 ** 2 - x * x - y * y)];
            }),
            C.faint,
          );
        }
      } else if (d.scene_variant === 'galaxy') {
        mesh([0, 0, 0], [1.2, 0.24, 0.75], teal, 0.1);
        mesh([0, 0, 0], [0.3, 0.32, 0.3], gold, 0.05);
      } else {
        volume(teal, 7);
        mesh([0, 0, 0], [0.7, 0.45, 0.7], gold, 0.08);
      }
      break;
  }
  // Paused action stages need an inspectable cue, including families whose
  // output is a static comparison. These marks indicate the operation only;
  // they do not depict a reference, prediction or adjudicated result.
  if (work) {
    switch (k) {
      case 'object_identity':
      case 'mask_shortcuts':
        ring([0, 0, 0.65], 0.42, gold, 'z', 0.85, true);
        label(
          [0.75, 0.75, 0.65],
          k === 'mask_shortcuts' ? 'Check spatial cue' : 'Inspect one object',
          gold,
          [0, 0, 0.65],
        );
        break;
      case 'anatomy_curation':
        ring([0, 0, 0.5], 0.48, gold, 'z', 0.85, true);
        label([0.8, 0.65, 0.5], 'Review candidate', gold, [0, 0, 0.5]);
        break;
      case 'cardiac_contours':
        ring([0, 0, 0.35], 0.7, teal, 'z', 0.9, true);
        label([0.8, 0.8, 0.35], 'Fit between contours', teal, [0, 0, 0.35]);
        break;
      case 'dynamic_mesh':
        if (d.input_form === 'masks') {
          line([-0.9, 0, 0.5], [0, 0, 0.5], teal, 0.9, 2, true);
          label([0.8, 0.8, 0.5], 'Connect phase shapes', teal, [0, 0, 0.5]);
        }
        break;
      case 'vesselgraph':
        dot([0, -0.3, 0.28], 0.06, gold);
        dot([0.48, 0.17, 0.28], 0.06, gold);
        line([0, -0.3, 0.28], [0.48, 0.17, 0.28], gold, 0.9, 2, true);
        label([0.9, -0.7, 0.3], 'Check connectivity', gold, [0.48, 0.17, 0.28]);
        break;
      case 'vessel_source_screen':
        line([0.2, 0.03, 0.3], [0.7, 0.4, 0.3], gold, 0.9, 2, true);
        label([0.9, -0.65, 0.3], 'Inspect source route', gold, [0.5, 0.25, 0.3]);
        break;
      case 'prediction_screen':
        ring([0.28, 0.08, 0.45], 0.28, gold, 'z', 0.8, true);
        label([0.9, -0.7, 0.45], 'Compare structures', gold, [0.28, 0.08, 0.45]);
        break;
      case 'nlos':
        ring([0.2, 0.35, 0.7], 0.22, gold, 'z', 0.85, true);
        label([0.8, -0.8, 0.7], 'Trace wall return', gold, [0.2, 0.35, 0.7]);
        break;
      case 'deflectometry':
        line([-0.55, 0.1, 0.45], [0.55, 0.1, 0.45], gold, 0.9, 2, true);
        label([0.8, -0.9, 0.45], 'Compare views', gold, [0, 0.1, 0.45]);
        break;
      case 'wavefront':
        ring([0, 0, 0.22], 0.48, gold, 'z', 0.85, true);
        label([0.85, -0.8, 0.22], 'Fit wavefront', gold, [0, 0, 0.22]);
        break;
      case 'molecules':
        box([0, 0, 0.3], [0.9, 0.9, 0.6], gold, true);
        label([0.85, -0.85, 0.3], 'Localize emitters', gold, [0, 0, 0.3]);
        break;
      case 't2':
        dot([0.35, 0.2, 0.3], 0.06, gold);
        label([0.8, 0.7, 0.3], 'Fit decay', gold, [0.35, 0.2, 0.3]);
        break;
    }
  }
  return { primitives, labels };
}

function legend(e: VisualEntry): LegendKey[] {
  const d = e.illustration,
    k = d.kind;
  let keys: LegendKey[] = [
    [C.stone, 'Structure / input'],
    [C.teal, 'Derived structure'],
    [C.gold, 'Focus / correspondence'],
  ];
  if (k === 'anatomy_audit')
    keys = [
      [C.stone, 'Anatomical context'],
      [C.teal, 'Illustrative supplied mask'],
      [C.gold, 'Spatial witness'],
    ];
  if (['segment', 'instances', 'object_identity'].includes(k))
    keys =
      d.mask_mode === 'separate'
        ? [
            [C.stone, 'Input'],
            [C.teal, 'Organ'],
            [C.gold, 'Lesion'],
          ]
        : [
            [C.stone, 'Input'],
            [C.teal, 'Spatial class A'],
            [C.blue, 'Class B'],
            [C.rose, 'Class C'],
            [C.gold, 'Class D / focus'],
          ];
  if (['point_correspondence', 'register', 'registration_diagnosis'].includes(k))
    keys = [
      [C.blue, 'Source'],
      [C.rose, 'Target'],
      [C.gold, 'Query'],
      [C.teal, 'Returned point'],
    ];
  if (k === 'register' && d.scene_variant === 'slice-to-volume')
    keys = [
      [C.gold, 'Oblique section'],
      [C.blue, 'Target CT volume'],
      [C.teal, 'Placement path · dashed', true],
    ];
  if (k === 'cardiac_material')
    keys = [
      [C.blue, 'Initial phase geometry'],
      [C.teal, 'Later phase geometry'],
      [C.gold, 'Material point A · dashed track', true],
      [C.rose, 'Material point B · dashed track', true],
    ];
  if (k === 'cardiac_anchors')
    keys = [
      [C.gold, 'Supplied anchors · solid'],
      [C.teal, 'Recovered motion · dashed', true],
    ];
  if (k === 'cardiac_contours')
    keys = [
      [C.blue, 'Supplied contours'],
      [C.teal, 'Recovered surface'],
    ];
  if (k === 'prediction_screen')
    keys = [
      [C.blue, 'Reference · dashed', true],
      [C.teal, 'Prediction · solid'],
    ];
  if (k === 'diffraction')
    keys = [
      [C.ink, 'Input measurements'],
      [C.teal, 'Amplitude'],
      [C.rose, 'Phase'],
    ];
  if (['spectral', 't2', 'soundmap', 'conductivity'].includes(k))
    keys = [
      [C.ink, 'Input'],
      [C.blue, 'Lower field value'],
      [C.teal, 'Mid field value'],
      [C.gold, 'Higher field value'],
    ];
  if (k === 'tensor')
    keys = [
      [C.ink, 'Input'],
      [C.blue, 'Axis A'],
      [C.teal, 'Axis B'],
      [C.gold, 'Axis C'],
    ];
  if (d.mask_mode === 'binary')
    keys = [
      [C.stone, 'Input'],
      [C.teal, 'Single target mask'],
    ];
  return keys;
}

export const TaskSceneModels = {
  build: scene,
  animated: (e: VisualEntry, stage: Stage) => {
    const d = e.illustration,
      family = recipes[d.kind];
    if (family === 'motion')
      return d.kind === 'cardiac_material'
        ? stage < 2
        : stage === 2 || (d.input_form !== 'masks' && d.kind !== 'cardiac_contours');
    return (
      stage === 1 &&
      [
        'segmentation',
        'localization',
        'registration',
        'routes',
        'tomography',
        'restoration',
        'waves',
        'optics',
        'fields',
        'astronomy',
      ].includes(family)
    );
  },
  usesAnatomy: (e: VisualEntry) =>
    recipes[e.illustration.kind] !== 'motion' &&
    (AnatomyAssets.has(e.illustration.subject) ||
      AnatomyAssets.has(e.illustration.target) ||
      ['object_identity', 'mask_shortcuts'].includes(e.illustration.kind)),
  legend,
  supports: (kind: string) => Object.hasOwn(recipes, kind),
};
