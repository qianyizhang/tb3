/** Shared contract for the export page and its Node capture adapter. */
export interface CaptureRequest {
  frame: number;
  fps: number;
  width: number;
  height: number;
}

declare global {
  interface Window {
    __tb3ExplainerCapture?: {
      ready: Promise<void>;
      seekFrame(request: CaptureRequest): Promise<void>;
    };
  }
}
