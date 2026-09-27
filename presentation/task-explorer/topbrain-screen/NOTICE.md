# TopBrain source-screen teaching assets

Source: TopBrain Challenge Organizers / University Hospital of Zurich, TopBrain data release Batches1n2nTA36_081726, https://zenodo.org/records/21972006. MRA originates in TopCoW: https://zenodo.org/records/15692630. Released TA36 model: https://zenodo.org/records/21959166. Cite Yang et al., TopBrain segmentation challenge for whole brain vessel anatomy (2026), and Yang et al., The TopCoW Challenge (2026).

The exact retained DATA-LICENSE.txt permits noncommercial use with attribution; commercial use requires the owner's permission. Code/model licensing does not replace data terms.

Five public training/development MRA scans, one released ResEncM fold-4 component on MPS; no official ensemble replication or coding-agent trial. Original predictions and all historical records remain unchanged. Author-selected views use prediction/reference extents. Source labels are hidden until reader reveal; these teaching files embed references and are not a solver packet.

Native pixels are unresampled. Display transposes and reverses the second in-plane axis; affine vectors, voxel bounds, axis/index, intensity windows and physical pixel spacing are retained. MIPs collapse a stated depth and do not prove 3D contacts. Overlay colors: blue context; orange first named class; turquoise second named class; pink saved additions or disconnected reference components, identified beside each scene.

Contacts count PCA voxels neighboring SCA in full 3D 6/26-neighbour masks, not adjacency pairs. Attachment uses a specified named-label chain, not whole-brain connectivity or clinical adjudication. Macro Dice averages nonbackground classes present in either mask, with each class equally weighted. The retained interior screen uses a 0.5 mm reference-interior cutoff and is not exhaustive for thin vessels.

The calibration changes two native voxels only. BA-to-R-SCA routing, eight CPRs and a one-component watertight mesh are saved author outputs, not newly executed repairs. All 140352 retained CPR samples are checked against original MRA. Display-only interpolation maps saved signal rows to uniform physical arc; raw row rasters remain included. Pixel-centre extent is 10.2 mm across 51 offsets at 0.2 mm. No view resolves the remaining reference-background addition or establishes a hard benchmark.
