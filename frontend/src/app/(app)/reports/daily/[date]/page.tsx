// app/(app)/reports/daily/[date]/page.tsx
import { DailyReportPage } from '@/components/reports/DailyReportPage';

type PageProps = {
  params: { date: string };
};

export default async function Page({ params }: PageProps) {
  const { date } = await params;
  return <DailyReportPage date={date} />;
}
