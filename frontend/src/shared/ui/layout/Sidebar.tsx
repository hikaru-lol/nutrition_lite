'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BarChart3,
  Target,
  User,
  CreditCard,
  Home,
  ChevronLeft,
  Settings,
  Calendar
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  className?: string;
}

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const navItems: NavItem[] = [
  {
    title: '今日',
    href: '/today',
    icon: Home,
  },
  {
    title: 'カレンダー',
    href: '/calendar',
    icon: Calendar,
  },
  {
    title: '目標',
    href: '/targets',
    icon: Target,
  },
  {
    title: 'レポート',
    href: '/reports',
    icon: BarChart3,
    badge: 'Soon',
  },
  {
    title: '料金プラン',
    href: '/billing/plan',
    icon: CreditCard,
  },
];

export function Sidebar({ isOpen = true, onClose, className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();

  const toggleCollapsed = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <>
      {/* モバイル用オーバーレイ */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* サイドバー本体 */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full bg-muted/50 border-r transition-all duration-300',
          isCollapsed ? 'w-16' : 'w-64',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          'lg:translate-x-0 lg:relative lg:top-0 lg:h-full',
          className
        )}
      >
        <div className="flex h-full flex-col">
          {/* コラプス切替ボタン（デスクトップのみ） */}
          <div className="hidden lg:flex justify-end p-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleCollapsed}
              className="h-8 w-8 p-0"
            >
              <ChevronLeft
                className={cn(
                  'h-4 w-4 transition-transform',
                  isCollapsed && 'rotate-180'
                )}
              />
            </Button>
          </div>

          {/* ナビゲーション */}
          <nav className="flex-1 space-y-1 p-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Link key={item.href} href={item.href}>
                  <div
                    className={cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground',
                      isActive && 'bg-accent text-accent-foreground',
                      isCollapsed && 'justify-center px-2'
                    )}
                    onClick={onClose}
                  >
                    <Icon className="h-4 w-4 shrink-0" />

                    {!isCollapsed && (
                      <>
                        <span className="truncate">{item.title}</span>
                        {item.badge && (
                          <span className="ml-auto rounded-md bg-primary px-1.5 py-0.5 text-xs text-primary-foreground">
                            {item.badge}
                          </span>
                        )}
                      </>
                    )}
                  </div>
                </Link>
              );
            })}
          </nav>

          {/* 設定セクション */}
          <div className="border-t p-2">
            <Link href="/settings">
              <div
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground',
                  pathname === '/settings' && 'bg-accent text-accent-foreground',
                  isCollapsed && 'justify-center px-2'
                )}
                onClick={onClose}
              >
                <Settings className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span className="truncate">設定</span>}
              </div>
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}