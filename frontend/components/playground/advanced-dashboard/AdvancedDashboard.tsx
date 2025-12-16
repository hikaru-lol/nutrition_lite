'use client';

import React, { useMemo, useRef, useState } from 'react';

// Types
import type { Command, Meal, SortState, Totals } from './types';

// Lib
import { cx } from './lib/cx';
import { formatNumber } from './lib/format';

// Hooks
import { useMealsDemo } from './hooks/useMealsDemo';
import { useToasts } from './hooks/useToasts';
import { useRecentCommands } from './hooks/useRecentCommands';
import { useGlobalHotkeys } from './hooks/useGlobalHotkeys';

// UI
import { ToastStack } from './ui/ToastStack';
// import { Button } from './ui/Button';

// Features/Layout
import { CommandPalette } from './features/command-palette/CommandPalette';
import { Sidebar } from './features/layout/Sidebar';
import { Topbar } from './features/layout/Topbar';
import { KpiPanel } from './features/layout/KpiPanel';
import { QuickActionsCard } from './features/layout/QuickActionsCard';

// Features/Meals
import { SearchFilters } from './features/meals/SearchFilters';
import { MealsTable } from './features/meals/MealsTable';
import { MealDetailsModal } from './features/meals/MealDetailsModal';

const RECENT_KEY = 'tw_demo_recent_commands_v1';

