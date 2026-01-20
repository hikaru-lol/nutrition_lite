'use client';
import { useEffect, useRef, useState } from 'react';

export default function Playground() {
  const boxRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState<number>(0);
  console.log('width', width);

  useEffect(() => {
    console.log('boxRef', boxRef.current);
    const el = boxRef.current;
    if (!el) return;

    const measure = () => setWidth(el.getBoundingClientRect().width);

    measure(); // 初回
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

  return (
    <div className="space-y-2">
      <div ref={boxRef} className="rounded-xl border border-slate-800 p-4">
        この要素の横幅を測る
      </div>
      <p className="text-xs text-slate-400">width: {width}px</p>
    </div>
  );
}
