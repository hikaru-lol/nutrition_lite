// // frontend/app/(app)/layout.tsx
// import type { ReactNode } from 'react';
// import { AppShell } from '@/components/layout/AppShell';
// import { RichUi } from '@/components/playground/RichUi';
// import AdvancedDashboard from '@/components/playground/advanced-dashboard/AdvancedDashboard';
// import Playground from '@/components/playground/Playground';
// import LayoutLab from '@/components/playground/Layoutlab';

// export default function AppLayout({ children }: { children: ReactNode }) {
//   type WhichUI =
//     | 'appShell'
//     | 'richUI'
//     | 'advancedDashboard'
//     | 'playground'
//     | 'layoutlab';
//   function renderContent(whichUI: WhichUI) {
//     if (whichUI === 'appShell') {
//       // return <AppShell>{children}</AppShell>;
//       return <>{children}</>;
//     } else if (whichUI === 'richUI') {
//       return <RichUi />;
//     } else if (whichUI === 'advancedDashboard') {
//       return <AdvancedDashboard />;
//     } else if (whichUI === 'playground') {
//       return <Playground />;
//     } else if (whichUI === 'layoutlab') {
//       return <LayoutLab viewState={{ kind: 'dropdownexample' }} />;
//     }
//   }

//   return renderContent('appShell');
// }

import { ReactNode } from 'react';
import { Header } from '@/modules/layout/ui/Header'; // 移動したHeaderを使用

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    // Rule A: アプリ全体の背景色と基本構造
    <div className="min-h-screen w-full bg-gray-50">
      <Header />
      {/* メインコンテンツエリア */}
      <main>{children}</main>
    </div>
  );
}