export default function AdvancedDashboard() {
  const [dark, setDark] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [selected, setSelected] = useState<Meal | null>(null);

  const { loading, meals } = useMealsDemo(650);
  const { toasts, pushToast, dismissToast } = useToasts({
    max: 3,
    durationMs: 2600,
  });
  const { recentIds, markRecent } = useRecentCommands(RECENT_KEY, 10);

  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | Meal['status']>(
    'all'
  );
  const [sort, setSort] = useState<SortState>({ key: 'date', dir: 'desc' });

  const searchInputRef = useRef<HTMLInputElement | null>(null);

  useGlobalHotkeys({
    onOpenPalette: () => setPaletteOpen(true),
    onFocusSearch: () => searchInputRef.current?.focus(),
  });

  const filteredMeals = useMemo(() => {
    const q = query.trim().toLowerCase();
    return meals.filter((m) => {
      const okStatus =
        statusFilter === 'all' ? true : m.status === statusFilter;
      const okQuery =
        q.length === 0
          ? true
          : m.title.toLowerCase().includes(q) || m.date.includes(q);
      return okStatus && okQuery;
    });
  }, [meals, query, statusFilter]);

  const sortedMeals = useMemo(() => {
    const arr = [...filteredMeals];
    const dir = sort.dir === 'asc' ? 1 : -1;
    arr.sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      if (typeof av === 'number' && typeof bv === 'number')
        return (av - bv) * dir;
      if (typeof av === 'string' && typeof bv === 'string')
        return av.localeCompare(bv) * dir;
      return 0;
    });
    return arr;
  }, [filteredMeals, sort]);

  const totals: Totals = useMemo(() => {
    const today = meals.filter((m) => m.date === meals[0]?.date);
    const sum = (
      k: keyof Pick<Meal, 'calories' | 'protein' | 'carbs' | 'fat'>
    ) => today.reduce((acc, m) => acc + m[k], 0);
    return {
      day: meals[0]?.date ?? '—',
      calories: sum('calories'),
      protein: sum('protein'),
      carbs: sum('carbs'),
      fat: sum('fat'),
    };
  }, [meals]);

  const weekCalories = useMemo(() => {
    const byDate = new Map<string, number>();
    for (const m of meals)
      byDate.set(m.date, (byDate.get(m.date) ?? 0) + m.calories);
    const dates = Array.from(byDate.keys())
      .sort((a, b) => a.localeCompare(b))
      .slice(-7);
    return dates.map((d) => byDate.get(d) ?? 0);
  }, [meals]);

  const commands = useMemo<Command[]>(() => {
    return [
      {
        id: 'theme.toggle',
        name: 'Toggle theme (Light/Dark)',
        group: 'Actions',
        icon: '◐',
        keywords: ['dark', 'light', 'theme'],
        shortcut: 'T',
        run: () =>
          setDark((prev) => {
            const next = !prev;
            pushToast('Theme', next ? 'Dark mode' : 'Light mode');
            return next;
          }),
      },
      {
        id: 'focus.search',
        name: 'Focus search input',
        group: 'Actions',
        icon: '/',
        keywords: ['search', 'focus'],
        shortcut: '/',
        run: () => {
          searchInputRef.current?.focus();
          pushToast('Focus', 'Search input focused');
        },
      },
      {
        id: 'filters.reset',
        name: 'Reset filters',
        group: 'Actions',
        icon: '↺',
        keywords: ['reset', 'clear'],
        run: () => {
          setQuery('');
          setStatusFilter('all');
          setSort({ key: 'date', dir: 'desc' });
          pushToast('Filters', 'Reset done');
        },
      },
      {
        id: 'open.first',
        name: 'Open first meal details',
        group: 'Actions',
        icon: '→',
        keywords: ['open', 'details'],
        run: () => {
          const first = sortedMeals[0];
          if (!first) {
            pushToast('Open', 'No items');
            return;
          }
          setSelected(first);
          pushToast('Opened', first.title);
        },
      },

      {
        id: 'filter.all',
        name: 'Filter: All',
        group: 'Filters',
        icon: '•',
        keywords: ['filter'],
        run: () => setStatusFilter('all'),
      },
      {
        id: 'filter.logged',
        name: 'Filter: Logged',
        group: 'Filters',
        icon: '✓',
        keywords: ['filter'],
        run: () => setStatusFilter('logged'),
      },
      {
        id: 'filter.draft',
        name: 'Filter: Draft',
        group: 'Filters',
        icon: '…',
        keywords: ['filter'],
        run: () => setStatusFilter('draft'),
      },
      {
        id: 'filter.flagged',
        name: 'Filter: Flagged',
        group: 'Filters',
        icon: '!',
        keywords: ['filter'],
        run: () => setStatusFilter('flagged'),
      },

      {
        id: 'sort.date',
        name: 'Sort: Date (desc)',
        group: 'Sort',
        icon: '⇅',
        keywords: ['sort', 'date'],
        run: () => setSort({ key: 'date', dir: 'desc' }),
      },
      {
        id: 'sort.cal',
        name: 'Sort: Calories (desc)',
        group: 'Sort',
        icon: '⇅',
        keywords: ['sort', 'calories'],
        run: () => setSort({ key: 'calories', dir: 'desc' }),
      },
      {
        id: 'sort.pro',
        name: 'Sort: Protein (desc)',
        group: 'Sort',
        icon: '⇅',
        keywords: ['sort', 'protein'],
        run: () => setSort({ key: 'protein', dir: 'desc' }),
      },
    ];
  }, [sortedMeals, pushToast]);

  const rootClass = cx(
    'min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100',
    dark && 'dark'
  );

  return (
    <div className={rootClass}>
      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        commands={commands}
        recentIds={recentIds}
        onUseCommand={(id) => markRecent(id)}
      />

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            className="absolute inset-0 bg-black/40"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          />
          <div className="absolute left-0 top-0 h-full w-[min(84vw,320px)] border-r border-gray-200 bg-white shadow-xl dark:border-gray-800 dark:bg-gray-950">
            <Sidebar
              totals={
                {
                  ...totals,
                  calories: Number(formatNumber(totals.calories)),
                  protein: Number(formatNumber(totals.protein)),
                } as Totals
              }
              onOpenPalette={() => setPaletteOpen(true)}
              onNotify={pushToast}
            />
          </div>
        </div>
      )}

      <div className="mx-auto grid max-w-7xl grid-cols-1 lg:grid-cols-[320px_1fr]">
        {/* Desktop sidebar */}
        <aside className="sticky top-0 hidden h-screen border-r border-gray-200 bg-white/60 backdrop-blur dark:border-gray-800 dark:bg-gray-950/40 lg:block">
          <Sidebar
            totals={totals}
            onOpenPalette={() => setPaletteOpen(true)}
            onNotify={pushToast}
          />
        </aside>

        {/* Main */}
        <div className="min-h-screen">
          {/* <Topbar
            onOpenSidebar={() => setSidebarOpen(true)}
            onOpenPalette={() => setPaletteOpen(true)}
          /> */}

          <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
            <section className="grid gap-4 lg:grid-cols-[1fr_320px]">
              <KpiPanel
                loading={loading}
                totals={totals}
                weekCalories={weekCalories}
              />
              <QuickActionsCard
                onToast={pushToast}
                onOpenPalette={() => setPaletteOpen(true)}
              />
            </section>

            <SearchFilters
              query={query}
              onQueryChange={setQuery}
              statusFilter={statusFilter}
              onStatusFilterChange={setStatusFilter}
              sort={sort}
              onSortChange={setSort}
              searchInputRef={
                searchInputRef as React.RefObject<HTMLInputElement>
              }
              onApply={() =>
                pushToast('Search', `Query: ${query || '(empty)'}`)
              }
            />

            <MealsTable
              loading={loading}
              meals={sortedMeals}
              onOpenDetails={(m) => {
                setSelected(m);
                pushToast('Opened', m.title);
              }}
              onResetFilters={() => {
                setQuery('');
                setStatusFilter('all');
                pushToast('Filters reset');
              }}
            />
          </main>
        </div>
      </div>

      <MealDetailsModal
        meal={selected}
        onClose={() => setSelected(null)}
        onSave={() => {
          if (selected) pushToast('Saved', `${selected.title} updated (demo)`);
          setSelected(null);
        }}
      />

      <ToastStack toasts={toasts} dismiss={dismissToast} />
    </div>
  );
}
