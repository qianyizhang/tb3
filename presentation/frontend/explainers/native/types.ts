/** Adapters draw native data; the reader owns chapter timing and reference consent. */
export interface NativeStageProps<Payload> {
  payload: Payload;
  stateId: string | null;
  chapterId: string;
  referenceShown: boolean;
  onReady: (ready: boolean) => void;
}
