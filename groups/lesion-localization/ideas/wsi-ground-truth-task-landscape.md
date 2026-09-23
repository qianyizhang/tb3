+++
schema_version = 2
kind = "idea"
id = "wsi-ground-truth-task-landscape"
group_id = "lesion-localization"
title = "WSI task landscape: ground truth before task selection"
idea_state = "exploring"
source = "codex://threads/01a0c9be-5bd3-7c21-af12-4c012196fff7"
+++

# WSI task landscape: ground truth before task selection

Which whole-slide pathology sources provide obtainable, task-matched ground truth for agent search, measurement, tissue reasoning and correspondence?

## Prior findings

### Source screen — 2026-09-22

User request: brainstorm WSI tasks again, starting with a broad search for data
with ground truth. This is a source/documentation screen, not an acquired dataset
inventory or an experiment. No WSI payloads were downloaded, accounts registered,
access agreements accepted, authors contacted, or model trials launched.
Recommendations below are by the assistant; the user has not selected a task.
No prior WSI idea was found in the current workbench search.

The owning group is the initial lesion-search entry point. Registration,
anatomical labeling and multimodal candidates are retained here for comparison;
a selected study should move into its appropriate scientific group through a
linked new idea, without duplicating this source screen.

### What counts as usable GT

For every candidate distinguish: original WSI versus released crop; spatial
annotations versus slide/case labels; exhaustive target coverage versus selected
ROIs; human annotation versus corrected machine labels versus predictions; public
reference files versus a hidden challenge evaluator. A public image does not imply
a downloadable reference. A blank annotation region is not automatically negative.

Access below means a source-documented route, not a successful local download.
Exact file pairing, release hashes, read compatibility and license text still need
sample-level verification. Dataset counts are source/version-specific and are not
counts of locally usable cases.

### A. WSI spatial references and morphology

