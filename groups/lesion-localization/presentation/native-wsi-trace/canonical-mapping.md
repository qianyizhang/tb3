# Canonical mapping: native CAMELYON whole-slide trace

**Mapping complete; production acceptance remains separate.** Entry `wsi-camelyon-search` can use the retained Sol 6 xhigh `tumor_084` attempt as a source-backed whole-slide search trace: 27 trajectory steps, nine exact delivered JPEGs, ten native helper reads, and a valid empty output with 0/30 study-defined groups hit. This mapping records source availability and display transforms; it does not bind a canonical story or certify pathology.

The adapter, payload contracts and renderer are retained as unfinished development
scaffolding. No canonical story or reader routing enables this adapter yet; source
packaging, integration and visual review remain pending.

## Contract and source boundaries

- **Attempt:** `attempt-9acd94eaa875417b`, experiment `wsi-camelyon-lesion-v2-sol6-xhigh`, small-positive condition, `openai/gpt-6-sol`, xhigh. The attempt launch record says running; later execution, observation and retained synthesis record completion. Retain both historical states.
- **Frozen input:** task digest `522d06f5b8e21cf30459cb7c903b56e605407982401eb701878738d61f243c5c`; snapshot `.local/freezes/<digest>/task`. All 13 files independently match the freeze manifest. The source TIFF also matches the frozen TIFF and acquisition receipt (838,426,602 bytes).
- **Prompt:** search lymph-node H&E at several scales and save `/app/answer/points.json` with `{"points":[{"x":123,"y":456,"confidence":0.8}]}` or an empty list. Coordinates are native level 0; confidence is 0–1. Source XML is withheld; a hit must lie inside a non-excluded Tumor polygon. Preparation, helper, private reference and evaluation remain separate.
- **Geometry:** native width 65,536 × height 86,016. Native pixel representation 0 in TIFF XML specifies 0.000227273 mm = **0.227273 µm/px**, matching the prompt and private reference. The enclosing scanner image XML has different spacings (0.000226316 and 0.000226321 mm); use representation 0 for this frozen pixel grid. No XResolution/YResolution TIFF tags were present.
- **Pyramid:** nine tiled IFDs, each with 512×512 tiles. Actual IFD `(width,height)` values are `(65536,86016)`, `(32768,43008)`, `(16384,21504)`, `(8192,10752)`, `(4096,5632)`, `(2048,3072)`, `(1024,1536)`, `(512,1024)`, `(512,512)`. Corresponding native valid extents divide level 0 by `2**level`: page4 valid height 5376, page6 valid height 1344. The step16 printed shapes reflect cropped pyramid-series views; the step17 direct page4 decode and retained `level4.jpg` are **4096×5632**. Do not fit the padded height onto the native slide.
- **Overview:** frozen JPEG 1024×1344, byte-identical to step8 delivery. Its scale is 64 native pixels per displayed pixel; no reference overlay. A direct page6 read includes 192 padded rows absent from the frozen overview.
- **Reference:** released `tumor_084.xml` coordinates exactly match the 54 private Tumor polygon arrays in order; there are zero Exclusion polygons. Frozen reference partitions them into 30 study groups. Native contours can be revealed after output, labeled source reference, with a clear red-solid legend. Do not treat groups as independently adjudicated biological lesions.
- **Evaluator:** source polygon interiors use the retained ray-crossing test; no edge-distance tolerance. Points are sorted by descending confidence. Excluded, outside-reference and duplicate points count as false positives; duplicate counts are also separate. Each new candidate group increments group coverage. Grouping was prescribed at 50 µm using a 16x raster and about 25 µm dilation per side; this is a study rule, not the official challenge FROC. The retained artifact reward 1 means JSON contract validity; retained diagnostic recall is **0/30**, submitted points 0.
- **Terms:** retained publisher S3 `camelyon-license.txt` declares CC0 and has the pinned release hash below. The retained S3 `camelyon-readme.md` states full tumor annotation except its explicit list; `tumor_084` is absent from that list. Its native source XML has 54 Tumor and zero Exclusion polygons. Other CAMELYON pages use different wording; retain release-specific attribution and do not assert a universal license. This local explanatory mapping requires no further dataset acquisition.

