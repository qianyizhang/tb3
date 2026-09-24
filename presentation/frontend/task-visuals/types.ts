import type { Illustration } from '../types';

/** Display coordinates, never patient coordinates. */
export type ScreenPoint = readonly [x: number, y: number];
export type ScenePoint = readonly [x: number, y: number, z: number];
export type Segment = readonly [start: ScenePoint, end: ScenePoint];
export type Quad = readonly [a: ScenePoint, b: ScenePoint, c: ScenePoint, d: ScenePoint];
export type Polygon = readonly [ScenePoint, ScenePoint, ScenePoint, ...ScenePoint[]];
export type Stage = 0 | 1 | 2;
export interface VisualEntry {
  illustration: Illustration;
  role?: string;
}
interface Mark {
  color: string;
  alpha: number;
}
export interface Face extends Mark {
  type: 'face';
  points: Polygon;
  surface?: boolean;
  backdrop?: boolean;
  normals?: ScenePoint[];
  asset?: string | null;
}
export interface Line extends Mark {
  type: 'line';
  points: Segment;
  width: number;
  dash: boolean;
}
export interface Dot extends Mark {
  type: 'dot';
  points: readonly [ScenePoint];
  radius: number;
}
export interface ImagePlane extends Mark {
  type: 'image';
  points: Quad;
  subject: string;
}
export type Primitive = Face | Line | Dot | ImagePlane;
export interface Annotation {
  p: ScenePoint;
  text: string;
  color: string;
  anchor?: ScenePoint;
}
export interface SceneModel {
  primitives: Primitive[];
  labels: Annotation[];
}
export interface AnatomyPart {
  id: string;
  label: string;
  vertices: ScenePoint[];
  faces: number[][];
  normals?: ScenePoint[];
  provenance: string;
}
export type LegendKey = [color: string, label: string, dashed?: boolean];
export interface SceneView {
  width: number;
  height: number;
  yaw: number;
  pitch: number;
}
