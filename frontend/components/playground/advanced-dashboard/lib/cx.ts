export type ClassValue = string | false | null | undefined;

export const cx = (...v: ClassValue[]) => v.filter(Boolean).join(' ');