## Exact deliveries and saved files

The trajectory observations contain Python literal lists of `input_image` data URLs. Decode those bytes directly. Every embedded delivery is byte-identical to its retained JPEG; all calls use `detail:"original"`. This proves the tool-return payload, not any undocumented model-side resizing, attention or visual interpretation. Individual native PNGs and `level4.jpg` were saved but never delivered individually in this trace. The contact sheets and selected detail panels are the actual native-derived deliveries.

Local audit: `.local/anatomy-pose/wsi/mapping/inventory.json`; extracted original bytes: `delivery-STEP-ORDINAL.jpg` in that directory. The job root is `.local/attempts/attempt-9acd94eaa875417b/job/task__AbJ8DUi`, with saved images under `artifacts/app/work/`.

| Step | Exact delivered file | Dimensions | Bytes | SHA-256 |
| --- | --- | --- | --- | --- |
| 8 | `overview.jpg` | 1024×1344 | 315322 | `5064c9a9f12b0189b84153894ec3a4f7edc95f2e148b5be5b335c84aa5b39b77` |
| 12 | `contact.jpg` | 2400×1620 | 2317564 | `44b25b2360102604ca2993515f7a13b1094b2f13304d710021a838487d9c476a` |
| 15 | `detail.jpg` | 3072×2048 | 2563263 | `76c9a623d3c4bab4c125c4a9c8f2bde43b49d09e6cdd94201c892aae5486aac1` |
| 19 | `upper_16.jpg` | 2000×2000 | 2214865 | `af0238b96ccbbb2bc55fc1eb8d5d489dfcaecb590d181bbb10ba2ecedba5904a` |
| 19 | `lower_top_16.jpg` | 2000×2000 | 2917861 | `1a88596d9800d1b37e9c60f905059b52bf472d1cbcec0de99b993a1ac19d4a3f` |
| 19 | `lower_bottom_16.jpg` | 2000×2000 | 1823251 | `656c517fbbea835b51310b40e5dc97ca2091b608d4c3241e0b4f90d151ca2aa9` |
| 19 | `lower_right_16.jpg` | 2000×2000 | 1660428 | `f961f85e63fc10f56d5032ee00fca79e6b69b4d66c369c8ea934b79ba27952d8` |
| 22 | `contact2.jpg` | 2048×2080 | 2913600 | `c5787036c613d0876476f9037b9d86b15d822c249b685ee2ae120bd813b0095e` |
| 24 | `detail2.jpg` | 2048×2048 | 1785562 | `4fec006ecc8b30bd7e79168db31da48525cacbc9900797b19cc48c39911ceb0c` |

## Native coordinate transforms for every delivered panel

Rectangles are half-open `(x,y,width,height)`; display origin is `(u,v)`. For a panel, native `x=x0+s*(u-u0)`, `y=y0+s*(v-v0)` in continuous pixel-edge coordinates. Pillow resampling introduces normal pixel-center/filter effects; this map records the exact crop and resize footprint, not a claim of byte losslessness. Composite whitespace, title bands and painted labels are outside the scientific image mapping.