| Source | Image/GT unit and scope | Access and caveat | Candidate task |
| --- | --- | --- | --- |
| [CAMELYON16 / 17 publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC6007545/), [official data](https://camelyon17.grand-challenge.org/Data/) | Original release: 399 CAM16 and 1,000 CAM17 lymph-node WSIs. Lesion contours for CAM16 and 50 CAM17 slides; CAM17 also supplies patient-level pN labels in training. References were prepared with expert supervision and cytokeratin IHC when needed. | Public download routes. CAM17 training micro/macro metastases are exhaustively annotated in its annotated subset; isolated tumor cells are not. Do not call all 1,000 CAM17 slides densely annotated. Selected-file exclusions and updated references need checking. | Search the full slide for small metastases, return locations/contours and physical extent; later aggregate multiple nodes per case. |
| [HiESD](https://www.nature.com/articles/s41597-025-05679-1), [author repository](https://github.com/JSGe-AI/HiESD) | 104 gastric ESD WSIs, 44 patients, 308 tissue strips; 10 region-level histotypes. SVS, XML, downsampled masks and strip-to-slide mappings. | Original WSIs on Figshare; other files on the linked Hugging Face repository. Two external cohorts are private. Authors explicitly warn that grouped gland annotations are imprecise at boundaries and recommend patch classification. Unannotated tissue exists. QC masks are GrandQC outputs, not manual QC GT. | Find and map selected histotypes by tissue strip, quantify coarse distributions; avoid exact gland boundaries, invasion depth or margin claims without additional GT. |
| [BEETLE release](https://zenodo.org/records/16812932), [benchmark](https://beetle.grand-challenge.org/) | 587 development biopsies/resections; four classes: invasive epithelium, non-invasive epithelium, necrosis, other. JSON/XML polygons and pyramidal TIFF masks at about 0.5 microns/pixel. | Public development annotations; external 54-WSI/170-ROI evaluation annotations are hidden. Some WSIs must be obtained separately from TIGER. Annotation coverage must be checked per slide. The parsed release page did not expose a readable license value. | Distinguish invasive from non-invasive regions, recover small dispersed tumor areas, assess compartment areas within valid annotations. |
| [PAIP2019](https://paip2019.grand-challenge.org/) | Liver cancer, 100 WSIs: 50 training, 10 validation, 40 test. Expert annotations of total tumor and viable tumor area. | Training GT provided; validation/test references reserved. Requires account, participation and signed data-use/confidentiality agreement; access credentials are emailed. | Produce both masks and viable-tumor/total-tumor area fraction. Keep the area metric separate from clinical treatment response. |
| [HuBMAP Hacking the Kidney, publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC10356924/) | Post-competition description: 30 PAS kidney WSIs with 7,102 glomeruli, plus 7 colon WSIs with 395 crypts. Polygon annotations initialized automatically, then inspected/corrected by subject experts. | Publication says all competition data were released via HuBMAP after the challenge. Older Kaggle page describes an earlier 20-image/8-training release; use the publication-linked collection rather than mixing counts. | Locate/count glomeruli across tissue, draw contours and measure size distributions. These labels do not establish glomerular disease or sclerosis grades. |
| [KPIs2024](https://sites.google.com/view/kpis2024/home), [paper](https://arxiv.org/abs/2502.07288) | Over 10,000 glomeruli across 60+ PAS WSIs from rodent CKD models; patch and slide-level detection/segmentation tasks. | Synapse route; organizers state training, validation and test data are released. Need confirm exact reference files and access terms. Animal data, not human clinical renal pathology. | Exhaustive glomerulus search and counting under diseased morphology; species-specific conclusions. |
| [PANDA](https://panda.grand-challenge.org/data/), [organizer account](https://www.wouterbulten.nl/posts/panda-challenge/) | Roughly 11,000 prostate biopsy WSIs with slide Gleason/ISUP labels and label masks. | Kaggle; official page states noncommercial share-alike terms. Mask provenance, institution-specific label semantics and disagreement need audit before any fine-boundary evaluation. | Whole-slide grading and evidence selection; do not treat every training mask as independently adjudicated gland GT. |
| [PANDA-PLUS](https://pmc.ncbi.nlm.nih.gov/articles/PMC12858358/) | 546 PANDA WSIs with full-resolution glandular graded masks and expert-assigned scores, created through a supervised annotation workflow. | Full new masks are available for academic research **on qualified request**, with intended use and affiliation. PANDA WSIs remain on Kaggle. Public PANDA-PLUS-Bench tiles are a different derivative. | Gland pattern mapping and grade-composition audit after reference access; disagreements with original PANDA are reference differences, not automatically proven errors. |
| [SICAPv2 v2](https://data.mendeley.com/datasets/9xxm58dvs3/2), [paper](https://arxiv.org/abs/2105.10490) | Prostate histology with global Gleason scores and local grade annotations. | Mendeley Data, CC BY 4.0. Source abstracts and derivative descriptions differ in WSI totals; inspect actual release contents, coordinates and splits before assigning a count or claiming native WSI availability. | Local-to-global grading and cribriform-pattern exploration, conditional on exact available labels. |

### B. Tissue context, cells and mitoses

| Source | Image/GT unit and scope | Access and caveat | Candidate task |
| --- | --- | --- | --- |
| [TIGER](https://tiger.grand-challenge.org/Data/) | WSIROIS: 195 WSIs with tissue and immune-cell annotations in selected regions. WSIBULK: 93 slides with coarse tumor envelopes. WSITILS: 82 with pathologist-estimated slide TIL scores. | Public AWS download without an AWS account. Annotations/RUMC/JB slides are CC BY-NC 4.0; TCGA rights separate. Sets have different GT semantics; do not add their counts as independent patients. | In annotated regions, distinguish tumor/stroma, find lymphocytes and plasma cells, compute compartment-specific density. Clinical sTIL area percentage is not simply a cell count. |
| [PanopTILs](https://sites.google.com/view/panoptils/) | 1,709 ROIs from 151 TCGA breast patients; colocated tissue regions and nuclear types/boundaries. | Two distinct versions: pathologist-approved manual labels for validation, and algorithmically expanded labels for training. CC0 on source page. Released unit is ROI, not exhaustively annotated WSI. | Count cells conditional on tissue compartment; repair cell-type assignments using surrounding tissue. Use manual validation flavor as reference. |
| [PUMA](https://puma.grand-challenge.org/dataset/) | Melanoma: 310 selected 1,024-square ROIs with 5,120-square context; public training 206 ROIs. Tissue and nuclei GeoJSON annotations, medically annotated and dermatopathologist-corrected. | Private final test; training file `training_set_metastatic_roi_103` has a documented annotation correction. Full-WSI navigation is not supported by this crop release alone. | Joint tissue/cell classification, necrotic versus viable context, tumor-cell/immune-cell counting. |
| [MIDOG++ / MIDOG2025](https://midog2025.deepmicroscopy.org/datasets/) | Mitosis locations in selected tumor regions across human and animal domains; 2025 also provides expert-voted normal/atypical mitosis subclassification. | Public dataset links; official pages differ between 503 tumor cases and 454 labeled images, so release identity/counts require manifest audit. Do not infer a full-slide mitotic hotspot from selected hotspot ROI annotations. | Mitosis verification/counting in a fixed physical area; atypical-vs-normal adjudication. |
| [MITOS_WSI_CMC / CCMCT](https://midog2025.deepmicroscopy.org/datasets/) | Whole-slide mitosis annotations: 21 canine mammary carcinoma WSIs with 13,907 mitoses; 32 canine mast-cell tumor WSIs with 44,880. | Public source datasets linked by the organizers. Animal disease scope must stay explicit. | Stronger source for full-slide mitotic hotspot search than ROI-only human MIDOG data. |
| [Lizard](https://arxiv.org/abs/2108.11195), [PanNuke](https://arxiv.org/abs/2003.10778) | Colon nuclear instance segmentation/types; pan-cancer nuclear instance segmentation/types respectively. | WSI-derived crops. Semi-automatic annotation and review provenance differ. Lizard reuses other datasets, including PanNuke/CoNSeP; these are not independent cross-dataset controls. | Small local counting/segmentation controls; not full-slide search benchmarks. |
| [DigestPath](https://www.sciencedirect.com/science/article/pii/S1361841522001323) | Colorectal tissue segmentation and signet-ring cell boxes. Publication describes about 20,000 signet-ring cells and 1,000 segmented tissue images across the challenge. | Challenge download page was not accessible in this screen. Released crop/full-slide granularity and complete-versus-partial cell annotation require inspection; publication totals are not public-training counts. | Suspicious-cell localization or colorectal tumor extent within verified annotated images. |
| [SemiCOL](https://www.semicol.org/data/) | Manual tissue regions from 20 WSIs and separate weakly labeled multi-center slide collections. Nine tissue classes plus background and ignore pixels. | Challenge access/account route; test sets private. Weakly labeled WSIs were cut into 10-mm-square images. Some same sections were scanned twice. A tile from a tumor-positive slide can be tumor-free. | Tumor/stroma/mucin/necrosis region labeling and aggregation; paired-scanner consistency if matched data are accessible. |
| [WSSS4LUAD](https://arxiv.org/abs/2204.06455) | 10,091 training patch labels and dense pixels in validation/test images, sourced from 87 lung adenocarcinoma WSIs. Tumor epithelium, tumor-associated stroma, normal. | Paper says entire dataset released; current direct challenge endpoint was unavailable in this screen. Pathologist-in-the-loop AI-assisted labels, reviewed by a board. | Tissue classification/segmentation; source WSI count does not prove native slides with full coverage are released. |

### C. Correspondence, quality, slide labels and molecular references

| Source | Reference type | Access and task boundary |
| --- | --- | --- |
| [ANHIR](https://anhir.grand-challenge.org/Data/), [original paper](https://cmp.felk.cvut.cz/ftp/articles/kybic/Borovec-ieeeTMI2020.pdf) | Manually corresponding landmarks; 355 histology images, 18 stains, 481 registration pairs. | Training landmarks public; some held out server-side. Challenge join/download route. Multiple organs/species and released scales; not uniformly native pyramidal WSI. Candidate: transfer landmarks across stains and measure target-registration error. |
| [HyReCo](https://arxiv.org/abs/2106.13150), [institutional source](https://www.diagnijmegen.nl/publications/lotz21/) | 81 slide pairs and about 3,000 landmarks, including consecutive sections and same-section restaining. | Public release described by authors; IEEE DataPort endpoint was inaccessible to this research tool. Candidate: corresponding-region retrieval/registration. Same-section and consecutive-section accuracy must be separated; a landmark reference is not a dense deformation field. |
| [ACROBAT](https://acrobat.grand-challenge.org/data/) | Paired H&E and IHC WSIs, landmark registration evaluation. | Training has no landmark annotations; validation/test source points public, target points secret. Strong external benchmark but not a ready local reference set. Published pyramids start at 10x despite original 40x scanning. |
| [GrandQC manual test release](https://zenodo.org/records/14039591), [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11649692/) | Expert artifact masks on crops from 318 slides across breast, colon, kidney and prostate, released at three resolutions. | Public 5.4-GB crop release, academic/noncommercial terms. Full TCGA QC masks are algorithm outputs, not manual GT. Candidate: locate folds/blur/pen marks and define usable tissue; no clinical accept/reject or re-scan label established. |
| [BRACS](https://www.bracs.icar.cnr.it/background/) | 547 breast WSIs from 189 patients, seven slide/ROI classes, labeled by three expert pathologists. | Official pages disagree on ROI count (4,537 vs 4,539). Access terms/download route not completed in this screen. Candidate: classification and supporting-region selection; not exhaustive lesion-boundary scoring. |
| [Dartmouth lung adenocarcinoma](https://bmirds.github.io/LungCancer/) | 143 WSIs; five predominant patterns, consensus of three pathologists. | Form/email download route. Slide-predominant pattern is GT; all minor-pattern locations are not thereby annotated. Candidate: multi-region sampling followed by predominant-pattern classification. |
| [HEROHE](https://ecdp2020.grand-challenge.org/Dataset/), [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9410129/) | H&E slides with case HER2 status derived from IHC/ISH. | Official site says 360 train/150 test; paper describes 359 usable train/150 test. CC BY-NC-ND 3.0. No tumor localization or released IHC slides in the paper's task. An assay outcome is not visibly decidable cell-level GT. |
| [HEST](https://github.com/mahmoodlab/HEST/blob/main/README.md) | Paired spatial transcriptomics and histology; current README describes 1,276 samples, versus 1,229 in the publication. | Public access route and noncommercial share-alike terms. Measured expression is a biological target; computational nuclei segmentations and inferred cell types are not all manual GT. Candidate: morphology/molecular spatial correspondence after assay/alignment audit. |
| [REG2026](https://reg2026.grand-challenge.org/) | WSI report generation, structured pathologist reasoning and visual-grounding task interfaces. | Verified account; test reports/reasoning hidden. Source lists slide and annotation corrections and a publication embargo until official papers/proceedings, unless organizers grant an exception. Grounding examples are format samples, not an exhaustive public localization set. Record as a research lead, not ready local GT. |

### Cross-source risks that affect selection

- TIGER, BEETLE, PanopTILs, BCSS and NuCLS share TCGA-BRCA origins. PANDA-PLUS
  derives from PANDA. Splitting by dataset name does not establish independence.
- Pair patients, blocks, sections, rescans and tiles before splitting. If patient
  identifiers cannot be recovered, retain that limitation instead of calling a
  slide split patient-independent. Public benchmark exposure/pretraining remains
  possible even after filenames and source IDs are removed from solver inputs.
- Preserve original resolution, level-0 coordinate conventions, physical pixel
  size and transforms. TIGER labels at 0.5 microns/pixel cannot be applied directly
  to a 0.25-micron/pixel original TCGA image without the recorded transform.
- Score only a verified annotation-valid domain. Do not penalize detections in
  unannotated regions as false positives, or rank global hotspots against a few
  preselected fields. Shared tissue envelopes are not exact invasive fronts.
- Reference disagreement needs adjudication; neither a newer annotation nor an
  agent's plausible explanation automatically invalidates the original reference.
- CAMELYON official pages expose conflicting license statements (data page CC0;
  older download page CC BY-NC-ND 4.0). Pin the specific supplying release's terms
  before reuse/redistribution. Do not resolve this by choosing the most permissive
  page. [Data](https://camelyon17.grand-challenge.org/Data/),
  [older download](https://camelyon17.grand-challenge.org/Download/).

### Task sketches — assistant proposals, not selected studies

| Task | Solver sees and returns | Reference and proposed measurements | Main unresolved condition |
| --- | --- | --- | --- |
| Budgeted whole-slide metastasis search | WSI with overview/region-read tools; lesion coordinates, confidence, optional polygons and evidence crops | CAM16 lesion references; lesion sensitivity, false positives/slide, physical extent error and tissue/search coverage versus tool budget | Verify exhaustive target scope and include genuine negatives, tiny lesions and difficult benign tissue. |
| Gastric tissue-strip lesion map | HiESD WSI and taxonomy; each strip's histotypes with coarse locations and area proportions | Region masks and strip mapping; class-specific region detection and coarse-area agreement in valid domains | Grouped gland outlines cannot justify fine-boundary, invasion-depth or surgical-margin scoring. |
| Whole-slide glomerulus inventory | PAS WSI; object centers/contours, total count and size table | HuBMAP corrected polygons; object precision/recall, count error, per-object area/overlap | Verify full target coverage and edge-object rules; no unprovided disease grading. |
| Tissue-aware immune-cell measurement | TIGER WSI plus an explicit evaluation ROI, or PanopTILs manual ROI; tissue regions and compartment-specific cell locations/counts | Joint tissue/cell GT; compartment Dice, cell F1 and count/density error | A fixed ROI tests tissue reasoning/counting, not autonomous full-slide hotspot selection; density differs from clinical sTIL percentage. |
| Viable tumor fraction | PAIP WSI; total and viable tumor masks plus a ratio | Two reference masks; each overlap/area error and ratio absolute error | Access agreement and case-level mask review; distinguish a geometric reference ratio from treatment-response GT. |
| Cross-stain point/region transfer | ANHIR/HyReCo image pair and query point/ROI on the source; target location and optional transform | Held-private paired landmarks; target-registration error and retrieval recall | Locally obtainable target points and physical calibration; separate restained/consecutive tissue. |
| Mitosis hotspot search | Fully annotated canine WSI; ranked equal-physical-area fields and all counted mitoses | Exhaustive mitosis labels; hotspot count regret and object detection error | Human MIDOG hotspot crops cannot establish this global GT. Animal result stays an animal result. |
| Artifact-aware measurement audit | Manual GrandQC crops or a verified linked full image; artifact polygons and usable-tissue area | Manual artifact masks; class overlap and retained-tissue error | Release is crops; no invented diagnostic fitness or re-scan threshold. |

### Proposed next source audit

Start a small acquisition/GT inspection, if requested, with CAMELYON16, HiESD and
HuBMAP kidney; use TIGER/PanopTILs for tissue-plus-cell reasoning and HyReCo/ANHIR
for correspondence. PAIP and PANDA-PLUS remain access-dependent options. This order
is based on task-matched spatial references and varied task mechanisms, not on an
assumption about which tasks models will fail.

For each selected source: obtain one positive and an appropriate negative/control
where the task supports negatives; retain exact source/version/license and hashes;
confirm image/reference pairing, valid-domain coverage and physical coordinates;
render representative overlays with matching color legends; then define input,
output and evaluator-only references. Establish oracle and no-op controls before
claims from a nondiagnostic trial. No model trial is implied by this recommendation.

## Reopen when

- The user chooses a task family or requests bounded sample acquisition.
- Native WSI plus reference files can be inspected for the chosen release.
- Access, license, coordinate alignment or GT completeness changes the ranking.
- Expert adjudication resolves a reference disagreement needed by the task.

### Bounded acquisition and teaching viewer — 2026-09-22/23

User selected the four suggested routes and explicitly asked for one/few paired
samples and a visual explanation of data, GT and task. This authorizes acquisition
and teaching preparation; no model trial or benchmark promotion was requested.
Fourth route uses TIGER as the representative; PanopTILs was not acquired.

Acquired four complete source images (1,193,104,862 bytes total): CAMELYON16
`tumor_091`, HiESD `e4442edf-05b0-431b-bf61-ccf2d8cdebb6`, HuBMAP kidney
`aaa6a05cc`, and TIGER `114S`. TIGER also has three exactly matched ROI images and
masks. Selected-file URLs, publisher metadata, SHA-256 hashes, HuBMAP ZIP-member
CRC32 values, native coordinate transforms and measurements are retained in
[the source receipt](../../../datasets/receipts/wsi-teaching-samples.json).
Extra small XML/preview files belong to selection screening and are not additional
native-image cases. Native data and generated media remain under
`.local/wsi-ground-truth/`.

The [four canonical task briefs](../presentation/wsi-sample-catalog.json) feed
both the normal Task Explorer and a local [interactive teaching viewer](../../../.local/wsi-ground-truth/explainer/index.html).
The viewer offers 10 source-derived views, explicit GT reveal, physical scale
bars, crop-position maps, and separate TIGER tissue/cell layers. Read-only visual
preparation uses [group-owned methods](../methods/wsi-samples/README.md).
GT-selected CAMELYON, HiESD and HuBMAP detail crops are reader aids that remove
search; they must not silently become full-slide task inputs.

Sample-level findings:

- CAMELYON16 has 6 Tumor polygons and 1 Exclusion polygon in this file; that is
  not a connected-lesion count. The relatively small file has large positive
  regions, so it is a teaching example rather than evidence for difficult sparse
  metastasis search. Native pyramid padding must not distort coordinate scale.
- HiESD has two strips and six XML region classes in this sample. The released
  category PNG contains 1,569 unique RGB colors, while XML refers to six category
  colors; do not silently treat every interpolated color as a new class. The
  teaching overlay uses official coarse-grid XML, scaled by 64 for native crops.
  Its 139,324,209-byte SVS matches the publisher MD5.
- HuBMAP JSON contains 99 glomerulus polygons on the downloaded TIFF grid.
  OME spacing is 0.65 µm/px. Only image and GT/anatomy members were extracted
  from the 33.6 GB archive; the whole-archive checksum was not verified.
- TIGER source ROI counts are 175, 323 and 20 merged lymphocyte/plasma-cell
  boxes. All three ROI PNGs match native TIFF crops exactly (RGB MAE 0).
  TIFF spacing is 0.456694 µm/px rather than assuming a nominal 0.5. The
  centroid-to-tissue assignment demonstration is reference-derived and is not
  a model result or clinical sTIL area score.

Assistant recommendation: start with HuBMAP for an auditable object inventory,
or TIGER for tissue-conditioned counting with explicit with/without-tissue-GT
conditions. This is an assistant recommendation, not a user selection or claim
of demonstrated model difficulty. Next promotion requires a frozen assistance
condition, scoring rules, source/split exposure audit and relevant additional
cases (including CAMELYON negatives).

Validation: explicit four-dataset byte audit verified all 25 declared source
files. `med brief check` and `med check` passed with 32 dataset snapshots and no
missing media. Scoped method Ruff checks passed. The standalone teaching viewer
passed the repository disposable Chrome harness for all ten views, default-hidden
GT/reveal/hide behavior, independent TIGER layers and mobile page bounds, with no
browser errors. Native overlays and desktop/mobile renders were visually reviewed.
These checks establish acquisition/rendering integrity, not clinical correctness
or a model result. No commit, publication or trial was performed.

### Presentation revision — 2026-09-23

- **User direction:** review all similar prose blocks; prefer concise, structured
  language. The two browser comments were examples, not the full scope.
- **Revision:** all four briefs now use short goals, labeled facts, action lists,
  scoring lists and color tables. Viewer guidance, numeric explanations, captions,
  recommendations and footnotes were shortened; GT limits remain explicit.
- **Review:** checked all four chapters with every detail panel expanded; no long
  prose blocks or page overflow found in the desktop pass. Source data and scores
  are unchanged.
- **User authorization:** clean up and commit this WSI work. Other task changes
  retain separate ownership.

### First agent-test recommendation — 2026-09-23

In response to the user's question about what to test after the WSI curation,
the assistant recommends a bounded **HuBMAP whole-slide glomerulus inventory**
pilot first. This is an assistant recommendation, not a user task selection or
authorization to launch a trial. The single `aaa6a05cc` slide is a diagnostic
case for the workflow; its 99 paired polygons do not establish generalization.

- Solver input: native PAS TIFF, physical scale, overview and coordinate-based
  tile reader. Keep glomerulus JSON, reference-derived crops and teaching overlays
  out of the solver context. Freeze a read budget and log every viewed region.
- Output: deduplicated level-0 object centers, confidence and optional contours;
  record measured area only when a contour is supplied. Permit explicit
  unreviewed regions so coverage is visible.
- Evaluation: audit annotation-valid domain and edge-object rules first. Freeze
  one-to-one object matching and report recall, false/duplicate detections,
  count error and recall versus read budget; score contour overlap and physical
  area error separately for matched objects. Use no-op and full-reference oracle
  checks for the scorer, plus a uniform-scan baseline under the same read budget.
- Next distinct mechanism: TIGER `114S` official ROIs for tissue-conditioned
  immune-cell counting, with and without tissue GT supplied. Score tissue,
  cells and compartment attribution separately; do not infer full-slide search
  or clinical sTIL scores from these ROI annotations.
- Later flagship search: CAMELYON16 after adding appropriate negative and small
  lesion cases and freezing lesion merging/exclusion rules. The acquired
  `tumor_091` is a positive teaching example with large regions. HiESD is best
  reserved for coarse strip/region mapping because its boundaries are not a
  fine segmentation reference.

Before interpreting any pilot as task performance, pin source/split exposure,
assistance condition and evaluator-only references. Additional independent
cases are required for a comparative or generalization claim.

### Diagnostic experiments selected — 2026-09-23

- **User direction:** In [the current task](codex://threads/01a0cbf7-5068-7001-90be-102123fff079), the user accepted the proposed WSI directions and requested Sol 6 at xhigh effort for the experiments, with active babysitting. This authorizes the bounded diagnostic trials and supervision; it does not promote these tasks or change the GT limits above.
- **Preparation:** Four experiment records cover HuBMAP inventory, TIGER's image-only and tissue-supplied ROI conditions, CAMELYON positive-slide search, and HiESD coarse mapping. All five task previews and Harbor oracle/no-op pairs passed their expected control contrast.
- **Execution boundary:** Two HuBMAP model invocations ended before analysis with credential/model-routing errors. They are retained as execution errors, with no model performance result. The remaining model conditions await a working `gpt-6-sol` route; do not retry unchanged or substitute another model.

### Model switch to Astra medium — 2026-09-23

- **User direction:** The user asked whether the new model was generally unavailable and directed us to try Astra medium. This replaces Sol 6 xhigh for the pending diagnostic trials; it does not change the frozen Sol attempts or their no-verdict interpretation.
- **Access check:** Official API documentation lists `gpt-6-astra` with medium reasoning. The installed `codex` 0.147.0 rejected Astra because it needs a newer version. The desktop app's bundled CLI 0.155.0-alpha.9.2 completed a tiny Astra medium request, including from an isolated Codex home populated with the existing auth file. Thus the earlier Sol error does not show that all GPT-6 models are unavailable to this account.
- **Study identity:** Four new Astra medium experiment records point to the same five local task inputs, scorers and reference boundaries. Source task digests and the exact-task oracle/no-op controls remain applicable. The old Sol records remain separate. Full WSI dispatch awaits an isolated Harbor route verified with a tiny task, followed by sequential model runs and trace review.
