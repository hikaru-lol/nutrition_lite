'use client';

import { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
  user?: {
    name: string;
    email: string;
  } | null;
  showSidebar?: boolean;
}

export function AppLayout({ children, user, showSidebar = true }: AppLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* ヘッダー */}
      <Header
        user={user}
        onMenuClick={toggleSidebar}
        showMenuButton={showSidebar}
      />

      <div className="flex">
        {/* サイドバー */}
        {showSidebar && (
          <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
        )}

        {/* メインコンテンツ */}
        <main className="flex-1 min-h-[calc(100vh-4rem)]">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}