| Step / panel | Display origin | Display content size | Native rectangle | Native px/display px |
| --- | --- | --- | --- | --- |
| 8 overview | (0,0) | 1024×1344 | (0,0,65536,86016) | 64 |
| 12 lo_center | (0,20) | 790×790 | (18432,55552,4096,4096) | 4096/790 |
| 12 lo_top | (800,20) | 790×790 | (22272,39232,4096,4096) | 4096/790 |
| 12 lo_right | (1600,20) | 790×790 | (40832,47872,4096,4096) | 4096/790 |
| 12 up_top | (0,830) | 790×790 | (41472,8832,4096,4096) | 4096/790 |
| 12 up_right | (800,830) | 790×790 | (49152,20352,4096,4096) | 4096/790 |
| 12 lo_left | (1600,830) | 790×790 | (12672,52352,4096,4096) | 4096/790 |
| 15 lo_center + (0,0) | (0,0) | 1024×1024 | (18432,55552,1024,1024) | 1 |
| 15 lo_center + (2048,0) | (1024,0) | 1024×1024 | (20480,55552,1024,1024) | 1 |
| 15 lo_center + (0,2048) | (2048,0) | 1024×1024 | (18432,57600,1024,1024) | 1 |
| 15 lo_center + (2048,2048) | (0,1024) | 1024×1024 | (20480,57600,1024,1024) | 1 |
| 15 lo_top + (0,0) | (1024,1024) | 1024×1024 | (22272,39232,1024,1024) | 1 |
| 15 up_top + (0,0) | (2048,1024) | 1024×1024 | (41472,8832,1024,1024) | 1 |
| 19 upper_16 | (0,0) | 2000×2000 | (27200,4800,32000,32000) | 16 |
| 19 lower_top_16 | (0,0) | 2000×2000 | (9600,36000,32000,32000) | 16 |
| 19 lower_bottom_16 | (0,0) | 2000×2000 | (9600,54400,32000,32000) | 16 |
| 19 lower_right_16 | (0,0) | 2000×2000 | (28800,39200,32000,32000) | 16 |
| 22 up_pale_right | (0,16) | 1024×1024 | (45000,10000,4096,4096) | 4 |
| 22 up_pale_left | (1024,16) | 1024×1024 | (34500,9000,4096,4096) | 4 |
| 22 lo_bottom_pale | (0,1056) | 1024×1024 | (19000,60500,4096,4096) | 4 |
| 22 lo_upper_left | (1024,1056) | 1024×1024 | (17500,41500,4096,4096) | 4 |
| 24 up_pale_right + (1550,2650) | (0,0) | 1024×1024 | (46550,12650,1024,1024) | 1 |
| 24 up_pale_right + (1750,1150) | (1024,0) | 1024×1024 | (46750,11150,1024,1024) | 1 |
| 24 lo_bottom_pale + (500,1250) | (0,1024) | 1024×1024 | (19500,61750,1024,1024) | 1 |
| 24 lo_upper_left + (300,1500) | (1024,1024) | 1024×1024 | (17800,43000,1024,1024) | 1 |

- **Step12:** generated at step11, JPEG quality90; native 4096-square PNGs use `thumbnail((790,790))`, pasted into 800×810 cells with 20-row title bands.
- **Step15:** generated at step14, quality94; six unresized 1024-square crops, rather than exhaustive views of the six helper tiles. Painted white label rectangles cover local `(0,0)` through `(220,25)` inclusive (221×26 pixels).
- **Step19:** step17 saves direct page4 as JPEG quality92; step18 then crops this JPEG and re-encodes four quality95 images. `lower_bottom_16` ends at native y86400: its last **24 rows** map beyond native y86016 and must be marked padding, excluded from native coverage. It must not be stretched to fit the slide. The other three rectangles lie within native extent.
- **Step22:** step21 resizes each 4096-square helper PNG to 1024-square with Pillow's default resize filter, quality94; 16-row bands per 1040-row cell.
- **Step24:** step23 unresized crops, quality94; white labels cover local `(0,0)` through `(330,24)` inclusive (331×25 pixels).

## Access, interpretation and output

- **Native helper coverage:** ten successful reads, each 4096×4096, are in `read-ledger.jsonl`; origins appear in the panel table. They contain 11/30 retained oracle group-center points, reproduced by point-in-half-open-helper-rectangle only. This is an access lower bound for those centers, not tumor area coverage, attention or an exact delivered-detail measure.
- **Direct reads:** full page4 was read outside the helper ledger and four regions were delivered. The helper has no enforced global read budget; a sparse ledger cannot establish that other areas were inaccessible. Saved `level4.jpg` is broader than delivered step19 crops. Overview includes the whole native slide at 64x downsampling.
- **Recorded reasoning:** step13 describes differing lower-node texture and native checks. Step25 calls the pale tissue granulomatous/foreign-body giant-cell areas; step27 says no convincing metastasis. These are the agent's recorded judgments. Specialist adjudication has not validated them; do not present them as clinical findings or a corrected reference.
- **Output:** retained bytes are `{"points":[]}
`, 14 bytes, hash below; no point confidence values exist because no points were submitted. Display empty answer and nonempty source reference together only after the chronological outcome reveal. Source-centered post-hoc review images are separate evidence, never images delivered to this attempt.
- **Limits:** one selected slide and one attempt do not establish population sensitivity, specificity, model ranking, causal failure mechanism, or source-label error. No new trial or scorer execution occurred for this mapping.

