'use client';

import React from 'react';

export function MiniLineChart({
  points,
  height = 56,
}: {
  points: number[];
  height?: number;
}) {
  const w = 240;
  const h = height;
  const pad = 6;

  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = Math.max(1, max - min);

  const coords = points.map((v, i) => {
    const x = pad + (i * (w - pad * 2)) / Math.max(1, points.length - 1);
    const y = pad + (1 - (v - min) / range) * (h - pad * 2);
    return { x, y };
  });

  const d = coords
    .map((p, i) =>
      i === 0
        ? `M ${p.x.toFixed(2)} ${p.y.toFixed(2)}`
        : `L ${p.x.toFixed(2)} ${p.y.toFixed(2)}`
    )
    .join(' ');

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-14 w-60">
      <defs>
        <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="currentColor" stopOpacity="0.25" />
          <stop offset="1" stopColor="currentColor" stopOpacity="0" />
        </linearGradient>
      </defs>

      <path
        d={`${d} L ${coords[coords.length - 1].x.toFixed(2)} ${(
          h - pad
        ).toFixed(2)} L ${coords[0].x.toFixed(2)} ${(h - pad).toFixed(2)} Z`}
        fill="url(#area)"
        className="text-blue-600"
      />
      <path
        d={d}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        className="text-blue-600"
      />
      {coords.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="2.5" className="fill-blue-600" />
      ))}
    </svg>
  );
}
