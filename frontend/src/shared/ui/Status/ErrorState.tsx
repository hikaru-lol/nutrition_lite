'use client';

export function ErrorState(props: { title?: string; message?: string }) {
  return (
    <div className="w-full rounded-xl border p-6">
      <div className="text-base font-semibold">{props.title ?? 'Error'}</div>
      {props.message ? (
        <div className="mt-1 text-sm text-muted-foreground">
          {props.message}
        </div>
      ) : null}
    </div>
  );
}