## Proposed eight chapters

1. **Whole-slide question:** actual unannotated overview, native grid and physical scale, output contract; show source identifier separately from image analysis.
2. **Source and evaluator boundary:** native TIFF/pyramid/overview/helper visible; XML/private groups hidden. Explain 54 polygons versus 30 study groups without exposing the reference prematurely.
3. **First native sampling:** step10 six helper footprints followed by exact step12 contact sheet; orient every panel on the native overview.
4. **Detail selection:** exact step15 six 1024 panels and their smaller footprints inside the original helper reads; keep the agent's suspicion text attributed.
5. **Pyramid route:** exact four step19 JPEGs, scale16 transforms and explicit bottom padding; distinguish direct-read context from helper ledger.
6. **Second native sampling:** four step20 helper reads, exact step22 contact and step24 detail sheet; retain composite label occlusion.
7. **Decision and artifact:** chronological step25 judgment, step26 empty JSON, step27 completion; call it a recorded negative judgment on a reference-positive slide.
8. **Reference reveal and limits:** source XML red contours, 30 declared groups, retained reward1 versus 0/30 recall, 11/30 oracle centers inside helper footprints, direct-read caveat and specialist-review boundary.

## Verified source pins

Hashes below were reread on 2026-10-12. Runtime/source assets stay local. `inventory.json` records every frozen file; no preparation, scorer or authoring module was executed. Paths beginning `TASK/` expand to the frozen snapshot above.

