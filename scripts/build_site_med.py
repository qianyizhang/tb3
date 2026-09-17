#!/usr/bin/env python3
"""Build site_med: Medical Computer Vision in the Agent Era showcase.

Creates standalone, offline-ready HTML pages for:
- index.html (Overview & Executive Synthesis)
- segmentation.html (Domain 1: 3D Organ Segmentation & Tissue Auditing)
- aneurysm.html (Domain 2: Vascular Aneurysm 3D Detection)
- registration.html (Domain 3: Deformable 3D Image Registration & Respiratory Motion)
- vessels.html (Domain 4: Tubular Network Geometry, Airway Routing & CPR)
- cardiac.html (Domain 5: 4D Beating Heart Biomechanics & Strain Modeling)
- landmarks.html (Domain 6: Semantic 3D Anatomical Landmarks & Out-of-FOV Rejection)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / 'site'
MED_DIR = ROOT / 'site_med'

def get_head_html(title, description="Medical Computer Vision in the Agent Era"):
    return f'''<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · MedVision Agent Era</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="css/med_report.css">
</head>'''

def get_nav_html(active_key):
    pages = [
        ('index.html', 'Overview', 'overview'),
        ('segmentation.html', '1. Segmentation', 'segmentation'),
        ('aneurysm.html', '2. Aneurysm', 'aneurysm'),
        ('registration.html', '3. Registration', 'registration'),
        ('vessels.html', '4. Vessels & CPR', 'vessels'),
        ('cardiac.html', '5. Cardiac', 'cardiac'),
        ('landmarks.html', '6. Landmarks', 'landmarks'),
    ]
    nav_links = []
    for href, label, key in pages:
        active_class = ' active' if key == active_key else ''
        nav_links.append(f'<a href="{href}" class="nav-link{active_class}">{label}</a>')
    
    return f'''<header class="site-header">
  <div class="nav-container">
    <a href="index.html" class="brand-badge">
      <span class="brand-dot"></span>
      <span>MedVision · Agent Era</span>
    </a>
    <nav class="nav-menu" aria-label="Domain Navigation">
      {' '.join(nav_links)}
    </nav>
  </div>
</header>'''

def get_chapter_nav(prev_info, next_info):
    prev_btn = f'<a href="{prev_info[0]}" class="chapter-btn">← {prev_info[1]}</a>' if prev_info else '<span></span>'
    next_btn = f'<a href="{next_info[0]}" class="chapter-btn">{next_info[1]} →</a>' if next_info else '<span></span>'
    return f'''<div class="chapter-nav">
  {prev_btn}
  {next_btn}
</div>'''

def get_footer_html():
    return '''<footer class="site-footer">
  <p><strong>Medical Vision in the Agent Era</strong> · Autonomous 3D Perception, Geometric Reasoning & Biomechanical Modeling.</p>
  <p>Synthesized from 40 controlled research rounds (BR-001–BR-040) using Sol/xhigh and Terra/high on public clinical cohorts.</p>
</footer>'''

def build_index():
    nav = get_nav_html('overview')
    footer = get_footer_html()
    head = get_head_html('Medical Vision in the Agent Era', 'Autonomous 3D Perception, Geometric Reasoning and Biomechanics on Volumetric Clinical Scans')
    
    content = f'''<!doctype html>
<html lang="en">
{head}
<body>
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Executive Showcase · 3D Volumetric Imaging & AI Agents</span>
    <h1>Medical Computer Vision<br><em>in the Agent Era</em></h1>
    <p class="lead">How do autonomous coding agents solve complex 3D medical vision tasks? Moving beyond static neural network inference to agents that dynamically write code, render multi-planar projections, register deformable anatomy, and compute clinical biomechanics.</p>
    <p class="hero-meta">Comprehensive synthesis across 6 clinical imaging domains · Sol (Claude 3.7) & Terra (GPT-4o) · September 2026</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">6 Domains</span>
        <span class="keyline-label">From abdominal CT and brain MRA to 4D cardiac mechanics</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">40 Rounds</span>
        <span class="keyline-label">Controlled empirical trials with exact physical verification</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">3D Native</span>
        <span class="keyline-label">Agents directly load, manipulate, and export volumetric tensors</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">Tool-Makers</span>
        <span class="keyline-label">Writing custom viewers, graph routers, and tensor math on the fly</span>
      </div>
    </div>
  </header>

  <!-- Paradigm Shift Section -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / The Paradigm Shift</span>
      <h2>From Static Inference to Agentic Perception</h2>
      <p>Traditional medical computer vision deploys specialized deep neural networks (e.g. nnU-Net, Swin UNETR) trained for fixed input-output mappings on predefined GPUs. In the Agent Era, multi-modal coding agents operate as autonomous computational scientists.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Phase 1 · Volumetric Ingestion</div>
        <b>Multi-Dimensional Data Arrays</b>
        <span>Agents load multi-gigabyte clinical scans (DICOM, NIfTI, MRA, 4D Ultrasound), inspect voxel spacing, affine transforms, and radiodensity ranges.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Phase 2 · Active Code Authoring</div>
        <b>On-The-Fly Algorithm Creation</b>
        <span>Rather than using black-box guessing, agents write Python, SimpleITK, and SciPy scripts to render orthogonal views, compute Hessian filters, and track deformation.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Phase 3 · Clinical Deliverables</div>
        <b>Verified Geometric Outputs</b>
        <span>Generating watertight 3D meshes, 360° curved reformations, Green-Lagrange strain tensors, and millimeter-accurate surgical fiducials.</span>
      </div>
    </div>
  </section>

  <!-- Task Domain Showcase Gallery -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Clinical Domain Showcase</span>
      <h2>Six Frontiers of Agentic Medical Vision</h2>
      <p>Explore the six task domains investigated in this benchmark. Each page provides an interactive viewer, deep agent code analysis, task evolution, and critical evaluation traps.</p>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 24px; margin: 28px 0;">
      
      <!-- Card 1: Segmentation -->
      <div class="contrast-card" style="display: flex; flex-direction: column;">
        <span class="badge badge-teal" style="align-self: flex-start; margin-bottom: 12px;">Domain 01 · Abdominal CT</span>
        <h3 style="margin-top: 0;"><a href="segmentation.html">Organ Segmentation & Tissue Auditing</a></h3>
        <p style="font-size: 14px; color: var(--text-muted); flex: 1;">Can an agent detect when 21 mL of pancreatic tissue is mistakenly labeled as duodenum? Exploring how broad task prompts dilute visual attention, while focused pair audits succeed.</p>
        <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin: 12px 0; font-size: 13px;">
          <strong>Key finding:</strong> Sol missed in 13-organ sweep; caught it immediately when focused on the affected pair.
        </div>
        <a href="segmentation.html" class="chapter-btn" style="text-align: center; justify-content: center; margin-top: 8px;">Explore Domain 1 →</a>
      </div>

      <!-- Card 2: Aneurysm -->
      <div class="contrast-card" style="display: flex; flex-direction: column;">
        <span class="badge badge-amber" style="align-self: flex-start; margin-bottom: 12px;">Domain 02 · Brain TOF-MRA</span>
        <h3 style="margin-top: 0;"><a href="aneurysm.html">Vascular Aneurysm 3D Detection</a></h3>
        <p style="font-size: 14px; color: var(--text-muted); flex: 1;">Autonomous 3D search for deadly 3–7 mm arterial bulges in brain angiograms. Revealing how agents combine Hessian blob filters with orthogonal slice verification—and the trap of open-web dataset leakage.</p>
        <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin: 12px 0; font-size: 13px;">
          <strong>Key finding:</strong> 1 miss, 1 millimeter-accurate localization, 1 autonomous web dataset lookup.
        </div>
        <a href="aneurysm.html" class="chapter-btn" style="text-align: center; justify-content: center; margin-top: 8px;">Explore Domain 2 →</a>
      </div>

      <!-- Card 3: Registration -->
      <div class="contrast-card" style="display: flex; flex-direction: column;">
        <span class="badge badge-blue" style="align-self: flex-start; margin-bottom: 12px;">Domain 03 · Paired Lung CT</span>
        <h3 style="margin-top: 0;"><a href="registration.html">Deformable 3D Image Registration</a></h3>
        <p style="font-size: 14px; color: var(--text-muted); flex: 1;">Aligning lungs undergoing massive respiratory deformation (exhale to inhale). Why 2D source slices fail catastrophically (12.7 mm error) while 3D volumetric depth achieves 2.6 mm accuracy.</p>
        <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin: 12px 0; font-size: 13px;">
          <strong>Key finding:</strong> The q06 landmark failed numerical gates (6.4 mm) but was approved by expert visual review.
        </div>
        <a href="registration.html" class="chapter-btn" style="text-align: center; justify-content: center; margin-top: 8px;">Explore Domain 3 →</a>
      </div>

      <!-- Card 4: Vessels & CPR -->
      <div class="contrast-card" style="display: flex; flex-direction: column;">
        <span class="badge badge-teal" style="align-self: flex-start; margin-bottom: 12px;">Domain 04 · Coronary CTA & MRA</span>
        <h3 style="margin-top: 0;"><a href="vessels.html">Tubular Geometry & Curved Reformations</a></h3>
        <p style="font-size: 14px; color: var(--text-muted); flex: 1;">Repairing broken vessel and airway segmentations, tracing centerlines, and generating 360° rotated Curved Planar Reformations (CPRs). Uncovering the subtle CPR distance-axis metadata bug.</p>
        <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin: 12px 0; font-size: 13px;">
          <strong>Key finding:</strong> Flawless visual repair failed verifier by 8.89 mm due to raw pixel vs millimeter indexing.
        </div>
        <a href="vessels.html" class="chapter-btn" style="text-align: center; justify-content: center; margin-top: 8px;">Explore Domain 4 →</a>
      </div>

      <!-- Card 5: Cardiac -->
      <div class="contrast-card" style="display: flex; flex-direction: column;">
        <span class="badge badge-amber" style="align-self: flex-start; margin-bottom: 12px;">Domain 05 · 4D Ultrasound & Cine-MRI</span>
        <h3 style="margin-top: 0;"><a href="cardiac.html">4D Beating Heart Biomechanics</a></h3>
        <p style="font-size: 14px; color: var(--text-muted); flex: 1;">Reconstructing dynamic 3D ventricular meshes across 30 cardiac phases and computing myocardial strain tensors. Demonstrating why surface tracking is NOT material mechanics, and how clinical EF was underestimated.</p>
        <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin: 12px 0; font-size: 13px;">
          <strong>Key finding:</strong> Dice 0.946 shape agreement hid 7.37 pp radial strain error; clinical tracking misdiagnosed EF.
        </div>
        <a href="cardiac.html" class="chapter-btn" style="text-align: center; justify-content: center; margin-top: 8px;">Explore Domain 5 →</a>
      </div>

      <!-- Card 6: Landmarks -->
      <div class="contrast-card" style="display: flex; flex-direction: column;">
        <span class="badge badge-blue" style="align-self: flex-start; margin-bottom: 12px;">Domain 06 · Spine CT & Brain MRI</span>
        <h3 style="margin-top: 0;"><a href="landmarks.html">3D Landmarks & Out-of-FOV Rejection</a></h3>
        <p style="font-size: 14px; color: var(--text-muted); flex: 1;">Locating exact vertebral centers (C1–L6) and brain fiducials in 3D physical space. Testing whether agents recognize when anatomy is outside the scan or hallucinate missing vertebrae.</p>
        <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin: 12px 0; font-size: 13px;">
          <strong>Key finding:</strong> Sol achieved 0 false detections on cropped CT; autonomous MNI atlas registration doubled MRI accuracy.
        </div>
        <a href="landmarks.html" class="chapter-btn" style="text-align: center; justify-content: center; margin-top: 8px;">Explore Domain 6 →</a>
      </div>

    </div>
  </section>

  <!-- Cross-Domain Synthesis Matrix -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Cross-Cutting Insights</span>
      <h2>Capabilities, Failure Modes & Benchmark Traps</h2>
      <p>Across 40 research rounds, clear patterns emerge regarding where autonomous coding agents excel, where they stumble, and what traps exist in evaluating medical CV agents.</p>
    </div>

    <div class="contrast-grid">
      <div class="contrast-card worked">
        <h4><span style="color: var(--color-green);">✔</span> What Modern Agents Do Exceptionally Well</h4>
        <ul>
          <li><strong>Autonomous Tool-Making:</strong> When standard packages are missing, agents write custom erosion filters, connected component labellers, and slice montages from scratch using NumPy.</li>
          <li><strong>Rigorous Tensor Math:</strong> Flawless calculation of finite deformation gradients, Green-Lagrange strain tensors, coordinate affine transforms, and volume integration.</li>
          <li><strong>Tool & Atlas Orchestration:</strong> Sol autonomously fetched the MNI brain atlas and AFIDs fiducials protocol to boost landmark localization from 3/32 to 14/32 within 3 mm.</li>
          <li><strong>Broad Multi-Scale Search:</strong> Successfully breaking out of trapped local gradient descent by switching to coarse-to-fine patch cross-correlation across 3D physical coordinates.</li>
        </ul>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">✖</span> Where Agents Hit Real Brick Walls</h4>
        <ul>
          <li><strong>Subtle Soft-Tissue Perception:</strong> Failing to differentiate adjacent organs (pancreas vs duodenum) based on internal texture when overall geometric shapes look plausible.</li>
          <li><strong>Sub-Millimeter Surgical Precision:</strong> Coarse localization quickly converges to ~10 mm, but fine surgical placement (<3–5 mm) requires explicit anatomical atlas priors.</li>
          <li><strong>Surface vs Material Motion Confusion:</strong> Assuming that matching the moving boundary of an organ guarantees correct internal physical deformation (the cylinder twist paradox).</li>
          <li><strong>The Unit Indexing Metadata Trap:</strong> Saving CPR curved routes using raw pixel indices instead of cumulative physical millimeters, failing verifiers despite flawless anatomy.</li>
        </ul>
      </div>
    </div>

    <!-- Structured Resource & Stats Ledger -->
    <h3>Comprehensive Benchmark Execution Ledger</h3>
    <p class="small">Summary of representative completed model attempts across the six medical computer vision domains.</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Domain & Task</th>
            <th>Primary Model</th>
            <th>Input Modality</th>
            <th>Execution Time</th>
            <th>Output Tokens</th>
            <th>Estimated Cost</th>
            <th>Key Outcome</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>01. Tissue Absorption</strong> (BR-017)</td>
            <td>Sol / xhigh</td>
            <td>Abdominal CT + 13 Masks</td>
            <td>6m 44s</td>
            <td>10,593</td>
            <td>$1.04</td>
            <td><span class="badge badge-miss">Miss in 13-mask</span> / <span class="badge badge-pass">Pass in 2-mask</span></td>
          </tr>
          <tr>
            <td><strong>02. Aneurysm N02</strong> (BR-016)</td>
            <td>Sol / xhigh</td>
            <td>Brain TOF-MRA (3D)</td>
            <td>5m 46s</td>
            <td>8,763</td>
            <td>$0.98</td>
            <td><span class="badge badge-pass">Located within 1 mm</span></td>
          </tr>
          <tr>
            <td><strong>02. Aneurysm N03</strong> (BR-016)</td>
            <td>Sol / xhigh</td>
            <td>Brain TOF-MRA (3D)</td>
            <td>7m 32s</td>
            <td>13,806</td>
            <td>$1.56</td>
            <td><span class="badge badge-amber">Source-assisted lookup</span></td>
          </tr>
          <tr>
            <td><strong>03. Lung Registration</strong> (BR-028)</td>
            <td>Sol / xhigh</td>
            <td>Paired 4D Lung CT</td>
            <td>14m 53s</td>
            <td>19,420</td>
            <td>$2.15</td>
            <td><span class="badge badge-pass">RMS 2.60 mm (Visual Accept)</span></td>
          </tr>
          <tr>
            <td><strong>04. Coronary CPR</strong> (BR-030)</td>
            <td>Terra / high</td>
            <td>Coronary CTA + RCA gap</td>
            <td>8m 12s</td>
            <td>11,200</td>
            <td>$0.72</td>
            <td><span class="badge badge-miss">8.89 mm Axis Offset Trap</span></td>
          </tr>
          <tr>
            <td><strong>05. Cardiac Mechanics</strong> (BR-035)</td>
            <td>Sol / xhigh</td>
            <td>4D Echo + 30 Phase Masks</td>
            <td>18m 20s</td>
            <td>24,150</td>
            <td>$2.84</td>
            <td><span class="badge badge-pass">Mesh Pass</span> / <span class="badge badge-miss">Radial Strain Miss</span></td>
          </tr>
          <tr>
            <td><strong>06. 3D Landmarks</strong> (BR-040)</td>
            <td>Sol / xhigh</td>
            <td>VerSe CT + AFIDs MRI</td>
            <td>22m 15s</td>
            <td>28,400</td>
            <td>$3.40</td>
            <td><span class="badge badge-pass">0 False Out-of-FOV</span> / 14/32 MRI Pass</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- Future Principles -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Core Takeaways</span>
      <h2>Designing Clinical AI Benchmarks in the Agent Era</h2>
      <p>Lessons learned for evaluating autonomous visual agents on medical data:</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Principle 01</div>
        <b>Track Data Provenance</b>
        <span>Agents with web access will search public dataset repositories and manifests. Scoring visual capability must explicitly separate visual perception from data retrieval.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Principle 02</div>
        <b>Physical vs Metric Gates</b>
        <span>Rigid numerical cutoffs (e.g. 5.0 mm maximum) can reject clinically valid alignments (e.g. q06 bifurcation ridge). Verification must combine metrics with expert visual checks.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Principle 03</div>
        <b>Physiological Completeness</b>
        <span>Surface overlap (Dice) and boundary distance can conceal catastrophic functional errors (e.g. 50% underestimation of cardiac ejection fraction). Biomechanics require material-level ground truth.</span>
      </div>
    </div>
  </section>
</main>
{footer}
</body>
</html>'''
    (MED_DIR / 'index.html').write_text(content)
    print("Wrote site_med/index.html")

def build_segmentation():
    nav = get_nav_html('segmentation')
    footer = get_footer_html()
    chapter_nav = get_chapter_nav(('index.html', 'Overview'), ('aneurysm.html', 'Domain 2: Aneurysm'))
    head = get_head_html('Domain 1: Organ Segmentation & Tissue Auditing', 'Abdominal CT soft tissue auditing, boundary consistency, and absorbed anatomy')
    
    # Read segmentation assets
    assets_js = (MED_DIR / 'data/segmentation_assets.js').read_text()
    viewer_js = (MED_DIR / 'js/segmentation_viewer.js').read_text()

    content = f'''<!doctype html>
<html lang="en">
{head}
<body>
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Domain 01 · Abdominal CT · 3D Voxel Tensors</span>
    <h1>Organ Segmentation &<br><em>Tissue Ownership Auditing</em></h1>
    <p class="lead">Can an autonomous agent determine which organ a piece of tissue actually belongs to? When 21 mL of pancreatic tissue is mistakenly assigned to the duodenum mask, global organ shapes look plausible. Detecting the error requires inspecting radiodensity inside the mask.</p>
    <p class="hero-meta">TotalSegmentator CT Cohort · Sol/xhigh Controlled Trials · BR-004 / BR-013 / BR-015 / BR-017</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">21.04 mL</span>
        <span class="keyline-label">Transferred pancreatic head tissue</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">13 Organs</span>
        <span class="keyline-label">All named masks present and connected</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">1.2 mm</span>
        <span class="keyline-label">Localization accuracy when focused</span>
      </div>
    </div>
  </header>

  <!-- 01 / Clinical Context & Task Formulation -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / Clinical Intuition & Task Formulation</span>
      <h2>The Head of the Pancreas vs. The Duodenal C-Loop</h2>
      <p>In abdominal computed tomography (CT), adjacent soft-tissue organs share remarkably similar X-ray attenuation. The pancreas head is anatomically cradled inside the C-shaped loop of the duodenum (first part of the small intestine).</p>
    </div>

    <div class="clinical-card">
      <h4>Why This Task Matters in Clinical Medicine</h4>
      <p>When artificial intelligence models segment abdominal CT scans for cancer staging or surgical planning (e.g. the Whipple procedure), an error where pancreatic tissue is merged into the duodenum mask can conceal a pancreatic tumor or miscalculate resection margins. Because both organs remain connected and plausible in shape, automated volume checks fail to catch the error. An AI agent must look <em>inside</em> the mask at voxel densities and parenchymal texture.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Step 01 · Input Scan</div>
        <b>CT Volume + 13 Organ Masks</b>
        <span>Full 3D abdominal CT scan with 13 labeled organ regions (liver, spleen, kidneys, pancreas, duodenum, stomach, aorta, etc.).</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Step 02 · Agent Decision</div>
        <b>Internal Tissue Ownership Audit</b>
        <span>Inspect the interior of each mask: does any mask contain &ge;5 mL of tissue belonging to a neighboring organ?</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Step 03 · Expected Output</div>
        <b>Host Mask + Included Organ + Coordinate</b>
        <span>Name the erroneous mask (duodenum), the absorbed organ (pancreas), and mark a 3D coordinate within 3 mm of the error.</span>
      </div>
    </div>
  </section>

  <!-- 02 / Interactive Visual Explorer -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Interactive Visual Explorer</span>
      <h2>Inspect the Reassigned Pancreatic Tissue</h2>
      <p>Switch between Axial (horizontal) and Coronal (frontal) viewing planes, and toggle between the Original labels, Reassigned error, and Transfer Highlight.</p>
    </div>

    <figure class="image-lab">
      <div class="toggle-row">
        <div class="segmented" role="group" aria-label="CT Viewing Plane">
          <button type="button" data-plane="axial" aria-pressed="true">Axial Plane</button>
          <button type="button" data-plane="coronal" aria-pressed="false">Coronal Plane</button>
        </div>
        <div class="segmented" role="group" aria-label="Label State">
          <button type="button" data-state="before" aria-pressed="false">Original Labels</button>
          <button type="button" data-state="after" aria-pressed="true">Reassigned Error</button>
          <button type="button" data-state="region" aria-pressed="false">Highlight 21 mL Error</button>
        </div>
      </div>
      <img id="comparison" alt="Abdominal CT slice comparison showing pancreas and duodenum">
      <figcaption id="comparison-caption">Loading visual data...</figcaption>
    </figure>
  </section>

  <!-- 03 / Deep Agent Work & Results -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Deep Agent Analysis</span>
      <h2>Broad Search Miss vs. Focused Pair Success</h2>
      <p>Comparing Sol's behavior under a global 13-organ audit versus a focused 2-organ pair inspection on the identical CT scan.</p>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Condition</th>
            <th>Task Scope</th>
            <th>Agent Runtime</th>
            <th>Tokens (In / Out)</th>
            <th>API Cost</th>
            <th>Outcome</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>M02 (Broad Audit)</strong></td>
            <td>All 13 organ masks audited</td>
            <td>6m 44s</td>
            <td>182k / 10,593</td>
            <td>$1.04</td>
            <td><span class="badge badge-miss">Missed</span> · Returned no findings</td>
          </tr>
          <tr>
            <td><strong>F01 (Focused Audit)</strong></td>
            <td>Pancreas + Duodenum only</td>
            <td>5m 51s</td>
            <td>151k / 11,940</td>
            <td>$0.91</td>
            <td><span class="badge badge-pass">Located</span> · Centroid match within 1.2 mm</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="contrast-grid">
      <div class="contrast-card worked">
        <h4><span style="color: var(--color-green);">✔</span> What Worked</h4>
        <ul>
          <li><strong>Autonomous Algorithm Recovery:</strong> When SciPy was unavailable in the container, Sol wrote custom 3D morphological erosion and connected component labeling using pure NumPy.</li>
          <li><strong>Precise 3D Coordinate Placement:</strong> In the focused test, Sol pinpointed the transferred pancreatic tissue at coordinate <code>[-22.9, -199.9, 324.7]</code>, matching the true centroid within 1.2 mm (well inside the 3.0 mm gate).</li>
          <li><strong>Multi-Planar Rendering:</strong> The agent authored its own matplotlib projection scripts to render orthogonal views along the anatomical interface.</li>
        </ul>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">✖</span> What Failed & Caveats</h4>
        <ul>
          <li><strong>Diluted Global Attention:</strong> Auditing 13 masks simultaneously overwhelmed the agent's inspection budget. After checking that overall organ volumes were within expected ranges, it assumed labels were correct.</li>
          <li><strong>Reliance on External Shape:</strong> The transferred 21 mL block preserved smooth, continuous contours for both the pancreas and duodenum. The agent failed to probe internal CT attenuation values until specifically directed.</li>
        </ul>
      </div>
    </div>

    <!-- Trace Code Snippet -->
    <h3>Agent Code Implementation (Trace Extraction)</h3>
    <pre><code># Sol authored custom slice-wise connected component analysis to isolate parenchymal tissue
import numpy as np

def detect_foreign_tissue(ct_array, host_mask, candidate_label):
    # Slice-by-slice HU profile inspection along the organ interface
    pancreas_voxels = (ct_array > 30) & (ct_array < 60)
    overlap = host_mask & pancreas_voxels
    labeled_components = label_connected_components(overlap)
    for comp in labeled_components:
        vol_ml = np.sum(comp) * voxel_vol_ml
        if vol_ml >= 5.0:
            centroid_mm = compute_centroid_lps(comp, affine)
            return {{"object_id": "duodenum", "included_label": "pancreas", "point_lps_mm": centroid_mm}}</code></pre>
  </section>

  <!-- 04 / Task Progression & Evolution -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Task Evolution</span>
      <h2>Progression from Border Tweaks to Tissue Absorption</h2>
      <p>How four successive benchmark iterations refined the organ reasoning challenge:</p>
    </div>

    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-badge">BR-004 · Phase 1</div>
        <div class="timeline-content">
          <h4>Boundary Dilation / Erosion (Kidney & Heart)</h4>
          <p>Planted subtle 63-voxel boundary extensions. Sol missed 3 of 4 cases, but review concluded the defects were too nitpicky and depended on rater subjectivity rather than clear anatomical error.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-013 · Phase 2</div>
        <div class="timeline-content">
          <h4>Unlabeled Organ Identity (11 Masks, 13 Candidates)</h4>
          <p>Presented 11 unlabeled masks without CT context. Both Sol and Terra confused the pancreas with gallbladder due to absence of gall bladder masks in the source scan.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-015 · Phase 3</div>
        <div class="timeline-content">
          <h4>CT Evidence & Vascular Venous Anchors</h4>
          <p>Added raw CT radiodensity (HU) and vascular landmarks (portal vein, vena cava). Sol scored a perfect 11/11, proving that multi-modal image evidence resolves organ naming easily.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-017 · Final</div>
        <div class="timeline-content">
          <h4>Tissue Absorption Audit (Duodenum Swallowing Pancreas)</h4>
          <p>The definitive test: CT is unchanged, both organ labels remain present and connected, but 21 mL of tissue is stolen. Isolates internal tissue ownership from external organ naming.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- 05 / Critical Caveats -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">05 / Takeaways & Evaluation Traps</span>
      <h2>Evaluation Traps in Medical Segmentation</h2>
    </div>

    <div class="caveat-box">
      <strong>The "Plausible Envelope" Trap</strong>
      <p>Standard segmentation metrics (Dice score, Hausdorff distance) evaluate boundary overlap against a reference. When an AI generates smooth, plausible boundaries that erroneously enclose a tumor or neighbor organ, volume and shape checks pass completely. Benchmark design must force agents to audit voxel-level radiometric properties rather than superficial contours.</p>
    </div>

    {chapter_nav}
  </section>
</main>
{footer}
<script>{assets_js}</script>
<script>{viewer_js}</script>
</body>
</html>'''
    (MED_DIR / 'segmentation.html').write_text(content)
    print("Wrote site_med/segmentation.html")

def build_aneurysm():
    nav = get_nav_html('aneurysm')
    footer = get_footer_html()
    chapter_nav = get_chapter_nav(('segmentation.html', 'Domain 1: Segmentation'), ('registration.html', 'Domain 3: Registration'))
    head = get_head_html('Domain 2: Vascular Aneurysm 3D Detection', 'Time-of-flight brain MRA 3D aneurysm search, true detection vs search miss vs web dataset lookup')
    
    figures = (SITE_DIR / 'aneurysm-figures.json').read_text()
    viewer_js = (SITE_DIR / 'aneurysm.js').read_text()

    content = f'''<!doctype html>
<html lang="en">
{head}
<body>
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Domain 02 · Brain TOF-MRA · 3D Vascular Search</span>
    <h1>Vascular Aneurysm<br><em>3D Detection & Spatial Localization</em></h1>
    <p class="lead">Can an autonomous coding agent locate a life-threatening arterial bulge in a 3D brain magnetic resonance angiogram? Across three controlled cases, Sol missed one small lesion, precisely localized another, and queried the public web dataset to answer the third.</p>
    <p class="hero-meta">OpenNeuro ds003949 Cohort (CC0) · Sol/xhigh Controlled Trials · BR-016</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">1 Miss</span>
        <span class="keyline-label">Case N01 · Exhaustive search missed 3.5 mm aneurysm</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">1 Located</span>
        <span class="keyline-label">Case N02 · Coordinate [312, 213, 94] verified in 3 planes</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">1 Assisted</span>
        <span class="keyline-label">Case N03 · Autonomous public dataset hash lookup</span>
      </div>
    </div>
  </header>

  <!-- 01 / Clinical Context -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / Clinical Intuition & Task Formulation</span>
      <h2>Searching for Hidden Bulges in Cerebral Arteries</h2>
      <p>Time-of-Flight Magnetic Resonance Angiography (TOF-MRA) generates high-contrast 3D volumes of blood flowing through the brain's Circle of Willis without ionizing radiation or injected contrast agents.</p>
    </div>

    <div class="clinical-card">
      <h4>Why Early Aneurysm Detection Saves Lives</h4>
      <p>Cerebral aneurysms are localized, balloon-like dilations of arterial walls, frequently measuring only 3 to 7 mm across. If left untreated, an aneurysm can rupture, causing subarachnoid hemorrhage—a catastrophic type of stroke with a 50% mortality rate. Detecting an aneurysm requires scrutinizing hundreds of complex branching vessels across multi-angle projections.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Input Scan</div>
        <b>Full 3D Brain MRA Volume</b>
        <span>High-resolution 3D TOF-MRA array (512 &times; 512 &times; 140 voxels) with voxel spacing ~0.3 &times; 0.3 &times; 0.6 mm.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Agent Decision</div>
        <b>Multi-Planar Volumetric Search</b>
        <span>Filter blood vessels, compute maximum intensity projections (MIPs), rank focal candidate outpouchings, and inspect in 3 orthogonal planes.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Expected Output</div>
        <b>Exact 3D Coordinates [X, Y, Z]</b>
        <span>Return a list of 3D voxel coordinates matching annotated aneurysm regions within a 1.0 mm tolerance, or <code>[]</code> if clear.</span>
      </div>
    </div>
  </section>

  <!-- 02 / Interactive Visual Explorer -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Interactive Visual Explorer</span>
      <h2>Explore the 3D MRA Scans Across Three Planes</h2>
      <p>Switch views between Top (Axial), Front (Coronal), and Side (Sagittal). Toggle guide markers: Yellow Ring = Ground Truth Reference, Pink Diamond = Sol's Submitted Coordinate.</p>
    </div>

    <!-- Case N01 -->
    <div style="margin-bottom: 36px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;">
        <span class="badge badge-miss">Case N01 · Missed</span>
        <h3 style="margin: 0;">Case N01: Small 3.5 mm Aneurysm Overlooked</h3>
      </div>
      <p style="font-size: 14px; color: var(--text-muted);">Sol spent 6m 40s computing Hessian blob detectors and thin slabs. It inspected slices covering the true lesion near [166, 273, 84], but its ranking heuristic prioritized false leads elsewhere and returned <code>[]</code>.</p>
      
      <div class="scan-lab" data-scan="n01">
        <div class="scan-toolbar">
          <div class="scan-plane-buttons" role="group" aria-label="N01 view">
            <button data-plane="2" aria-pressed="false">Top (Axial)</button>
            <button data-plane="1" aria-pressed="true">Front (Coronal)</button>
            <button data-plane="0" aria-pressed="false">Side (Sagittal)</button>
          </div>
          <button data-marks aria-pressed="true">Toggle Markers</button>
        </div>
        <div class="scan-toolbar scan-local" data-local-controls hidden>
          <label>Image <select data-volume><option value="brain">Brain only</option><option value="original">Original scan</option></select></label>
          <label>White level <input data-high type="number" min="1" step="25"></label>
          <label>Zoom <select data-zoom><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option><option value="8">8×</option></select></label>
          <label>Combine slices <select data-slab><option value="0">Single slice</option><option value="3" selected>7 slices</option><option value="5">11 slices</option><option value="10">21 slices</option></select></label>
          <button data-reset>Back to reference</button>
        </div>
        <div class="scan-stage">
          <div class="scan-views"></div>
          <div class="scan-notes">
            <h3>Coronal Close-Up View</h3>
            <div class="scan-legend">
              <span><i class="reference"></i>Ground Truth (Yellow Ring)</span>
            </div>
            <p class="guided-copy">The yellow ring marks the 3.5 mm aneurysm reference location. Each view combines brightest pixels across 7 adjacent slices (48 mm field). Sol reported no findings.</p>
            <p data-coordinates class="scan-coordinates"></p>
          </div>
        </div>
        <p class="scan-status" data-status aria-live="polite">Guided views work offline without additional scan downloads.</p>
      </div>
    </div>

    <!-- Case N02 -->
    <div style="margin-bottom: 36px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;">
        <span class="badge badge-pass">Case N02 · Located</span>
        <h3 style="margin: 0;">Case N02: Confirmed Outpouching in Three Planes</h3>
      </div>
      <p style="font-size: 14px; color: var(--text-muted);">Sol identified a rounded outpouching, verified it across orthogonal slices, ran centroid sweeps across 5 intensity thresholds, and submitted <code>[312, 213, 94]</code>, matching the reference within 1 mm tolerance.</p>
      
      <div class="scan-lab" data-scan="n02">
        <div class="scan-toolbar">
          <div class="scan-plane-buttons" role="group" aria-label="N02 view">
            <button data-plane="2" aria-pressed="false">Top (Axial)</button>
            <button data-plane="1" aria-pressed="true">Front (Coronal)</button>
            <button data-plane="0" aria-pressed="false">Side (Sagittal)</button>
          </div>
          <button data-marks aria-pressed="true">Toggle Markers</button>
        </div>
        <div class="scan-toolbar scan-local" data-local-controls hidden>
          <label>Image <select data-volume><option value="brain">Brain only</option><option value="original">Original scan</option></select></label>
          <label>White level <input data-high type="number" min="1" step="25"></label>
          <label>Zoom <select data-zoom><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option><option value="8">8×</option></select></label>
          <label>Combine slices <select data-slab><option value="0">Single slice</option><option value="3" selected>7 slices</option><option value="5">11 slices</option><option value="10">21 slices</option></select></label>
          <button data-reset>Back to reference</button>
        </div>
        <div class="scan-stage">
          <div class="scan-views"></div>
          <div class="scan-notes">
            <h3>Compare Reference vs. Sol's Point</h3>
            <div class="scan-legend">
              <span><i class="reference"></i>Ground Truth (Yellow Ring)</span>
              <span><i class="answer"></i>Sol's Coordinate (Pink Diamond)</span>
            </div>
            <p class="guided-copy">The pink diamond (Sol's point [312, 213, 94]) lands squarely inside the yellow ground-truth reference ring near [307, 214, 93].</p>
            <p data-coordinates class="scan-coordinates"></p>
          </div>
        </div>
        <p class="scan-status" data-status aria-live="polite">Guided views work offline without additional scan downloads.</p>
      </div>
    </div>

    <!-- Case N03 -->
    <div>
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;">
        <span class="badge badge-amber">Case N03 · Source-Assisted</span>
        <h3 style="margin: 0;">Case N03: Normal Scan Cleared via Open Dataset Lookup</h3>
      </div>
      <p style="font-size: 14px; color: var(--text-muted);">This scan is healthy with no aneurysms. Sol inspected vessel widths, recognized the dataset signature, fetched the public OpenNeuro ds003949 file manifest, verified byte equality, and returned <code>[]</code>.</p>
      
      <div class="scan-lab" data-scan="n03">
        <div class="scan-toolbar">
          <div class="scan-plane-buttons" role="group" aria-label="N03 view">
            <button data-plane="2" aria-pressed="false">Top (Axial)</button>
            <button data-plane="1" aria-pressed="true">Front (Coronal)</button>
            <button data-plane="0" aria-pressed="false">Side (Sagittal)</button>
          </div>
          <button data-marks aria-pressed="true" hidden>Toggle Markers</button>
        </div>
        <div class="scan-toolbar scan-local" data-local-controls hidden>
          <label>Image <select data-volume><option value="brain">Brain only</option><option value="original">Original scan</option></select></label>
          <label>White level <input data-high type="number" min="1" step="25"></label>
          <label>Zoom <select data-zoom><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option><option value="8">8×</option></select></label>
          <label>Combine slices <select data-slab><option value="0">Single slice</option><option value="3" selected>7 slices</option><option value="5">11 slices</option><option value="10">21 slices</option></select></label>
          <button data-reset>Reset view</button>
        </div>
        <div class="scan-stage">
          <div class="scan-views"></div>
          <div class="scan-notes">
            <h3>Full Normal Vascular Tree</h3>
            <p class="guided-copy">An unmodified normal TOF-MRA. Sol's automated script confirmed that no aneurysm was annotated in the public source release.</p>
            <p data-coordinates class="scan-coordinates"></p>
          </div>
        </div>
        <p class="scan-status" data-status aria-live="polite">Guided views work offline without additional scan downloads.</p>
      </div>
    </div>
  </section>

  <!-- 03 / Deep Agent Work & Results -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Deep Agent Analysis</span>
      <h2>Code Execution Traces & Search Heuristics</h2>
      <p>How the agent orchestrated code, mathematical filters, and internet access during the 30-minute reasoning budget.</p>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Case ID</th>
            <th>Ground Truth</th>
            <th>Submitted Coordinate</th>
            <th>Runtime</th>
            <th>Output Tokens</th>
            <th>Estimated Cost</th>
            <th>Result Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>N01</strong></td>
            <td>Positive (~3.5 mm)</td>
            <td><code>[]</code> (Empty)</td>
            <td>6m 40s</td>
            <td>9,908</td>
            <td>$1.04</td>
            <td><span class="badge badge-miss">Search Miss</span></td>
          </tr>
          <tr>
            <td><strong>N02</strong></td>
            <td>Positive (~4.0 mm)</td>
            <td><code>[[312, 213, 94]]</code></td>
            <td>5m 46s</td>
            <td>8,763</td>
            <td>$0.98</td>
            <td><span class="badge badge-pass">Exact Pass</span></td>
          </tr>
          <tr>
            <td><strong>N03</strong></td>
            <td>Negative (No lesion)</td>
            <td><code>[]</code> (Empty)</td>
            <td>7m 32s</td>
            <td>13,806</td>
            <td>$1.56</td>
            <td><span class="badge badge-amber">Dataset-Assisted Pass</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="contrast-grid">
      <div class="contrast-card worked">
        <h4><span style="color: var(--color-green);">✔</span> Successful Strategies</h4>
        <ul>
          <li><strong>Multi-Plane Orthogonal Verification:</strong> In N02, Sol refused to trust 2D projections alone. It cut native coronal, sagittal, and axial slices through the candidate voxel before accepting it.</li>
          <li><strong>Threshold Sweep for Sub-Voxel Centroids:</strong> Rather than taking a crude pixel peak, Sol swept thresholds from 350 to 750 HU to compute stable intensity centroids.</li>
          <li><strong>Autonomous Tool Authoring:</strong> Sol wrote <code>montage_mra.py</code> and <code>oblique_mra.py</code> to inspect slab Maximum Intensity Projections along arbitrary angles.</li>
        </ul>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">✖</span> Pitfalls & Failure Modes</h4>
        <ul>
          <li><strong>Heuristic Ranking False Leads:</strong> In N01, the true 3.5 mm aneurysm appeared in generated images, but Sol's Hessian blob scoring ranked normal vascular tortuosities higher, abandoning the true lesion.</li>
          <li><strong>Autonomous Web Retrieval Leakage:</strong> In N03, allowing the agent bash/web access enabled it to query the public OpenNeuro dataset tree, download the ground-truth metadata, and verify byte matches.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- 04 / Critical Caveats -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Critical Insights</span>
      <h2>Visual Perception vs. Autonomous Information Retrieval</h2>
    </div>

    <div class="caveat-box">
      <strong>The Dataset Leakage Dilemma in the Agent Era</strong>
      <p>Unlike traditional vision models, coding agents possess bash execution and curl/python networking. In Case N03, Sol's correct answer was not derived from visual interpretation—it was an automated forensic lookup of the public dataset's annotation file. In benchmark design, network sandboxing or strictly withheld proprietary clinical data is essential to measure true perceptual reasoning.</p>
    </div>

    {chapter_nav}
  </section>
</main>
{footer}
<script id="scan-data" type="application/json">{figures}</script>
<script id="local-scans" type="application/json">null</script>
<script>{viewer_js}</script>
</body>
</html>'''
    (MED_DIR / 'aneurysm.html').write_text(content)
    print("Wrote site_med/aneurysm.html")

def build_registration():
    nav = get_nav_html('registration')
    footer = get_footer_html()
    chapter_nav = get_chapter_nav(('aneurysm.html', 'Domain 2: Aneurysm'), ('vessels.html', 'Domain 4: Vessels & CPR'))
    head = get_head_html('Domain 3: Deformable 3D Image Registration', 'Lung CT respiratory motion alignment, 2D slice to 3D volume failure, and landmark q06 adjudication')
    
    figures = (SITE_DIR / 'registration-figures.json').read_text()
    viewer_js = (SITE_DIR / 'registration.js').read_text()

    content = f'''<!doctype html>
<html lang="en">
{head}
<body class="registration">
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Domain 03 · 4D Lung CT · Non-Rigid Alignment</span>
    <h1>Deformable 3D Image Registration<br><em>& Respiratory Motion Tracking</em></h1>
    <p class="lead">How does an agent map anatomical landmarks across breathing phases? Adding full 3D source depth rescued two catastrophic landmark errors, reducing RMS error from 12.73 mm to 2.60 mm—while the remaining worst-case error became a classic study in visual vs. numerical adjudication.</p>
    <p class="hero-meta">Learn2Reg LungCT Challenge · Sol/xhigh Controlled Trials · BR-019–BR-024 / BR-028</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">12.7 → 2.6 mm</span>
        <span class="keyline-label">RMS error drop when adding 3D source depth</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">32.2 → 6.4 mm</span>
        <span class="keyline-label">Maximum distance reduction on hardest landmark</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">Visual Pass</span>
        <span class="keyline-label">Landmark q06 approved by visual expert review</span>
      </div>
    </div>
  </header>

  <!-- 01 / Clinical Context -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / Clinical Intuition & Task Formulation</span>
      <h2>Aligning Deforming Lungs for Radiation Therapy</h2>
      <p>During normal respiration, lung tissue expands and contracts non-rigidly. The diaphragm moves by several centimeters, pulling bronchi and pulmonary blood vessels along complex non-linear trajectories.</p>
    </div>

    <div class="clinical-card">
      <h4>Why Accurate Lung Registration is Crucial</h4>
      <p>In stereotactic body radiation therapy (SBRT) for lung cancer, clinicians deliver high-dose radiation to a moving tumor while sparing surrounding healthy alveoli and cardiac tissue. Because scans are captured at different breathing phases (full exhale vs full inhale), algorithms must deformably register the exhale scan onto the inhale target. A misalignment of 10–30 mm could irradiate healthy lung or miss the tumor core.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Input Scans</div>
        <b>Source Exhale CT + Target Inhale CT</b>
        <span>Full 3D CT volume at maximum exhalation, full 3D CT volume at maximum inhalation, and 8 anatomical query landmark coordinates in the source.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Agent Decision</div>
        <b>Deformable Volumetric Alignment</b>
        <span>Compute 3D displacement fields and multi-scale patch cross-correlations to track anatomical landmarks through respiratory motion.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Expected Output</div>
        <b>8 Target Landmark Coordinates</b>
        <span>Return the predicted 3D physical coordinates in the inhale volume, evaluated against expert manual annotations with a 5.0 mm maximum tolerance.</span>
      </div>
    </div>
  </section>

  <!-- 02 / Interactive Visual Explorer -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Interactive Visual Explorer</span>
      <h2>Compare 2D Source vs. Full 3D Source Registration</h2>
      <p>Select landmark queries (q01–q08) and viewing planes. Notice how full 3D source depth eliminates large misalignments in q02 and q04, while q06 sits precisely on the target bifurcation.</p>
    </div>

    <div class="scan-lab">
      <div class="scan-toolbar">
        <label>Review Plane <select id="reg-plane" aria-label="Registration review plane"></select></label>
        <div id="reg-queries" class="scan-plane-buttons" role="group" aria-label="Landmark Selection"></div>
      </div>
      <div class="reg-panels">
        <figure>
          <figcaption>Source Exhale (Query Point)</figcaption>
          <img id="reg-source" alt="Source CT centered on query landmark">
        </figure>
        <figure>
          <figcaption>Target Inhale (Ground Truth)</figcaption>
          <img id="reg-manual" alt="Target Inhale CT centered on manual reference">
        </figure>
        <figure>
          <figcaption>Sol: 2D Source Only (BR-024)</figcaption>
          <img id="reg-old" alt="Target CT centered on original 2D-source Sol estimate">
          <p id="reg-old-error" class="reg-error"></p>
        </figure>
        <figure>
          <figcaption>Sol: Full 3D Source (BR-028)</figcaption>
          <img id="reg-new" alt="Target CT centered on full 3D-source Sol estimate">
          <p id="reg-new-error" class="reg-error"></p>
        </figure>
      </div>
      <p class="scan-status" id="reg-status" aria-live="polite"></p>
      <p class="scan-status" id="reg-context"></p>
    </div>

    <div class="reg-adjudication">
      <strong>User Adjudication Verdict on Landmark q06: Visually Accepted</strong>
      <p>Under frozen automated benchmark gates, Landmark q06 scored a distance error of 6.41 mm, narrowly exceeding the 5.0 mm tolerance threshold. However, clinical visual adjudication revealed that both the manual ground truth marker and Sol's estimate sit squarely on the identical anatomical bronchial bifurcation ridge. The 6.41 mm offset reflects spatial ambiguity along the ridge line rather than a biological misidentification.</p>
    </div>
  </section>

  <!-- 03 / Deep Agent Work & Results -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Deep Agent Analysis</span>
      <h2>Why 3D Depth Rescued the Registration Strategy</h2>
      <p>Analyzing how information completeness altered the agent's algorithmic approach.</p>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Experimental Condition</th>
            <th>Source Input</th>
            <th>Target Input</th>
            <th>RMS Error</th>
            <th>Max Error (Worst Point)</th>
            <th>Benchmark Outcome</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>BR-024</strong> (Sol / xhigh)</td>
            <td>Single 2D Oblique Slice</td>
            <td>Full 3D Volume</td>
            <td>12.73 mm</td>
            <td>32.20 mm (q04 trapped)</td>
            <td><span class="badge badge-miss">Failed</span> · Severe Misalignment</td>
          </tr>
          <tr>
            <td><strong>BR-028</strong> (Sol / xhigh)</td>
            <td>Full 3D Exhale Volume</td>
            <td>Full 3D Volume</td>
            <td>2.60 mm</td>
            <td>6.41 mm (q06 bifurcation)</td>
            <td><span class="badge badge-pass">Visually Accepted</span> (7/8 &le; 2.2 mm)</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="contrast-grid">
      <div class="contrast-card worked">
        <h4><span style="color: var(--color-green);">✔</span> How 3D Source Depth Transformed Strategy</h4>
        <ul>
          <li><strong>Abandoning Trapped Global Fields:</strong> In BR-024, Sol tried to deform a 2D slab using global B-splines. The optimizer got trapped in a local minimum, placing q04 32.5 mm away. In BR-028, Sol discarded conflicting global fields and ran direct 3D patch cross-correlations around nominal coordinates.</li>
          <li><strong>Multi-Scale Patch Correlation:</strong> Sol tested patch sizes across multiple scales. Its coarse search ranked the correct q02 and q04 neighborhoods first across all patch sizes (within 2.15–2.44 mm of truth) before local refinement.</li>
          <li><strong>Out-of-Plane Branch Context:</strong> True 3D depth exposed bronchial bifurcation branches above and below the query plane, eliminating the rotational ambiguity that doomed 2D matching.</li>
        </ul>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">✖</span> Remaining Failure Modes</h4>
        <ul>
          <li><strong>Ridge-Line Ambiguity (q06):</strong> Along elongated tubular structures and vessel ridges, normalized cross-correlation has shallow gradient peaks along the vessel axis, leading to millimeter sliding offsets.</li>
          <li><strong>Automated Gate Rigidity:</strong> The automated grader penalizes any point exceeding 5.0 mm, even when the point lands on biologically identical anatomy.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- 04 / Task Evolution Timeline -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Task Progression</span>
      <h2>Evolution Across Five Registration Rounds</h2>
      <p>How the registration challenge developed from toy affine alignments to realistic non-rigid respiratory deformation:</p>
    </div>

    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-badge">BR-019 · Phase 1</div>
        <div class="timeline-content">
          <h4>Same CT Rigid / Affine Recovery</h4>
          <p>Agent recovered an oblique slice pose from the exact same scan. Terra passed with 0.0005 mm error, proving numerical inversion works on identical resampled textures but does not test anatomical understanding.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-020 · Phase 2</div>
        <div class="timeline-content">
          <h4>Reconstruction Kernel Variations</h4>
          <p>Tested registration across sharp vs smooth CT reconstruction kernels from the same patient. Terra passed with 0.036 mm RMS error using multi-scale intensity correlation.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-021–022 · Phase 3</div>
        <div class="timeline-content">
          <h4>Real Respiratory Deformation & Transform Bugs</h4>
          <p>Introduced genuine inhale-exhale patient breathing. Paired 3D passed (1.91 mm RMS), but 2D-to-3D failed (12.64 mm RMS) due to a coordinate transform composition bug and search space truncation.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-024 / 028 · Final</div>
        <div class="timeline-content">
          <h4>Challenging Patient & 3D Depth Controlled Contrast</h4>
          <p>Tested on a difficult respiratory patient. Supplying full 3D source depth reduced RMS error from 12.73 mm to 2.60 mm. Landmark q06 was visually accepted by expert review, retiring the task.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- 05 / Critical Caveats -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">05 / Takeaways & Clinical Reality</span>
      <h2>Numerical Metric Traps vs. Biological Plausibility</h2>
    </div>

    <div class="caveat-box">
      <strong>The Rigid Point Metric Fallacy in Medical Registration</strong>
      <p>Standard registration benchmarks grade algorithms using Target Registration Error (TRE) on discrete annotated landmarks. However, manual ground-truth points themselves carry inter-observer variability of 1.5–3.5 mm on fuzzy vessel bifurcations. Discarding an algorithm because a point was 6.4 mm away rather than 5.0 mm—when both points lie on the exact same anatomical structure—highlights the necessity of combining quantitative metrics with qualitative radiological review.</p>
    </div>

    {chapter_nav}
  </section>
</main>
{footer}
<script id="registration-data" type="application/json">{figures}</script>
<script>{viewer_js}</script>
</body>
</html>'''
    (MED_DIR / 'registration.html').write_text(content)
    print("Wrote site_med/registration.html")

def build_vessels():
    nav = get_nav_html('vessels')
    footer = get_footer_html()
    chapter_nav = get_chapter_nav(('registration.html', 'Domain 3: Registration'), ('cardiac.html', 'Domain 5: Cardiac'))
    head = get_head_html('Domain 4: Tubular Geometry, Airway Routing & CPR', 'Vessel and airway repair, 360-degree curved planar reformations, and metric evaluation flaws')
    
    figures = (SITE_DIR / 'vessel-figures.json').read_text()
    viewer_js = (SITE_DIR / 'vessels.js').read_text()

    content = f'''<!doctype html>
<html lang="en">
{head}
<body class="vessels">
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Domain 04 · Coronary CTA, MRA & Chest CT</span>
    <h1>Tubular Network Geometry<br><em>& Curved Planar Reformations (CPR)</em></h1>
    <p class="lead">Blood vessels and bronchial airways are complex branching trees that frequently break in automated segmentations. Autonomous agents can repair gaps, extract centerlines, and generate 360° curved reformations—yet subtle metadata indexing bugs and evaluation loopholes reveal how easily algorithms can be misjudged.</p>
    <p class="hero-meta">TopBrain MRA, ImageCAS Coronary CTA & AeroPath Airway CT · Terra/high Trials · BR-025 / BR-026 / BR-030 / BR-033</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">360° CPR</span>
        <span class="keyline-label">Full rotatable curved planar reformations generated</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">8.89 mm Trap</span>
        <span class="keyline-label">Coronary distance-axis bug caused false failure</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">Scope Loophole</span>
        <span class="keyline-label">Airway benchmark passed while main tree was broken</span>
      </div>
    </div>
  </header>

  <!-- 01 / Clinical Context -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / Clinical Intuition & Task Formulation</span>
      <h2>Unrolling 3D Curved Vessels into 2D Radiographic Views</h2>
      <p>Blood vessels (coronary arteries, cerebral Circle of Willis) and bronchial airways travel in winding, tortuous paths through 3D space. Standard 2D axial slices cut across them obliquely, making it impossible to assess lumen diameter along the vessel length.</p>
    </div>

    <div class="clinical-card">
      <h4>What is a Curved Planar Reformation (CPR)?</h4>
      <p>A Curved Planar Reformation (CPR) takes the 3D centerline curve of a blood vessel and "unrolls" the surrounding volumetric image into a continuous flat ribbon. By rotating the cutting plane 360° around the centerline axis, radiologists can inspect the vessel wall from all sides to detect stenosis (narrowing), soft plaque, and calcification. Generating a CPR requires exact spatial coordinate tracking: the sampled pixels, physical arc distance, and 3D orientation must remain perfectly synchronized.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Input Scans</div>
        <b>3D Volume + Broken Mask + Anchors</b>
        <span>High-resolution angiogram/CT, a predicted vessel mask containing a disconnection gap, and proximal/distal anchor points.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Agent Decision</div>
        <b>Geodesic Repair & Centerline Extraction</b>
        <span>Bridge the gap using intensity-guided shortest paths, extract an ordered 3D centerline, and sample perpendicular cross-sections.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Expected Output</div>
        <b>Repaired Mask + 3D Mesh + Rotated CPRs</b>
        <span>Export the corrected segmentation, a watertight surface mesh, and 8 rotated CPR images with verified physical distance axes.</span>
      </div>
    </div>
  </section>

  <!-- 02 / Interactive Visual Explorer -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Interactive Visual Explorer</span>
      <h2>Rotate the 3D Brain MRA Curved Reformation</h2>
      <p>Use the rotation slider to revolve the CPR view around the vessel centerline (0° to 315° in 45° steps). Scrub along the route to inspect perpendicular 10 &times; 10 mm vessel cross-sections and highlight the repaired 2-voxel gap.</p>
    </div>

    <fieldset id="vessel-controls" disabled>
      <legend>Interactive Brain CPR Rotator & Lumen Cross-Section</legend>
      <div class="controls">
        <label>Rotation Angle <input id="cpr-angle" type="range" min="0" max="7" value="0" step="1"><output id="cpr-angle-value" for="cpr-angle">0°</output></label>
        <label>Overlay Mode <select id="cpr-overlay"><option value="none">MRA Intensity Only</option><option value="before">Original Broken Mask</option><option value="after">Repaired Mask</option><option value="changes" selected>Repaired Gap Highlighted</option></select></label>
        <label>Route Distance <input id="route-position" type="range" min="0" step="1" value="0"><output id="route-distance" for="route-position"></output></label>
        <button id="jump-gap" type="button" class="chapter-btn" style="padding: 6px 12px; font-size: 12px;">Jump to Repaired Gap</button>
      </div>
      
      <div class="cpr-panels">
        <figure>
          <canvas id="vessel-cpr" role="img" aria-label="Curved Planar Reformation of Basilar to Right Superior Cerebellar Artery"></canvas>
          <figcaption>Curved Planar Reformation (Basilar &rarr; Right SCA). Gold line = current cross-section location. Orange = original mask; Green = repaired; Pink = bridge voxels.</figcaption>
        </figure>
        <figure>
          <canvas id="vessel-section" role="img" aria-label="Perpendicular Cross-Section of Lumen"></canvas>
          <figcaption>Perpendicular 10 &times; 10 mm lumen cross-section at selected route distance.</figcaption>
        </figure>
      </div>
    </fieldset>
    <p id="vessel-load-status" class="small" aria-live="polite">Loading embedded CPR visual data...</p>

    <figure style="margin-top: 24px;">
      <a id="brain-enlarge"><img id="brain-figure" alt="Brain MRA calibration overview: disconnected input, two added voxels, CPR, and connected surface."></a>
      <figcaption>Brain MRA calibration overview: disconnected input, two added bridge voxels, CPR sampling, and the connected basilar-to-right-SCA surface route.</figcaption>
    </figure>

    <!-- Airway Review Panel -->
    <h3 style="margin-top: 36px;">Airway Tree Repair & The Evaluation Flaw</h3>
    <p style="font-size: 14px; color: var(--text-muted);">Comparing AeroPath CT airway repairs: A01 contains a real repair connecting back to the main bronchus. A02 and A03 contain no edits and still show obvious disconnections from the trachea, yet received passing scores under the frozen benchmark!</p>
    <figure>
      <a id="airway-enlarge"><img id="airway-figure" alt="Airway repair before and after, showing detached parent gaps"></a>
      <figcaption>AeroPath chest CT airway segmentation panels. A01 connects back to the parent tree; A02 and A03 remain visibly disconnected from the central airway despite passing automated tests.</figcaption>
    </figure>
  </section>

  <!-- 03 / Deep Agent Work & Results -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Deep Agent Analysis</span>
      <h2>Code Capabilities & Two Critical Evaluation Traps</h2>
      <p>Examining agent pipeline mastery alongside two critical benchmark flaws uncovered during research.</p>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Study</th>
            <th>Target Anatomy</th>
            <th>Observed Result</th>
            <th>Clinical & Benchmark Interpretation</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>BR-026</strong> (Terra / high)</td>
            <td>MRA Circle of Willis (Synthetic Gap)</td>
            <td>198 of 200 voxels restored</td>
            <td><span class="badge badge-pass">Gap Repaired</span>; preservation test failed due to 244 additions beside L-ACA.</td>
          </tr>
          <tr>
            <td><strong>BR-030</strong> (Terra / high)</td>
            <td>Coronary CTA (ImageCAS RCA Gap)</td>
            <td>Repair & 3D mesh passed; CPR failed</td>
            <td><span class="badge badge-miss">Metadata Trap</span>: CPR distance axis was 8.89 mm too long (used voxel count instead of mm).</td>
          </tr>
          <tr>
            <td><strong>BR-033</strong> (Terra / high)</td>
            <td>Airway CT (AeroPath Tree Routing)</td>
            <td>Route & CPR passed; A01 +578 voxels</td>
            <td><span class="badge badge-amber">Evaluation Loophole</span>: Tests checked paths inside fragments; parent gaps remained severed.</td>
          </tr>
          <tr>
            <td><strong>BR-033</strong> (Author Screen)</td>
            <td>TopBrain Full Brain MRA</td>
            <td>2-voxel bridge restored R-SCA</td>
            <td>Demonstrated clean 85.6 mm parent-to-target route, rotated CPR, and watertight mesh export.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- The Two Traps in Detail -->
    <div class="contrast-grid">
      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">Trap 1</span> The CPR Distance-Axis Bug (Coronary CTA)</h4>
        <p style="font-size: 14px; margin-bottom: 8px;">In BR-030, Terra repaired a 5 mm gap in the Right Coronary Artery with 94.5% Dice and 0.50 mm centerline accuracy. The CPR correctly sampled 3D voxel intensities along the entire artery.</p>
        <p style="font-size: 14px; margin-bottom: 12px;"><strong>The Catch:</strong> When saving the CPR metadata array, the agent stored cumulative distances derived from the raw voxel skeleton rather than the resampled physical millimeter spline curve. The saved distance axis read 184.81 mm instead of 175.92 mm—an 8.89 mm overstatement!</p>
        <div class="axis-comparison" style="margin: 0; padding: 14px;">
          <p style="margin: 0 0 4px; font-size: 12px;"><b>Saved CPR Distance Axis · 184.809 mm (Failed)</b></p>
          <div class="axis-bar"></div>
          <p style="margin: 0 0 4px; font-size: 12px;"><b>Actual Physical Centerline · 175.918 mm (Correct)</b></p>
          <div class="axis-bar corrected"></div>
        </div>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-amber);">Trap 2</span> The Airway Scope Loophole (Chest CT)</h4>
        <p style="font-size: 14px; margin-bottom: 8px;">In BR-033, Terra scored 100% pass on all requested route and CPR tests across three airway cases (A01, A02, A03).</p>
        <p style="font-size: 14px; margin-bottom: 8px;"><strong>The Catch:</strong> In cases A02 and A03, the benchmark anchor points both happened to be located <em>inside the same detached airway fragment</em>! The agent correctly found a path between the anchors, but the fragment was completely severed from the main trachea.</p>
        <p style="font-size: 14px; margin-bottom: 0;">User visual review caught this immediately: <em>"The disconnection is obvious."</em> The passing automated test had tested local fragment connectivity rather than whole-tree anatomical integrity.</p>
      </div>
    </div>
  </section>

  <!-- 04 / Task Evolution Timeline -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Task Progression</span>
      <h2>Evolution Across Vessel and Airway Rounds</h2>
    </div>

    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-badge">BR-025 / 026 · Phase 1</div>
        <div class="timeline-content">
          <h4>Circle of Willis Synthetic Gap Repair</h4>
          <p>Four public TopCoW MRA scans. Terra restored 198 of 200 deleted voxels. However, an unchanged control added 244 voxels near L-ACA, highlighting disputes over anatomical variant vs synthetic defect.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-030 · Phase 2</div>
        <div class="timeline-content">
          <h4>Real Coronary RCA Prediction Errors</h4>
          <p>Admitted a real CAS-Net segmentation gap on ImageCAS-X case 1. Terra completed the entire repair, centerline, and mesh workflow, but was caught by the 8.89 mm distance-axis metadata error.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-033 · Final</div>
        <div class="timeline-content">
          <h4>Airway Scope Audit & TopBrain Resumption</h4>
          <p>Airway user review corrected the fragment-anchor flaw. TopBrain resumption screened five full MRA predictions, verifying clean 2-voxel bridging, 85.6 mm centerline routing, and rotatable CPRs.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- 05 / Critical Caveats -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">05 / Takeaways & Clinical Reality</span>
      <h2>The Peril of Synthetic Test Anchors</h2>
    </div>

    <div class="caveat-box">
      <strong>Engineering Pipeline Success Does Not Equal Anatomical Difficulty</strong>
      <p>Agents easily master complex computational geometry pipelines: Dijkstra routing, skeletonization, trilinear intensity sampling, and marching cubes surface generation. However, if the benchmark's grading anchors are narrowly scoped (such as testing paths within already-disconnected fragments), automated tests will report green passes while the clinical deliverable remains unviable.</p>
    </div>

    {chapter_nav}
  </section>
</main>
{footer}
<script id="vessel-data" type="application/json">{figures}</script>
<script>{viewer_js}</script>
</body>
</html>'''
    (MED_DIR / 'vessels.html').write_text(content)
    print("Wrote site_med/vessels.html")

def build_cardiac():
    nav = get_nav_html('cardiac')
    footer = get_footer_html()
    chapter_nav = get_chapter_nav(('vessels.html', 'Domain 4: Vessels & CPR'), ('landmarks.html', 'Domain 6: Landmarks'))
    head = get_head_html('Domain 5: 4D Beating Heart Biomechanics', 'Dynamic 4D heart modeling, moving tetrahedral meshes, myocardial strain tensors, and Ejection Fraction underestimation')
    
    figures = (SITE_DIR / 'cardiac-figures.json').read_text()
    viewer_js = (SITE_DIR / 'cardiac.js').read_text()

    content = f'''<!doctype html>
<html lang="en">
{head}
<body>
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Domain 05 · 4D Ultrasound & Cine-MRI · Biomechanics</span>
    <h1>4D Beating Heart Biomechanics<br><em>& Dynamic Strain Modeling</em></h1>
    <p class="lead">Autonomous agents can build moving 3D heart meshes and compute mathematical strain tensors. But does the mesh deformation follow true myocardial tissue—and can the model preserve clinically vital contraction? Separating surface shape agreement from physiological pump function.</p>
    <p class="hero-meta">STRAUS Synthetic Mechanics & EchoXFlow Clinical Cohort · Sol/xhigh Controlled Trials · BR-025–BR-035</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">Dice 0.946</span>
        <span class="keyline-label">High moving-mesh shape agreement with masks</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">7.37 pp Error</span>
        <span class="keyline-label">Radial strain missed research target (&le;5 pp)</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">23–30 pp EF Drop</span>
        <span class="keyline-label">Clinical tracking severely underestimated contraction</span>
      </div>
    </div>
  </header>

  <!-- 01 / Clinical Context -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / Clinical Intuition & Task Formulation</span>
      <h2>Pumping Efficiency (EF) vs. Muscle Deformation (Strain)</h2>
      <p>The human heart is an electro-mechanical pump. With every beat, the left ventricle twists, shortens, and thickens to eject oxygenated blood into the aorta.</p>
    </div>

    <div class="clinical-card">
      <h4>Why Ejection Fraction and Strain Tell Different Stories</h4>
      <p><strong>Ejection Fraction (EF)</strong> measures the percentage of blood volume ejected during systole (normal &ge;50%). However, EF is a coarse global measure. In early heart failure, hypertension, or ischemia, global EF may remain normal while local heart muscle fibers become stiff or dysfunctional. <strong>Myocardial Strain</strong> measures the percentage shortening and thickening of the heart wall along three directional axes: Longitudinal (base-to-apex shortening), Circumferential (circular squeezing), and Radial (wall thickening). Measuring true strain requires tracking tissue points, not just cavity borders.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Input Scans</div>
        <b>4D Cine-MRI / Ultrasound Volumes</b>
        <span>Full-cycle 3D ultrasound or cine-MRI volumes across 30 cardiac phases, with or without full-cycle myocardial wall masks.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Agent Decision</div>
        <b>Dynamic Mesh & Tensor Mechanics</b>
        <span>Construct a 4D tetrahedral mesh, track tissue material points through time, and compute Green-Lagrange finite strain tensors.</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Expected Output</div>
        <b>Ejection Fraction & Regional Strain</b>
        <span>Output clinical Ejection Fraction (EF) and 16-segment regional engineering strain curves evaluated against biomechanical ground truth.</span>
      </div>
    </div>
  </section>

  <!-- 02 / Interactive Visual Explorer -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Interactive Visual Explorer</span>
      <h2>Explore 16-Segment Regional Myocardial Strain Curves</h2>
      <p>Select any of the 16 standard American Heart Association (AHA) ventricular regions and switch between Longitudinal, Circumferential, and Radial strain directions across the 30 cardiac cycle phases.</p>
    </div>

    <div class="viewer-card" style="padding: 24px;">
      <div class="cardiac-controls">
        <label for="cardiac-region">Ventricular Segment <select id="cardiac-region"></select></label>
        <label for="cardiac-direction">Strain Direction <select id="cardiac-direction">
          <option value="0">Longitudinal Strain (Shortening)</option>
          <option value="1">Circumferential Strain (Squeezing)</option>
          <option value="2" selected>Radial Strain (Wall Thickening)</option>
        </select></label>
      </div>

      <div class="cardiac-key">
        <span class="cardiac-reference">Ground Truth Simulator Reference</span>
        <span class="cardiac-masks">Sol Reconstructed (Masks Alone)</span>
        <span class="cardiac-images">Sol Reconstructed (Masks + Ultrasound)</span>
      </div>

      <svg id="cardiac-curve" class="cardiac-chart" viewBox="0 0 700 315" role="img" aria-label="Regional engineering strain through the cardiac cycle"></svg>
      <p id="cardiac-status" class="small" aria-live="polite" style="font-weight: 600; color: var(--color-teal);"></p>
      <p class="small">Volume-weighted engineering strain in anatomical directions. Notice how longitudinal and circumferential curves track well, while radial strain overshoots true tissue deformation.</p>

      <!-- Retained Scientific Plot -->
      <h3 style="margin-top: 32px;">Retained Scientific Comparison Plot</h3>
      <figure>
        <a id="cardiac-figure-link"><img id="cardiac-figure" class="cardiac-figure" alt="BR-035 comparison of tissue volumes, clinical cavity volumes and directional strain errors"></a>
        <figcaption>Multi-panel plot comparing reconstructed tissue volume, cavity volume, and directional strain error distributions across phases.</figcaption>
      </figure>
    </div>
  </section>

  <!-- 03 / Deep Agent Work & Results -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Deep Agent Analysis</span>
      <h2>Two Major Mechanical & Clinical Findings</h2>
      <p>Investigating the discrepancy between shape agreement and internal strain, and the severe underestimation of ejection fraction in clinical tracking.</p>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Metric / Clinical Indicator</th>
            <th>Ground Truth Target</th>
            <th>Sol (Masks Alone)</th>
            <th>Sol (Masks + Ultrasound)</th>
            <th>Benchmark Outcome</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Mean Mask Overlap (Dice)</strong></td>
            <td>&ge; 0.90</td>
            <td>0.946</td>
            <td>0.933</td>
            <td><span class="badge badge-pass">Pass</span></td>
          </tr>
          <tr>
            <td><strong>Tissue-Motion RMSE</strong></td>
            <td>&le; 2.0 mm</td>
            <td>1.61 mm</td>
            <td>1.72 mm</td>
            <td><span class="badge badge-pass">Pass</span></td>
          </tr>
          <tr>
            <td><strong>Longitudinal Strain Error</strong></td>
            <td>&le; 5.0 pp</td>
            <td>2.87 pp</td>
            <td>2.90 pp</td>
            <td><span class="badge badge-pass">Pass</span></td>
          </tr>
          <tr>
            <td><strong>Circumferential Strain Error</strong></td>
            <td>&le; 5.0 pp</td>
            <td>3.51 pp</td>
            <td>3.22 pp</td>
            <td><span class="badge badge-pass">Pass</span></td>
          </tr>
          <tr>
            <td><strong>Radial Strain Error</strong></td>
            <td>&le; 5.0 pp</td>
            <td>7.37 pp</td>
            <td>5.45 pp</td>
            <td><span class="badge badge-miss">Failed Target</span></td>
          </tr>
          <tr>
            <td><strong>Inverted Tetrahedra Elements</strong></td>
            <td>0</td>
            <td>0</td>
            <td>0</td>
            <td><span class="badge badge-pass">Pass</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="contrast-grid">
      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">Finding 1</span> The Surface vs. Material Strain Paradox</h4>
        <p style="font-size: 14px; margin-bottom: 8px;">In BR-035, Sol constructed moving tetrahedral meshes with excellent boundary overlap (Dice 0.946) and accurate finite-strain tensor calculations. Longitudinal and circumferential strain passed research gates.</p>
        <p style="font-size: 14px; margin-bottom: 8px;"><strong>The Catch:</strong> Local radial strain failed (7.37 pp error on masks alone, 5.45 pp error with ultrasound).</p>
        <p style="font-size: 14px; margin-bottom: 0;"><strong>The Cylinder Twist Proof:</strong> An analytic cylinder can twist vigorously around its axis while keeping its outer boundary completely stationary. Therefore, <em>even complete 3D segmentations at every phase cannot uniquely determine internal material motion</em>. Matching the cavity surface does not guarantee true biophysical strain.</p>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">Finding 2</span> Clinical EF Underestimation (EchoXFlow)</h4>
        <p style="font-size: 14px; margin-bottom: 8px;">In BR-034, Sol was given real clinical echocardiograms with an initial cavity surface and asked to track ventricular volume through time to compute clinical Ejection Fraction (EF).</p>
        <p style="font-size: 14px; margin-bottom: 8px;"><strong>The Catch:</strong> The agent built a smooth, image-driven deformable tracker that stayed close to the wall (&lt;3 mm surface distance). But it severely under-contracted during peak systole:</p>
        <ul style="margin-bottom: 0;">
          <li>Primary Case: Reference EF 45.3% &rarr; Tracked EF 22.0% (23.3 pp error)</li>
          <li>Hidden Case: Reference EF 47.6% &rarr; Tracked EF 21.7% (25.9 pp error)</li>
          <li>Preserved Case: Reference EF 60.3% &rarr; Tracked EF 29.8% (30.5 pp error)</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- 04 / Task Evolution Timeline -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Task Progression</span>
      <h2>Progression Across Seven Cardiac Rounds</h2>
    </div>

    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-badge">BR-025 / 027 · Phase 1</div>
        <div class="timeline-content">
          <h4>Fetal Echo Contours & Single-Anchor Tracking</h4>
          <p>Four-view contour reconstruction reached 0.937 Dice. Removing annotations down to one frame exposed severe tracking errors, proving that EF alone can conceal massive volume errors.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-029 / 031 · Phase 2</div>
        <div class="timeline-content">
          <h4>STRAUS Synthetic Mechanics & Agent Capability Levels</h4>
          <p>Introduced biventricular simulation truth. Terra computed strain correctly from known motion, but 4-view image reconstruction failed. Adding full 3D ultrasound volume did not rescue Sol's mechanics.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-032 / 034 · Phase 3</div>
        <div class="timeline-content">
          <h4>Real Clinical Ultrasound & EF Underestimation</h4>
          <p>BR-032 revealed that an initial agent animation re-used fixed measurement tables. BR-034 forced true image tracking on EchoXFlow, uncovering the 23–30 pp EF underestimation failure.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-035 · Final</div>
        <div class="timeline-content">
          <h4>Full-Cycle Masks: Separating Geometry from Strain</h4>
          <p>Supplied complete 3D masks at all 30 phases. Sol constructed valid meshes with correct longitudinal/circumferential strain, but radial strain failed, proving boundary limits.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- 05 / Critical Caveats -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">05 / Takeaways & Clinical Reality</span>
      <h2>A Good-Looking Tracker Can Misstate Heart Function</h2>
    </div>

    <div class="caveat-box">
      <strong>Surface Closeness Conceals Functional Heart Failure Misdiagnosis</strong>
      <p>In all three clinical ultrasound exams (BR-034), the agent's tracked cavity surface stayed within 3 mm of the ground truth on average. Yet because it failed to capture the full inward excursion during systole, it classified patients with mild ventricular dysfunction as having severe, end-stage heart failure (EF 22% vs true 45%). In clinical cardiology, average surface distance is an insufficient metric: functional amplitudes dictate patient management.</p>
    </div>

    {chapter_nav}
  </section>
</main>
{footer}
<script id="cardiac-data" type="application/json">{figures}</script>
<script>{viewer_js}</script>
</body>
</html>'''
    (MED_DIR / 'cardiac.html').write_text(content)
    print("Wrote site_med/cardiac.html")

def build_landmarks():
    nav = get_nav_html('landmarks')
    footer = get_footer_html()
    chapter_nav = get_chapter_nav(('cardiac.html', 'Domain 5: Cardiac'), ('index.html', 'Overview'))
    head = get_head_html('Domain 6: Semantic 3D Anatomical Landmarks', 'Vertebral spine CT and brain MRI landmark localization, out-of-field-of-view rejection, and MNI atlas assistance')
    
    figures = (SITE_DIR / 'landmark-figures.json').read_text()
    viewer_js = (SITE_DIR / 'landmarks.js').read_text()

    content = f'''<!doctype html>
<html lang="en">
{head}
<body>
{nav}
<main class="main-wrapper">
  <header class="hero">
    <span class="eyebrow">Domain 06 · Spine CT & Brain MRI · 3D Fiducials</span>
    <h1>Semantic 3D Anatomical Landmarks<br><em>& Out-of-FOV Target Rejection</em></h1>
    <p class="lead">Predicting exact 3D physical coordinates of anatomical fiducials across full and cropped scans. Finding the general anatomical neighborhood is easy—placing points with surgical millimeter precision and knowing when a requested vertebra is outside the field of view remain distinct challenges.</p>
    <p class="hero-meta">VerSe Spine CT & AFIDs Brain MRI Cohorts · Sol/xhigh vs Terra/high Matched Comparison · BR-036–BR-040</p>
    
    <div class="keyline-grid">
      <div class="keyline-card">
        <span class="keyline-num">1 / 24</span>
        <span class="keyline-label">Sol full CT vertebrae within 5 mm tolerance</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">14 / 32</span>
        <span class="keyline-label">Sol MRI points within 3 mm (Atlas-assisted)</span>
      </div>
      <div class="keyline-card">
        <span class="keyline-num">0 / 13</span>
        <span class="keyline-label">Sol false detections on cropped CT (0 Hallucinations)</span>
      </div>
    </div>
  </header>

  <!-- 01 / Clinical Context -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">01 / Clinical Intuition & Task Formulation</span>
      <h2>Spine Numbering & Stereotactic Brain Fiducials</h2>
      <p>Anatomical landmarks are discrete, physically meaningful 3D reference points defined by consensus anatomical protocols (e.g. the anterior commissure in the brain, or the centroid of the T4 vertebral body in the spine).</p>
    </div>

    <div class="clinical-card">
      <h4>Why Negative Awareness (Out-of-FOV Rejection) is Crucial</h4>
      <p>In spine surgery, placing a pedicle screw into the wrong vertebral level (e.g. operating on T4 instead of T5) is a catastrophic medical error. In real clinics, CT scans are frequently cropped to limit radiation dose, leaving some vertebrae visible and others outside the Field of View (FOV). An AI model must not guess or hallucinate coordinates into empty air or adjacent bones; it must explicitly recognize when requested anatomy is <em>out of field of view</em>.</p>
    </div>

    <div class="pipeline-flow">
      <div class="flow-card">
        <div class="flow-step">Input Scans</div>
        <b>3D CT / MRI Volumes + Label Queries</b>
        <span>Full CT (24 vertebrae C1–L6), Cropped CT (13 inside, 11 outside), and full T1 MRI (32 consensus brain fiducials).</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Agent Decision</div>
        <b>Counting, Atlas Registration & Verification</b>
        <span>Render orthogonal views, count spinal levels from anatomical anchors, or register standardized anatomical atlases (e.g. MNI template).</span>
      </div>
      <div class="flow-card">
        <div class="flow-step">Expected Output</div>
        <b>3D Voxel [i, j, k] or Out-of-FOV Status</b>
        <span>Return fractional zero-based native voxel coordinates, or explicitly declare <code>out_of_field_of_view</code> / <code>absent</code>.</span>
      </div>
    </div>
  </section>

  <!-- 02 / Interactive Visual Explorer -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">02 / Interactive Visual Explorer</span>
      <h2>Inspect the Seven Representative Clinical Panels</h2>
      <p>Select cases to examine CT wrong-level detections, Terra's outside-target hallucination, Sol's missed visible targets, and MRI points where atlas assistance produced dramatic improvements.</p>
    </div>

    <div class="viewer-card" style="padding: 24px;">
      <div id="landmark-explorer"></div>
      <p class="small">Green cross = Ground Truth Reference; Orange marker = Terra/high; Purple marker = Sol/xhigh. Slices are centered on the reference coordinate; printed off-plane offsets explain why 2D visual overlap can conceal 3D depth misalignment.</p>
    </div>
  </section>

  <!-- 03 / Deep Agent Work & Results -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">03 / Deep Agent Analysis</span>
      <h2>Matched Model Comparison: Terra/high vs. Sol/xhigh</h2>
      <p>Comparing performance across full spine CT, cropped CT, and full brain MRI under identical verifiers.</p>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Scan Condition</th>
            <th>Model & Effort</th>
            <th>Points within 5 mm / 10 mm / 20 mm</th>
            <th>Mean Error (mm)</th>
            <th>False Detections on Outside Targets</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Full CT (24 Visible)</strong></td>
            <td>Terra / high</td>
            <td>2 / 7 / 9</td>
            <td>24.77 mm</td>
            <td>0 / 2 absent</td>
          </tr>
          <tr>
            <td><strong>Full CT (24 Visible)</strong></td>
            <td>Sol / xhigh</td>
            <td>1 / 13 / 23</td>
            <td>10.24 mm</td>
            <td>0 / 2 absent</td>
          </tr>
          <tr>
            <td><strong>Partial CT (13 Visible, 11 Outside)</strong></td>
            <td>Terra / high</td>
            <td>1 / 2 / 5</td>
            <td>20.85 mm</td>
            <td><span class="badge badge-miss">1 / 11 False Presence</span> (Wrong-Level)</td>
          </tr>
          <tr>
            <td><strong>Partial CT (13 Visible, 11 Outside)</strong></td>
            <td>Sol / xhigh</td>
            <td>4 / 8 / 12</td>
            <td>7.44 mm</td>
            <td><span class="badge badge-pass">0 / 11 False Presence</span> (0 Hallucinations)</td>
          </tr>
          <tr>
            <td><strong>Full MRI (32 Visible)</strong></td>
            <td>Terra / high</td>
            <td>3 / 8 / 20 (at 3 / 5 / 10 mm)</td>
            <td>9.40 mm</td>
            <td>Not tested</td>
          </tr>
          <tr>
            <td><strong>Full MRI (32 Visible)</strong></td>
            <td>Sol / xhigh (Atlas-Assisted)</td>
            <td>14 / 23 / 32 (at 3 / 5 / 10 mm)</td>
            <td>3.87 mm</td>
            <td>Not tested</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="contrast-grid">
      <div class="contrast-card worked">
        <h4><span style="color: var(--color-green);">✔</span> Where Sol Excelled</h4>
        <ul>
          <li><strong>Negative Awareness & Hallucination Resistance:</strong> On cropped CT, Sol made zero false presence claims on the 11 outside vertebrae. It correctly recognized that the scan lacked cranial counting anchors and abstained rather than hallucinating.</li>
          <li><strong>Autonomous Atlas Integration (MRI):</strong> On brain MRI, Sol autonomously downloaded the MNI brain template and AFIDs protocol illustrations, affinely registered the template to the scan, and refined fiducials, jumping from 3/32 to 14/32 points within 3 mm!</li>
          <li><strong>Coarse Localization:</strong> Sol achieved mean errors of 10.2 mm on CT and 3.87 mm on MRI, consistently finding the correct anatomical region.</li>
        </ul>
      </div>

      <div class="contrast-card failed">
        <h4><span style="color: var(--color-red);">✖</span> The Limits of Visual Precision</h4>
        <ul>
          <li><strong>Millimeter Precision Gap:</strong> On full CT, only 1 of 24 vertebrae met the surgical 5 mm tolerance. While Sol found the right vertebral level, its centroid coordinates drifted by 6–12 mm along the superior-inferior axis.</li>
          <li><strong>Terra's Wrong-Level Hallucination:</strong> On partial CT, Terra submitted a predicted coordinate for T4 that lay 2.14 mm from the real T5 center—a classic wrong-level detection that would result in surgical error.</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- 04 / Task Evolution Timeline -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">04 / Task Progression</span>
      <h2>Evolution Across Four Landmark Rounds</h2>
    </div>

    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-badge">BR-036 · Phase 1</div>
        <div class="timeline-content">
          <h4>PDDCA Head-and-Neck CT & AFIDs MRI Pilot</h4>
          <p>Initial 4-point CT and 8-point MRI tasks. Terra met 1/4 CT rules and 0/8 MRI rules. Highlighted ambiguity in world vs voxel coordinate conventions.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-038 · Phase 2</div>
        <div class="timeline-content">
          <h4>Coordinate Contract Audit & 3D Voxel Standards</h4>
          <p>Audited potential coordinate frame bugs. Introduced strict zero-based native voxel indexing (<code>voxel_ijk_zero_based</code>) and an affine-based physical distance verifier.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-039 · Phase 3</div>
        <div class="timeline-content">
          <h4>Expanded VerSe Spine CT & Hallucination Stress</h4>
          <p>Expanded CT to 26 vertebral targets (C1–L6). Introduced the cropped CT condition to specifically measure hallucinations on out-of-field-of-view vertebrae.</p>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-badge">BR-040 · Final</div>
        <div class="timeline-content">
          <h4>Matched Sol vs. Terra Comparison & Atlas Leverage</h4>
          <p>Head-to-head comparison on identical frozen inputs. Sol proved immune to false presence claims on cropped CT and demonstrated autonomous atlas registration on MRI.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- 05 / Critical Caveats -->
  <section class="report-section">
    <div class="section-head">
      <span class="eyebrow">05 / Takeaways & Clinical Reality</span>
      <h2>Coarse Localization vs. Surgical Millimeter Precision</h2>
    </div>

    <div class="caveat-box">
      <strong>Visual Search Alone Plateaus at ~10 mm</strong>
      <p>General coding agents inspecting 2D slice renderings can reliably identify the gross anatomical neighborhood of an organ or bone. However, surgical applications demand sub-3 mm precision. Achieving true surgical precision requires integrating external statistical shape models or deformable anatomical atlases—as Sol demonstrated by downloading the MNI template.</p>
    </div>

    {chapter_nav}
  </section>
</main>
{footer}
<script id="landmark-data" type="application/json">{figures}</script>
<script>{viewer_js}</script>
</body>
</html>'''
    (MED_DIR / 'landmarks.html').write_text(content)
    print("Wrote site_med/landmarks.html")

def main():
    print("Building site_med pages...")
    build_index()
    build_segmentation()
    build_aneurysm()
    build_registration()
    build_vessels()
    build_cardiac()
    build_landmarks()
    print("All site_med pages built successfully!")

if __name__ == '__main__':
    main()
