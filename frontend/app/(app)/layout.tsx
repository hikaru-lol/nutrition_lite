// frontend/app/(app)/layout.tsx
import type { ReactNode } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { RichUi } from '@/components/playground/RichUi';
import AdvancedDashboard from '@/components/playground/advanced-dashboard/AdvancedDashboard';
import Playground from '@/components/playground/Playground';
import LayoutLab from '@/components/playground/Layoutlab';

export default function AppLayout({ children }: { children: ReactNode }) {
  type WhichUI =
    | 'appShell'
    | 'richUI'
    | 'advancedDashboard'
    | 'playground'
    | 'layoutlab';
  function renderContent(whichUI: WhichUI) {
    if (whichUI === 'appShell') {
      return <AppShell>{children}</AppShell>;
    } else if (whichUI === 'richUI') {
      return <RichUi />;
    } else if (whichUI === 'advancedDashboard') {
      return <AdvancedDashboard />;
    } else if (whichUI === 'playground') {
      return <Playground />;
    } else if (whichUI === 'layoutlab') {
      return <LayoutLab viewState={{ kind: 'dropdownexample' }} />;
    }
  }

  return renderContent('appShell');
}
