'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import type { Command } from '../../types';
import { cx } from '../../lib/cx';
import { KbdCombo } from '../../ui/Kbd';
import { buildSections } from './buildSections';

export function CommandPalette({
  open,
  onClose,
  commands,
  recentIds,
  onUseCommand,
}: {
  open: boolean;
  onClose: () => void;
  commands: Command[];
  recentIds: string[];
  onUseCommand: (id: string) => void;
}) {
  const [q, setQ] = useState('');
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return commands;
    return commands.filter((c) => {
      const hay = `${c.name} ${(c.keywords ?? []).join(' ')}`.toLowerCase();
      return hay.includes(query);
    });
  }, [q, commands]);

  const indexById = useMemo(() => {
    const m = new Map<string, number>();
    filtered.forEach((c, i) => m.set(c.id, i));
    return m;
  }, [filtered]);

  const recentCommands = useMemo(() => {
    const map = new Map(commands.map((c) => [c.id, c]));
    return recentIds.map((id) => map.get(id)).filter(Boolean) as Command[];
  }, [commands, recentIds]);

  const sections = useMemo(
    () => buildSections({ query: q, filtered, recentCommands }),
    [q, filtered, recentCommands]
  );

  useEffect(() => {
    if (!open) return;
    setTimeout(() => {
      setQ('');
      setActive(0);
      inputRef.current?.focus();
    }, 0);
  }, [open]);

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActive((i) => Math.min(i + 1, Math.max(0, filtered.length - 1)));
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActive((i) => Math.max(i - 1, 0));
        return;
      }
      if (e.key === 'Enter') {
        e.preventDefault();
        const cmd = filtered[active];
        if (!cmd) return;
        onUseCommand(cmd.id);
        cmd.run();
        onClose();
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, filtered, active, onClose, onUseCommand]);

  useEffect(() => {
    if (!open) return;
    const el = document.querySelector(
      `[data-cmd-index="${active}"]`
    ) as HTMLElement | null;
    el?.scrollIntoView({ block: 'nearest' });
  }, [active, open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60]">
      <button
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-label="Close command palette"
      />
      <div
        role="dialog"
        aria-modal="true"
        className="relative mx-auto mt-20 w-[min(92vw,720px)] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-950"
      >
        <div className="flex items-center gap-3 border-b border-gray-200 px-4 py-3 dark:border-gray-800">
          <div className="text-gray-400">⌘</div>
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setActive(0);
            }}
            placeholder="Type a command… (Try: theme, reset, sort, filter)"
            className={cx(
              'w-full bg-transparent text-sm outline-none',
              'text-gray-900 placeholder:text-gray-400',
              'dark:text-gray-100 dark:placeholder:text-gray-500'
            )}
          />
          <div className="hidden items-center gap-2 text-xs text-gray-400 sm:flex">
            <KbdCombo label="↑" /> <KbdCombo label="↓" />{' '}
            <KbdCombo label="Enter" /> <KbdCombo label="Esc" />
          </div>
        </div>

        <div className="max-h-[60vh] overflow-auto p-2">
          {filtered.length === 0 ? (
            <div className="px-3 py-10 text-center text-sm text-gray-600 dark:text-gray-400">
              No commands.
            </div>
          ) : (
            <div className="space-y-2">
              {sections.map((sec) => (
                <div key={sec.title}>
                  <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400">
                    {sec.title}
                  </div>
                  <div className="space-y-1">
                    {sec.items.map((c) => {
                      const index = indexById.get(c.id) ?? -1;
                      const isActive = index === active;

                      return (
                        <button
                          key={c.id}
                          type="button"
                          data-cmd-index={index}
                          onMouseEnter={() => index >= 0 && setActive(index)}
                          onClick={() => {
                            onUseCommand(c.id);
                            c.run();
                            onClose();
                          }}
                          className={cx(
                            'flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm transition',
                            isActive
                              ? 'bg-blue-50 text-blue-900 dark:bg-blue-900/30 dark:text-blue-100'
                              : 'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-900'
                          )}
                        >
                          <span className="flex min-w-0 items-center gap-2">
                            <span className="w-5 text-center text-gray-400 dark:text-gray-500">
                              {c.icon ?? '•'}
                            </span>
                            <span className="truncate">{c.name}</span>
                          </span>
                          {c.shortcut ? (
                            <span className="shrink-0 opacity-80">
                              <KbdCombo label={c.shortcut} />
                            </span>
                          ) : null}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}

              {q.trim().length === 0 && recentIds.length === 0 && (
                <div className="px-3 py-8 text-center text-sm text-gray-600 dark:text-gray-400">
                  Recent is empty. Run some commands!
                </div>
              )}
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 px-4 py-3 text-xs text-gray-500 dark:border-gray-800 dark:text-gray-400">
          Recent is saved to localStorage • ↑↓ to navigate • Enter to run • Esc
          to close
        </div>
      </div>
    </div>
  );
}
