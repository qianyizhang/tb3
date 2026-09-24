import type { Illustration } from '../types';

/** Display coordinates, never patient coordinates. Geometry checks enforce three components. */
export type Point = number[];
export type Stage = 0 | 1 | 2;
export interface VisualEntry {
  illustration: Illustration;
  role?: string;
}
interface Mark {
  points: Point[];
  color: string;
  alpha: number;
}
export interface Face extends Mark {
  type: 'face';
  surface?: boolean;
  backdrop?: boolean;
  normals?: Point[];
  asset?: string | null;
}
export interface Line extends Mark {
  type: 'line';
  width: number;
  dash: boolean;
}
export interface Dot extends Mark {
  type: 'dot';
  radius: number;
}
export interface ImagePlane extends Mark {
  type: 'image';
  subject: string;
}
export type Primitive = Face | Line | Dot | ImagePlane;
export interface Annotation {
  p: Point;
  text: string;
  color: string;
  anchor?: Point;
}
export interface SceneModel {
  primitives: Primitive[];
  labels: Annotation[];
}
export interface AnatomyPart {
  id: string;
  label: string;
  vertices: Point[];
  faces: number[][];
  normals?: Point[];
  provenance: string;
}
export type LegendKey = [color: string, label: string, dashed?: boolean];
export interface SceneView {
  width: number;
  height: number;
  yaw: number;
  pitch: number;
}
