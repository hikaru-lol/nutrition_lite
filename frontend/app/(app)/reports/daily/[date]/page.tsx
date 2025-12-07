// app/(app)/reports/daily/[date]/page.tsx
import { DailyReportPage } from '@/components/reports/DailyReportPage';

type PageProps = {
  params: { date: string };
};

export default function Page({ params }: PageProps) {
  const { date } = params;
  return <DailyReportPage date={date} />;
}
