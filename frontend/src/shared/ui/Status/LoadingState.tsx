'use client';

export function LoadingState(props: { label?: string }) {
  return (
    <div className="w-full rounded-xl border p-6 text-sm">
      {props.label ?? 'Loading...'}
    </div>
  );
}
