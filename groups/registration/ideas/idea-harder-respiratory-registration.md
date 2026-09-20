+++
schema_version = 2
kind = "idea"
id = "idea-harder-respiratory-registration"
group_id = "registration"
title = "Recover lung landmarks despite stronger nonuniform respiratory deformation"
next_action = "Preserve patient3-view1 and its complete failure analysis as a candidate for a separately authorized replication study. No further trial is scheduled. Patient2 remains unadmitted: all fixed author methods fail, including a view only 0.00127 mm beyond the maximum gate; this is not evidence of a Sol failure or substantive unsolvability."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "exploring"

[[sources]]
url = "codex://threads/01a0a845-7c2d-7992-a662-24d52831af90"
note = "User requested more challenging cases for Sol in the ongoing registration study on 2026-09-16. Earlier instructions authorize delegated benchmarking. Exact message ID is not exposed."

[[sources]]
url = "https://github.com/MDL-UzL/L2R"
note = "Official evaluation conventions; previously verified manual correspondence CSVs and source arrays are retained."

[[sources]]
url = "https://doi.org/10.5281/zenodo.3835682"
note = "Learn2Reg LungCT 1.11 source attribution, Radboud CT data, CC BY 4.0."

[historical_source]
path = "catalog/ideas/harder-respiratory-registration.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "aadc8a9bfb459a69e64ea5702f1f4635059f56b267e3acb32f30b3790ec315da"
+++

# Recover lung landmarks despite stronger nonuniform respiratory deformation

## Question

Different patients with larger residual deformation after the best global affine fit can expose incorrect anatomical correspondence selection in 2D-to-3D registration without increasing workflow or tightening tolerances.

## Prior findings

Of six predeclared views from two new patients, patient3-view1 passes isolated public-input author feasibility at 2.133 mm RMS / 3.416 mm maximum. One fresh Sol/xhigh attempt then fails normally at 12.731 / 32.203 mm in 1313.1 seconds with matched oracle/nop controls. The agent uses preinstalled SimpleITK rigid and B-spline registration, neighborhood correlation, denser meshes, edge checks, and custom local patch optimization. Its final q04 search is centered on a wrong deformation and cannot come within 25.50 mm of the reference under its chosen bounds. Final q02 is reachable within tolerance but still incorrectly selected. One selected attempt establishes a concrete failure candidate, not stable difficulty.

## Reopen when

Preserve patient3-view1 and its complete failure analysis as a candidate for a separately authorized replication study. No further trial is scheduled. Patient2 remains unadmitted: all fixed author methods fail, including a view only 0.00127 mm beyond the maximum gate; this is not evidence of a Sol failure or substantive unsolvability.