| Source | SHA-256 |
| --- | --- |
| `TASK/environment/Dockerfile` | `b4cb02db50b4bc9f0d489356f3d6c9f05ab0dc060be868a26b9b9e94acd47339` |
| `TASK/environment/data/overview.jpg` | `5064c9a9f12b0189b84153894ec3a4f7edc95f2e148b5be5b335c84aa5b39b77` |
| `TASK/environment/data/slide.tif` | `73c9766616c40aff2bd6315eb44cd39e7b3d6bb7292cb52e25d3872256baee30` |
| `TASK/environment/docker-compose.yaml` | `e8541c90c19542cffc12fe045b2961355d5592af13d7789521879f556af4dd5f` |
| `TASK/environment/tools/read_slide.py` | `27bac7a2fc952d749bc95b504c1362c1b53d85b509fa4baf875603d82b1b2376` |
| `TASK/instruction.md` | `1849bd1bcef876f92ea1735295f40a194c11b5339ec5ea80a4a2ca887c7c4628` |
| `TASK/solution/reference/points.json` | `b0caae39c9e983ad61c037d28bf3ecc9e3b2891e63dac1e1bdcc345a61ceb550` |
| `TASK/solution/solve.sh` | `1925a2ffacce481631dc43b4e56f5a435e08b98a0a276905a6c4932d9aba1593` |
| `TASK/task.toml` | `abf63373d6d0c6d44a2c1ea6d5593021f6e2572b7301f506a15901afc98b9c6a` |
| `TASK/tests/Dockerfile` | `d23564b057948a7676806382604abcee333185d627d0c74b72380cc2aa1268e3` |
| `TASK/tests/reference/reference.json` | `872216305692bdedf3cf50c0fcdd4e3d9be847530eb5727272d1670876d0544c` |
| `TASK/tests/score.py` | `8dd67c1b65f31dc5d6106b753ccf2e10fbc1fba302ff1c7f857b4a840ffd43d1` |
| `TASK/tests/test.sh` | `95c8f5717fef5e658dba6f5c75b7bed2a658fdc6e61b627550ed54b6099c0a2e` |
| `.local/wsi-ground-truth/camelyon/tumor_084.tif` | `73c9766616c40aff2bd6315eb44cd39e7b3d6bb7292cb52e25d3872256baee30` |
| `.local/wsi-ground-truth/camelyon/tumor_084.xml` | `d7c8c3911298cc9428386993baf281ce7eb033b4fce244d0af4f431787081210` |
| `.local/wsi-ground-truth/source-metadata/camelyon-license.txt` | `d3f9346ae36af5c23f746e68e3a645bf00a41ab6f2d5570d4219eea9458d75e7` |
| `.local/wsi-ground-truth/source-metadata/camelyon-readme.md` | `5c217b1135810d0ca2275b372b5cf054c4a22d48741111c9908bb295248c56c1` |
| `.local/wsi-ground-truth/source-metadata/camelyon-checksums.md5` | `5e4a4efe198cd0427d32f000c7f556f52fbf7f8a422d5210a7c1e5a12ab4ce08` |
| `datasets/receipts/wsi-agent-v2-camelyon-cases.json` | `fa825ae41f6f8687015c8908a3e43cf7dc80805d3e9ec1e0566acf50bd32e9f7` |
| `groups/lesion-localization/experiments/wsi-camelyon-lesion-v2-sol6-xhigh/protocol.md` | `bfe8d85effc35b2f69c6c451f42258a3ccb8622bc4391a0469300335aeafdbfe` |
| `groups/lesion-localization/findings/evidence/wsi-sol6-xhigh-v2-diagnostic-synthesis.json` | `4c5de475c63d57989affcc92d67c00646892b0bf14179884bfdd5d7e41cc87aa` |
| `groups/lesion-localization/experiments/wsi-camelyon-lesion-v2-sol6-xhigh/evaluations/observation-b711afaf4d7eae2e7e51bea6.json` | `5a1cc77b5ccf9c3f1ae8668daaccec1b3e8fbc45753d20326bf5530a961b9a4b` |
| `groups/lesion-localization/experiments/wsi-camelyon-lesion-v2-sol6-xhigh/attempts/attempt-9acd94eaa875417b.json` | `cb4798a8c3b51f2e2a54262177e7d40d5df5fa10aed71c6e6edf53fd45095681` |
| `.local/anatomy-pose/wsi/source-resolution-20261012.json` | `b54dbab83da830ed3c854091ea8253e65d62995981067c3e93387abc4099a183` |
| `.local/attempts/attempt-9acd94eaa875417b/execution.json` | `bc739155243d3ae51b969eb3c194abe4c8ee9bdae127daf370b33fc87dc07eda` |
| `.local/attempts/attempt-9acd94eaa875417b/job/task__AbJ8DUi/agent/trajectory.json` | `111c267bafa245710e71d8df58319daf5c65de70640ec01f3b6dd6080d2ae9b9` |
| `.local/attempts/attempt-9acd94eaa875417b/job/task__AbJ8DUi/agent/codex.txt` | `1b039bf20399b372864f24bf37532d4a285580b86c0abe3f63837351ef1a3520` |
| `.local/attempts/attempt-9acd94eaa875417b/job/task__AbJ8DUi/verifier/test-stdout.txt` | `5fb188ede824a9882e867ade9c37ea21d25c020b73962df004aec7b89c08e9c9` |
| `.local/attempts/attempt-9acd94eaa875417b/job/task__AbJ8DUi/artifacts/app/answer/points.json` | `1d945a1dc8f83d34d75fc3f00703dbcc1df07b4e4aabbd5cfba6179c02835979` |
| `.local/attempts/attempt-9acd94eaa875417b/job/task__AbJ8DUi/artifacts/app/work/read-ledger.jsonl` | `2ebc3fe460bb597573f8b3d0745c6c89ef850f6fb1713884f4f756f54396e9a8` |
| `groups/lesion-localization/experiments/wsi-camelyon-lesion-v2-sol6-xhigh/freezes/freeze-f71944ae9bec74d0acd47ebf.json` | `14b64933a2a73471546d030c25f26abfcce8aeddb80b825c4b5711228245f800` |

## Remaining production gaps

**No source acquisition blocker:** actual TIFF, overview, helper, source XML, frozen evaluator/reference, exact delivered bytes, output and verifier are present and pinned. Coordinate/display mappings are complete. Presentation still needs the canonical story/asset recipe, a native navigator with static fallback, explicit legends, narrow-layout/reference-reveal review and an independent source-pinned acceptance receipt. Those remain main-agent work; this file does not change catalogue bindings or acceptance status. The publisher's full-annotation statement is supported by retained README bytes; pathology interpretation and biological lesion identity remain unresolved specialist questions.
