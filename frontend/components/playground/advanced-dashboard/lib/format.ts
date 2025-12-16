export function formatNumber(n: number) {
  return new Intl.NumberFormat('ja-JP').format(n);
}
