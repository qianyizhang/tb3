import inputJson from '../../task-explorer/imaging101-cars/inputs.json?raw';
import referenceJson from '../../task-explorer/imaging101-cars/reference.json?raw';
import contractJson from '../../task-explorer/imaging101-cars/contract.json?raw';
import type { StoryState } from './story-timeline';
export type CarsState = Extract<StoryState, { recipe: 'imaging101-cars-v1' }>;
export const carsInput = JSON.parse(inputJson) as { nu: number[]; measured: number[] };
export const carsReference = JSON.parse(referenceJson) as {
  clean: number[];
  temperature_K: number;
  x_mol: number;
};
export const carsContract = JSON.parse(contractJson) as {
  fit: number[];
  temperature_K: number;
  proposals: { temperature_K: number; curve: number[] }[];
  replay: { ncc: number; nrmse: number; temperature_error_K: number };
};
export function carsReveal(s: CarsState) {
  return s.scene === 'reference' && s.reference > 0.5;
}
export function carsIndex(s: CarsState, count: number) {
  return Math.min(count - 1, Math.floor(s.view * count));
}
export function carsResidual(index: number) {
  return carsContract.fit[index] - carsInput.measured[index];
}
