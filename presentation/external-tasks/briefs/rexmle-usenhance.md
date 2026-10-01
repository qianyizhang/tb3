# Enhance handheld ultrasound images

Develop and apply a prediction method to enhance handheld ultrasound images.

> **Actual gap:** Exact paired PNGs and prepared split IDs are absent; filename pairing does not establish patient isolation or registered frames. Symbolic protocol only; no enhanced image or score. [Official acquisition](https://ultrasoundenhance2023.grand-challenge.org/ultrasoundenhance2023/).

## Value

Quality assessment/repair can support image review, but agreement with a benchmark reference does not demonstrate a clinical benefit.

## Given

### Original data

Required low-quality B-mode PNGs are absent locally. Source metadata describes five organs, 109 patients and 1500 pairs; no native pixel geometry or patient/frame correspondence is verified.

### Supplied helpers

ReX public/train low/high PNG pairs are training helpers; public/test exposes only lows, private/test holds highs and labels. Match same filename within organ, prefix organ to image ID; image-ID seed 42 80/20 split does not establish patient isolation.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Private high-quality test PNGs and test_labels.csv are grader-only by source staging. Public training highs are helpers. No reference pixels are shown; later reveal covers public rule mechanics only, not a private image.

## Task specification

Develop a pipeline from allowed public training pairs; infer each required public-test low; submit every image ID and enhanced image path. No specific checkpoint/model or mandatory inference runtime established. Pair registration, patient split and low/high geometry remain source-specific gaps.

## Expected output

Enhanced images saved as PNG and a CSV with image_id and enhanced_image_path.

## Evaluation

Pinned ReX grade.py uses local 11-pixel variance-masked LNCC, SSIM and PSNR (dB), means across merged image rows. It converts to grayscale float32 and resizes enhanced image to high-reference shape; SSIM/PSNR range is joint max-min. Existing leaderboard yields lower-better mean method=min ranks; fallback negative(LNCC+SSIM+PSNR/30) differs description normalized composite. Coverage uses merge row count, not explicit unique-ID/set check. The source copies public grade.py without adjacent metric configuration/leaderboard; standalone runtime recovery is unverified. No score or clinical benefit measured.

## Visual explanation

### Workflow

- Lower-quality handheld ultrasound B-mode images
- Develop and apply a prediction pipeline
- Enhanced images saved as PNG and a CSV with image_id and enhanced_image_path

### Input

**Symbolic input sockets; native source not acquired.** Required low-quality B-mode PNGs are absent locally. Source metadata describes five organs, 109 patients and 1500 pairs; no native pixel geometry or patient/frame correspondence is verified.

### Supplied helpers

**Given material, not an answer reveal.** ReX public/train low/high PNG pairs are training helpers; public/test exposes only lows, private/test holds highs and labels. Match same filename within organ, prefix organ to image ID; image-ID seed 42 80/20 split does not establish patient isolation.

### Reference or output

**Expected artifact, not an actual prediction.** Enhanced images saved as PNG and a CSV with image_id and enhanced_image_path.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Paired training examples from higher-quality ultrasound and the source image conventions. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Improve contrast and noise without inventing structures; paired devices may not depict exactly identical anatomy.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/usenhance/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Exact paired PNGs and prepared split IDs are absent; filename pairing does not establish patient isolation or registered frames. Symbolic protocol only; no enhanced image or score. Recover official low/high pairs with applicable data terms; verify pair pixels, patient/frame joins and split IDs; prove public-train versus private-test separation and grading unit/rank denominator before matching-data or performance claims.
