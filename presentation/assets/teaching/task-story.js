// Reusable teaching recipes. These describe output contracts, never case results.
export const TaskTeachingStory = (() => {
  const recipes = {};
  const add = (kinds, action, cue, form) => {
    for (const kind of kinds.split(' ')) recipes[kind] = { action, cue, form };
  };
  add(
    'segment',
    'Label each region',
    'Follow the image boundaries; assign the requested label to each location.',
    'Spatial label map',
  );
  add(
    'instances',
    'Separate each object',
    'Keep neighboring objects separate and give each one its own identity.',
    'Individual object masks',
  );
  add(
    'nuclei',
    'Mark every center',
    'Find cell nuclei in the tissue and mark their centers.',
    'A set of nucleus points',
  );
  add(
    'landmark_point',
    'Locate the named target',
    'Search the supplied image for the requested landmark; a point marks the output shape.',
    'A location or unavailable response',
  );
  add(
    'nodule_outline',
    'Trace the boundary',
    'Follow the edge of the candidate, rather than marking only its center.',
    'An outline',
  );
  add(
    'detect',
    'Draw the target box',
    'Find the relevant region and bound its extent in the image.',
    'Image coordinates + box extent',
  );
  add(
    'box3d',
    'Locate in the volume',
    'The box needs an extent through slices as well as across the image.',
    'A three-dimensional box',
  );
  add(
    'candidate_judgment',
    'Assess the candidate',
    'Inspect the supplied candidate and return a supported judgment with uncertainty.',
    'A candidate judgment',
  );
  add(
    'anatomy_audit',
    'Check the supplied labels',
    'Compare each supplied label with the spatial evidence and identify a witness.',
    'Affected label + spatial witness',
  );
  add(
    'object_identity',
    'Name each supplied object',
    'Use shape and context to identify each separately supplied object.',
    'Object-to-label mapping',
  );
  add(
    'mask_shortcuts',
    'Check shortcut cues',
    'Compare size and position cues with the identity question.',
    'Comparison of object cues',
  );
  add(
    'anatomy_curation',
    'Review candidate tasks',
    'Inspect source context before retaining, holding or excluding a candidate.',
    'A curation decision with evidence',
  );
  add(
    'dynamic_mesh',
    'Recover shape over time',
    'Follow cavity shape across phases; a changing surface does not establish tissue motion.',
    'A surface for each phase',
  );
  add(
    'cardiac_contours',
    'Connect the phase contours',
    'Use the supplied contours to recover a cavity surface at each phase.',
    'Time-varying cavity surfaces',
  );
  add(
    'cardiac_anchors',
    'Fill in the motion',
    'Use the supplied anchor phases to recover the intervening geometry.',
    'Geometry between anchor phases',
  );
  add(
    'cardiac_material',
    'Track material points',
    'Preserve point identities as the geometry deforms.',
    'A material trajectory',
  );
  add(
    'point_correspondence',
    'Match the same anatomy',
    'Keep the source point fixed; locate the corresponding structure in the target.',
    'A returned target point',
  );
  add(
    'register',
    'Align the two images',
    'Bring corresponding structures into the same coordinate frame.',
    'A spatial transform',
  );
  add(
    'registration_diagnosis',
    'Inspect the mismatch',
    'Separate transform-composition errors from correspondence or search errors.',
    'A supported failure explanation',
  );
  add(
    'longitudinal',
    'Match across examinations',
    'Link the same finding across earlier and later images before describing change.',
    'Linked findings over time',
  );
  add(
    'route_repair',
    'Repair the supported route',
    'Inspect the break in a branch and retain only a supported connection.',
    'A connected route',
  );
  add(
    'route_discovery',
    'Find the requested path',
    'Trace the named path through the branching structure.',
    'A named route',
  );
  add(
    'route_unfold',
    'Straighten the route',
    'Follow the vessel path, then lay its neighborhood out for inspection.',
    'An unfolded image along the path',
  );
  add(
    'vesselgraph',
    'Connect the branch points',
    'Turn the visible branching structure into nodes and connections.',
    'A vessel graph',
  );
  add(
    'vessel_source_screen',
    'Check the source labels',
    'Review whether the source provides the context needed for the proposed vessel task.',
    'Source suitability + limits',
  );
  add(
    'prediction_screen',
    'Compare the two structures',
    'Inspect where the supplied prediction differs from the separate reference.',
    'A supported comparison',
  );
  add(
    'mri mri_dynamic',
    'Reconstruct the scan',
    'Use the sampled measurements to recover an image; preserve time order for a sequence.',
    'Reconstructed image or sequence',
  );
  add(
    'ct ct_phantom',
    'Reconstruct the cross-section',
    'Combine measurements taken from different angles to recover the interior.',
    'A reconstructed cross-section',
  );
  add(
    'dualct',
    'Separate the materials',
    'Use the two measurement energies to estimate separate material images.',
    'Aligned material maps',
  );
  add(
    'pet',
    'Reconstruct the activity',
    'Use the measured events to estimate a spatial activity image.',
    'An activity map',
  );
  add(
    'denoise',
    'Remove image noise',
    'Reduce noise while retaining the structures needed to interpret the image.',
    'A restored image',
  );
  add(
    'superres',
    'Recover finer detail',
    'Estimate a finer image from the supplied lower-resolution measurements.',
    'A higher-resolution image',
  );
  add(
    'restore3d',
    'Restore the volume',
    'Recover structure across slices, preserving spatial consistency.',
    'A restored volume',
  );
  add(
    'synthesis',
    'Generate the requested contrast',
    'Map the supplied image information into the requested image representation.',
    'An aligned synthetic image',
  );
  add(
    'lensless',
    'Decode the measurement',
    'Recover image structure from the coded sensor observation.',
    'A reconstructed image',
  );
  add(
    'image_sequence',
    'Restore the sequence',
    'Recover each frame while retaining the order and relationship between frames.',
    'An ordered image sequence',
  );
  add(
    'ultrasound photoacoustic',
    'Reconstruct from signals',
    'Use the measured wave signals to locate internal structure.',
    'A reconstructed image',
  );
  add(
    'soundmap',
    'Estimate sound speed',
    'Use the measured signals to estimate how sound travels through the region.',
    'A spatial sound-speed map',
  );
  add(
    'seismic',
    'Recover the subsurface',
    'Use the received waves to estimate the underlying layers.',
    'A subsurface model',
  );
  add(
    'conductivity',
    'Map electrical conductivity',
    'Use the boundary measurements to estimate the interior conductivity.',
    'A spatial conductivity map',
  );
  add(
    'odt idt',
    'Recover the optical volume',
    'Combine optical measurements from different views into a volumetric estimate.',
    'A refractive-index volume',
  );
  add(
    'diffraction',
    'Recover amplitude and phase',
    'Infer both requested image components from diffraction measurements.',
    'Two distinct image components',
  );
  add(
    'opticalvolume',
    'Recover depth from views',
    'Combine the observed light pattern into a depth-resolved volume.',
    'An optical volume',
  );
  add(
    'molecules',
    'Localize the emitters',
    'Infer spatial emitter locations from the observed image signals.',
    'Three-dimensional emitter positions',
  );
  add(
    'nlos',
    'Locate the hidden object',
    'Use indirect light observations to recover structure outside the direct view.',
    'A hidden-object estimate',
  );
  add(
    'wavefront',
    'Recover the wavefront',
    'Convert measured spot displacements into the corresponding optical wavefront.',
    'A wavefront estimate',
  );
  add(
    'deflectometry',
    'Recover the surface shape',
    'Compare reflected patterns to estimate thickness and curvature.',
    'Surface shape parameters',
  );
  add(
    'tensor',
    'Estimate local directions',
    'Recover the directional quantity at each image location.',
    'A spatial tensor field',
  );
  add(
    't2',
    'Fit the signal decay',
    'Use signal changes across measurements to estimate a spatial relaxation map.',
    'A quantitative image map',
  );
  add(
    'spectral',
    'Separate spectral components',
    'Use wavelength-dependent measurements to recover the requested components.',
    'Separate component maps',
  );
  add(
    'spectral_cube',
    'Recover each wavelength',
    'Separate the coded measurement into aligned wavelength bands; the stack is spectral.',
    'An image for each wavelength',
  );
  add(
    'temperature',
    'Estimate temperature',
    'Map the supplied measurement to the requested temperature quantity.',
    'A temperature estimate',
  );
  add(
    'phase',
    'Unwrap the phase',
    'Resolve phase jumps into a consistent phase estimate.',
    'A continuous phase estimate',
  );
  add(
    'geofield',
    'Recover the missing field',
    'Use observed locations to estimate the field over the requested region.',
    'A spatial field',
  );
  add(
    'astronomy',
    'Recover the observed structure',
    'Use the supplied observations to reconstruct the astronomical structure.',
    'A reconstructed image',
  );
  add(
    'astro_uncertainty',
    'Show structure and uncertainty',
    'Keep uncertain image structure visible alongside the reconstruction.',
    'Reconstruction + uncertainty',
  );
  add(
    'astro_dynamic',
    'Recover changes over time',
    'Use the time-ordered observations to reconstruct the changing structure.',
    'A time-varying reconstruction',
  );
  add(
    'astro_features',
    'Recover the time features',
    'Extract the requested temporal features from the observation series.',
    'Features indexed by time',
  );
  add(
    'astro_volume',
    'Recover the spatial volume',
    'Infer the requested depth-resolved structure from the observations.',
    'A spatial volume',
  );
  add(
    'planet',
    'Find the faint candidate',
    'Separate the faint object of interest from the bright surrounding signal.',
    'A candidate location',
  );
  add(
    'classify',
    'Choose one class',
    'Read the image evidence and return one label from the allowed set.',
    'One class label',
  );
  add(
    'multilabel',
    'Assess each label',
    'Evaluate each requested label independently; more than one may apply.',
    'One value per requested label',
  );
  add(
    'report',
    'Write supported findings',
    'Turn image evidence into the requested report, retaining uncertainty and unknowns.',
    'Structured findings text',
  );
  add(
    'caption',
    'Describe the image',
    'Describe what the image supports in the requested text format.',
    'An image description',
  );
  add(
    'vqa',
    'Answer the image question',
    'Use the supplied image to answer the specific question.',
    'A question-specific answer',
  );
  add(
    'quality',
    'Assess image quality',
    'Inspect the image using the task’s quality criteria.',
    'A quality assessment',
  );
  add(
    'tiles',
    'Inspect the tissue tiles',
    'Read the local tissue views and combine the requested evidence.',
    'Tile-level or slide-level output',
  );
  add(
    'workflow',
    'Complete the image workflow',
    'Apply the requested steps and return the required image and analysis artifacts.',
    'Requested workflow artifacts',
  );
  add(
    'viewer',
    'Find the requested view',
    'Navigate the supplied image to the requested location and display state.',
    'A specified viewer state',
  );
  add(
    'metadata',
    'Read the requested field',
    'Locate the requested metadata field in the supplied study or series.',
    'A field value',
  );
  add(
    'records',
    'Find the relevant records',
    'Inspect the table and return the requested rows or record-level decisions.',
    'Selected or labeled records',
  );
  add(
    'etl',
    'Combine the source tables',
    'Align the requested fields across sources and return a consistent table.',
    'A unified table',
  );
  add(
    'trials',
    'Match the eligibility criteria',
    'Compare the patient evidence with each trial’s inclusion and exclusion criteria.',
    'Supported trial identifiers',
  );
  add(
    'risk',
    'Estimate one probability',
    'Use only information available before the cutoff for each prediction row.',
    'One scalar probability per row',
  );
  add(
    'source_provenance',
    'Connect the source evidence',
    'Trace the proposed task to its source, prior evidence and feasibility limits.',
    'A source-backed assessment',
  );
  add(
    'segmenter_calibration',
    'Compare the mask boundaries',
    'Keep the supplied box fixed and compare tool boundaries with the reference.',
    'A tool/reference comparison',
  );

  const subjects = {
    abdomen: 'Abdominal anatomy',
    brain: 'Brain anatomy',
    chest: 'Chest view',
    'chest-ct': 'Chest anatomy',
    torso: 'Torso overview',
    heart: 'Heart anatomy',
    teeth: 'Dental arch',
    tissue: 'Microscopy field',
    skin: 'Skin image',
    wrist: 'Wrist view',
    knee: 'Knee view',
    breast: 'Breast image',
    prostate: 'Prostate anatomy',
    aorta: 'Aortic tree',
    airways: 'Lungs and airways',
    vessels: 'Branching vessels',
    'brain-vessels': 'Brain vessel network',
    ultrasound: 'Ultrasound sector',
  };
  function describe(entry) {
    const d = entry.illustration;
    if (!recipes[d.kind]) throw new Error('Missing teaching recipe: ' + d.kind);
    const recipe = { ...recipes[d.kind] };
    if (d.kind === 'segment' && d.mask_mode === 'binary')
      Object.assign(recipe, {
        action: 'Isolate the target',
        form: 'One binary target mask',
        cue: 'Keep the requested target separate from the background; the output contains one foreground class.',
      });
    if (d.kind === 'segment' && d.mask_mode === 'separate')
      Object.assign(recipe, {
        action: 'Separate organ and lesion',
        form: 'Two separate masks',
        cue: 'Return the organ and lesion as distinct spatial outputs; one merged region loses this distinction.',
      });
    if (d.kind === 'point_correspondence' && d.initial_candidate)
      recipe.cue =
        'Keep the query fixed; inspect the supplied target candidate and retain or move it to matching anatomy.';
    if (d.kind === 'register' && d.scene_variant === 'slice-to-volume')
      Object.assign(recipe, {
        action: 'Place the section in 3D',
        form: 'Pixel-to-patient transform',
        cue: 'Find the position and tilt of this one section inside the target volume; return its spatial transform.',
      });
    return {
      ...recipe,
      context: subjects[d.subject] || 'Input structure',
      target: d.target ? d.target.replaceAll('_', ' ') : null,
      stages: [
        'Inspect input',
        recipe.action,
        entry.role && entry.role !== 'task' ? 'Study output' : 'Output shape',
      ],
    };
  }
  return { describe, kinds: Object.keys(recipes) };
})();
