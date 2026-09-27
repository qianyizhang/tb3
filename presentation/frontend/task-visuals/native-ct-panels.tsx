import type { ReactNode } from 'react';
export const CtText = ({
  x = 24,
  y,
  children,
  size = 18,
  color,
}: {
  x?: number;
  y: number;
  children: ReactNode;
  size?: number;
  color?: string;
}) => (
  <text x={x} y={y} style={{ fontSize: size, ...(color ? { fill: color } : {}) }}>
    {children}
  </text>
);
export function NativeCtScan({
  image,
  x,
  y,
  size = 240,
  fov,
  reference,
  output,
  children,
}: {
  image: string;
  x: number;
  y: number;
  size?: number;
  fov: number;
  reference?: string;
  output?: string;
  children?: ReactNode;
}) {
  return (
    <svg x={x} y={y} width={size} height={size} viewBox="0 0 256 256">
      <image href={image} width="256" height="256" data-ct-input />
      {reference && <image href={reference} width="256" height="256" data-ct-reference />}
      {output && <image href={output} width="256" height="256" data-ct-output />}
      {children}
      <g data-ct-scale>
        <rect x="8" y="222" width="80" height="30" fill="black" opacity="0.75" />
        <path d={`M14 245h${(20 / fov) * 256}`} stroke="white" strokeWidth="2" />
        <text x="14" y="238" style={{ fill: 'white', fontSize: 11 }}>
          20 mm
        </text>
      </g>
      <text x="6" y="126" style={{ fill: 'white', fontSize: 13 }}>
        R
      </text>
      <text x="239" y="126" style={{ fill: 'white', fontSize: 13 }}>
        L
      </text>
      <text x="124" y="15" style={{ fill: 'white', fontSize: 13 }}>
        A
      </text>
    </svg>
  );
}
export function CtRows({ values }: { values: string[] }) {
  return (
    <>
      {values.map((v, i) => (
        <g key={v}>
          <rect x="24" y={59 + i * 61} width="552" height="49" rx="5" fill="#e5ebe2" />
          <CtText x={36} y={90 + i * 61} size={16}>
            {v}
          </CtText>
        </g>
      ))}
    </>
  );
}
