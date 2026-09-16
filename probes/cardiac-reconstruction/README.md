# Cardiac reconstruction research archive

This series is complete. Start with the [report](../../site/index.html#cardiac)
or [session index](../../docs/research-cardiac-session.md). No command here is
an instruction to launch another trial. Raw runs, images, full meshes and
environments remain local; a clean clone contains the authored record and
portable presentation, not the source datasets.

| Authoring directory | Original purpose |
| --- | --- |
| [Root pilot](authoring/README.md) | BR-025 FeEcho4D contour-to-cavity calibration |
| [Video difficulty](authoring/video_difficulty/README.md) | BR-027 one/two-anchor controls |
| [Dynamic heart](authoring/dynamic_heart/README.md) | BR-029 STRAUS source mechanics and author fits |
| [Capability levels](authoring/levels/README.md) | BR-031 known-motion, four-view and full-volume trials |
| [Real echo](authoring/real_echo/README.md) | BR-032 public real-video case and altered-input checks |
| [Clinical adaptation](authoring/pathological_echo/README.md) | BR-034 clinical selection, tracking, hidden-case replays |
| [Segmentation mechanics](authoring/segmentation_mechanics/README.md) | BR-035 paired mask tasks, independent tissue probes and clinical transfer |

These scripts and historical READMEs are retained unchanged. Several hashes are
bound to frozen experiment receipts: presentation cleanup must not silently
refactor them. Commands in those documents reproduce historical stages and may
require retained datasets, Docker, model credentials or explicit new authorization.
The standard `make check` validates repository tooling and presentation only;
it does not run or certify these clinical/scientific tasks.
