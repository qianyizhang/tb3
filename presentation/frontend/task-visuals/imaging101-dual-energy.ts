import inputs from '../../task-explorer/imaging101-dual-energy/inputs.json?raw';
import contract from '../../task-explorer/imaging101-dual-energy/contract.json?raw';
import reference from '../../task-explorer/imaging101-dual-energy/reference.json?raw';
import type { StoryState } from './story-timeline';
export type DualEnergyState = Extract<StoryState, { recipe: 'imaging101-dual-energy-v1' }>;
export type DualEnergyImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  transform: 'linear';
};
export const dualEnergyInput = JSON.parse(inputs) as {
  counts: DualEnergyImage[];
  energies: number[];
  spectra: number[][];
  mus: number[][];
  theta: number[];
};
export const dualEnergyData = JSON.parse(contract) as {
  maps: DualEnergyImage[];
  sinograms: DualEnergyImage[];
  rays: {
    detector_bin: number;
    angle_degrees: number;
    saved_material_integrals_g_cm2: number[];
    observed_counts: number[];
    saved_predicted_counts: number[];
    transmission_by_energy: number[];
    count_contributions_by_energy: number[][];
  }[];
  native: Record<
    string,
    {
      tissue_ncc: number;
      tissue_nrmse: number;
      bone_ncc: number;
      bone_nrmse: number;
      mean_ncc: number;
      mean_nrmse: number;
    }
  >;
  generic: Record<string, { ncc?: number; mse?: number; error?: string }>;
  fbp: Record<string, { saved_fbp_max_abs_error: number }>;
};
export const dualEnergyReference = JSON.parse(reference) as {
  maps: DualEnergyImage[];
  solver_visible_all_levels: boolean;
};
export const dualEnergyIndex = (s: DualEnergyState, count = 3) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const dualEnergyReveal = (s: DualEnergyState) =>
  s.scene === 'reference' && s.reference > 0.5;
export const dualEnergyRayPixel = (detector: number, angle: number) => ({
  x: 48 + ((angle + 0.5) / 180) * 252,
  y: 20 + ((detector + 0.5) / 128) * 180,
});
export const dualEnergyExpected = (a: readonly number[]) =>
  dualEnergyInput.spectra.map((s) =>
    s.reduce(
      (v, photons, i) =>
        v +
        photons * Math.exp(-a[0] * dualEnergyInput.mus[0][i] - a[1] * dualEnergyInput.mus[1][i]),
      0,
    ),
  );
